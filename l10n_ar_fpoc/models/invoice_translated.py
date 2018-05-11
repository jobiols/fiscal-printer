# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################

from openerp import tools, models, fields, api, _
from openerp.exceptions import Warning


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    nro_ticket_impreso = fields.Char(
        'Nro ticket impreso'
    )

    no_fiscal_printer = fields.Boolean(
        default=False
    )

    @api.multi
    def action_number(self):
        """ sobreescribir action_number para chequear las secuencias antes
            de mandar a imprimir el ticket
        """
        self.ensure_one()
        for inv in self:
            if inv.validation_type == 'fiscal_controller':
                res = inv.journal_id.fiscal_printer_id.get_counters()
                sequences = res[inv.journal_id.fiscal_printer_id.id]

                if sequences.get('strResult') == u'Resultado exitoso':
                    self.check_counters(sequences)
                else:
                    raise Warning('Reintente mas tarde')

        super(AccountInvoice, self).action_number()

    @api.multi
    def check_counters(self, sequences):
        """ Verificar que las secuencias son correctas o generar una excepcion
        """
        a_invoice = sequences['last_a_sale_document']
        a_refund = sequences['last_a_credit_document']
        b_invoice = sequences['last_b_sale_document']
        b_refund = sequences['last_b_credit_document']

        for inv in self:
            if inv.type == 'out_invoice':
                if inv.journal_document_class_id.afip_document_class_id.document_letter_id.name == 'A':  # noqa
                    next_number = int(a_invoice) + 1
                if inv.journal_document_class_id.afip_document_class_id.document_letter_id.name == 'B':  # noqa
                    next_number = int(b_invoice) + 1
            if inv.type == 'out_refund':
                if inv.journal_document_class_id.afip_document_class_id.document_letter_id.name == 'A':  # noqa
                    next_number = int(a_refund) + 1
                if inv.journal_document_class_id.afip_document_class_id.document_letter_id.name == 'B':  # noqa
                    next_number = int(b_refund) + 1

            if next_number != inv.next_invoice_number:
                raise Warning(u'Error de secuencia!',
                              u'Proximo numero Odoo {} - '
                              u'Proximo numero Controlador Fiscal {}'.format(
                                  inv.next_invoice_number, next_number)
                              )

    def get_validation_type(self):
        """ detectar cuando el journal esta asociado a una impresora fiscal
            para poner luego el boton correcto
        """
        super(AccountInvoice, self).get_validation_type()

        for inv in self:
            if not inv.validation_type and inv.journal_id.fiscal_printer_id:
                inv.validation_type = 'fiscal_controller'
