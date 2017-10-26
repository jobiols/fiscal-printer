# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import tools, models, fields, api, _
from openerp.exceptions import Warning


class AfipPointOfSale(models.Model):
    _inherit = 'afip.point_of_sale'

    @api.multi
    def sync_document_local_remote_number(self):
        res = self.journal_ids[0].fiscal_printer_id.get_counters()
        if not res:
            raise Warning('No hay impresoras conectadas')

        sequences = res[self.journal_ids[0].fiscal_printer_id.id]
        if not sequences:
            raise Warning('No hay impresoras conectadas')

        try:
            FA = int(sequences['last_a_sale_document'])
            NA = int(sequences['last_a_credit_document'])
            FB = int(sequences['last_b_sale_document'])
            NB = int(sequences['last_b_credit_document'])
        except:
            raise osv.except_osv(u'Error de conexión con el controlador fiscal',
                                 u'Verifique que el controlador esté online y conectado')

        for j_document_class in self.journal_document_class_ids.filtered(
                lambda r: r.journal_id.type in ['sale', 'sale_refund']):

            if j_document_class.afip_document_class_id.name == 'FACTURAS A':
                j_document_class.sequence_id.number_next_actual = FA + 1

            if j_document_class.afip_document_class_id.name == 'FACTURAS B':
                j_document_class.sequence_id.number_next_actual = FB + 1

            if j_document_class.afip_document_class_id.name == 'NOTAS DE CREDITO A':
                j_document_class.sequence_id.number_next_actual = NA + 1

            if j_document_class.afip_document_class_id.name == 'NOTAS DE CREDITO B':
                j_document_class.sequence_id.number_next_actual = NB + 1

    @api.multi
    def check_document_local_controller_number(self):

        res = self.journal_ids[0].fiscal_printer_id.get_counters()
        if not res:
            raise Warning('No hay impresoras conectadas')

        sequences = res[self.journal_ids[0].fiscal_printer_id.id]
        if not sequences:
            raise Warning('No hay impresoras conectadas')

        msg = ''
        for j_document_class in self.journal_document_class_ids.filtered(
                lambda r: r.journal_id.type in ['sale', 'sale_refund']):

            if j_document_class.afip_document_class_id.name == 'FACTURAS A':
                next_by_seq = j_document_class.sequence_id.number_next_actual
                next_by_controller = int(sequences['last_a_sale_document']) + 1
                if next_by_controller != next_by_seq:
                    msg += 'Documento {} (id {}), Odoo {}, Controlador {}\n'.format(
                        j_document_class.afip_document_class_id.name,
                        j_document_class.id,
                        next_by_seq,
                        next_by_controller
                    )

            if j_document_class.afip_document_class_id.name == 'FACTURAS B':
                next_by_seq = j_document_class.sequence_id.number_next_actual
                next_by_controller = int(sequences['last_b_sale_document']) + 1
                if next_by_controller != next_by_seq:
                    msg += 'Documento {} (id {}), Odoo {}, Controlador {}\n'.format(
                        j_document_class.afip_document_class_id.name,
                        j_document_class.id,
                        next_by_seq,
                        next_by_controller
                    )

            if j_document_class.afip_document_class_id.name == 'NOTAS DE CREDITO A':
                next_by_seq = j_document_class.sequence_id.number_next_actual
                next_by_controller = int(sequences['last_a_credit_document']) + 1
                if next_by_controller != next_by_seq:
                    msg += 'Documento {} (id {}), Odoo {}, Controlador {}\n'.format(
                        j_document_class.afip_document_class_id.name,
                        j_document_class.id,
                        next_by_seq,
                        next_by_controller
                    )

            if j_document_class.afip_document_class_id.name == 'NOTAS DE CREDITO B':
                next_by_seq = j_document_class.sequence_id.number_next_actual
                next_by_controller = int(sequences['last_b_credit_document']) + 1
                if next_by_controller != next_by_seq:
                    msg += 'Documento {} (id {}), Odoo {}, Controlador {}\n'.format(
                        j_document_class.afip_document_class_id.name,
                        j_document_class.id,
                        next_by_seq,
                        next_by_controller
                    )
        if msg:
            msg = _('There are some doument desynchronized:\n') + msg
            raise Warning(msg)
        else:
            raise Warning(_('All documents are synchronized'))
