# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import tools, models, fields, api, _


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    use_fiscal_printer = fields.Boolean(
            'Asociado a una impresora fiscal'
    )
    fp_serial_number = fields.Char(
            'Numero de serie de la impresora'
    )
    fp_status = fields.Char(
            'Estado',
            compute='_get_fp_status'
    )

    @api.one
    def _get_fp_status(self):
        if self.use_fiscal_printer:
            self.fp_status = 'Conectado' if self.fiscal_printer_id else 'Desconectado'
        else:
            self.fp_status = ''
