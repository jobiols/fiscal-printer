# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import tools, models, fields, api, _


class EpsonArFiscalPrinter(models.Model):
    _inherit = 'fpoc.fiscal_printer'

    point_of_sale = fields.Char(
        'Punto de venta',
        compute='_get_point_of_sale'
    )

    @api.one
    def _get_point_of_sale(self):
        pos = 'unknown'
        journal_obj = self.env['account.journal']
        for journal in journal_obj.search(
            [('fp_serial_number', '=', self.serialNumber)]):
            pos = journal.point_of_sale_id.name

        self.point_of_sale = pos
