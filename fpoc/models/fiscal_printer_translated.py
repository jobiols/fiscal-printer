# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from openerp import tools, models, fields, api, _
from ..controllers.main import do_event
import logging

_logger = logging.getLogger(__name__)


class FpocFiscalPrinter(models.Model):
    _inherit = 'fpoc.fiscal_printer'

    @api.model
    def update_printers(self):
        """ check alive printers, add o delete fiscal printers accordingly
        """
        #import wdb;wdb.set_trace()
        # chequear las impresoras vivas
        data = do_event('list_printers', control=True)

        # si viene sin datos es porque fpoc no esta logeado, eliminar todos
        if not data:
            _logger.error('No FPOC logged.')
            self.search([]).unlink()
            return

        # Data trae los datos de los printers vivos, en una lista con las
        # conexiones activas y dentro de cada conexion otra lista con los
        # printers
        active_printer_names = []  # nombre de todos los printers activos
        active_printers = []  # todos los printers activos

        # reviso todas las conexiones que hay en data
        for connection in data:
            active_printers += connection.get('printers')

        # obtengo lista de los nombres de las impresoras activas
        for printer in active_printers:
            _logger.info('Live printer {}'.format(printer.get('name')))
            active_printer_names.append(printer.get('name'))

        # lista con los impresores registrados
        registered_printer_names = []
        for printer in self.search([]):
            registered_printer_names.append(printer.name)

        # vemos cuales printers hay que agregar y cuales hay que quitar
        to_unlink = set(registered_printer_names) - set(active_printer_names)
        to_append = set(active_printer_names) - set(registered_printer_names)

        for printer_name in to_unlink:
            _logger.info('Remove FISCAL PRINTER -- {}'.format(printer_name))
            self.search([('name', '=', printer_name)]).unlink()

        for printer_name in to_append:
            _logger.info('Add FISCAL PRINTER -- {}'.format(printer_name))
            # search printer name in printers
            for printer in active_printers:
                if printer.get('name') == printer_name:
                    self.add_printer(printer)

    @api.model
    def add_printer(self, printer):

        # A veces aparece sin el serial y no se attacha a ningun PV
        # para que no pasa, si no tengo el serial no lo pongo
        if not printer.get('serialNumber'):
            return

        values = {
            'name': printer.get('name'),
            'protocol': printer.get('protocol'),
            'model': printer.get('model'),
            'serialNumber': printer.get('serialNumber'),
            'session_id': printer.get('sid'),
        }
        fp_id = self.create(values)
        # attach this printer to the correct journal
        journal_obj = self.env['account.journal']
        journals = journal_obj.search(
            [('fp_serial_number', '=', values.get('serialNumber'))])
        for journal in journals:
            journal.fiscal_printer_id = fp_id

