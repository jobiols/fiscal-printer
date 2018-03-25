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

        # chequear las impresoras vivas
        data = do_event('list_printers', control=True)

        # si viene sin datos es porque fpoc no esta logeado, eliminar todos
        if not data:
            _logger.error('FPOC is not logged')
            self.search([]).unlink()
            return

        # estos son los datos de los printers vivos, en una lista
        printers = data[0].get('printers')

        # lista con los nombres de las impresores que responden (vivas)
        live_printers = []
        for l_printer in printers:
            live_printers.append(l_printer.get('name'))

        # lista con los impresores registrados
        registered_printers = []
        for r_printer in self.search([]):
            registered_printers.append(r_printer.name)

        # vemos cuales printers hay que agregar y cuales hay que quitar
        to_unlink = set(registered_printers) - set(live_printers)
        to_append = set(live_printers) - set(registered_printers)

        for printer_name in to_unlink:
            _logger.info('Remove FISCAL PRINTER {}'.format(printer_name))
            self.search([('name', '=', printer_name)]).unlink()

        for printer_name in to_append:
            _logger.info('Add FISCAL PRINTER {}'.format(printer_name))
            # search printer name in printers
            for printer in printers:
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

