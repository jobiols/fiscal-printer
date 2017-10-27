# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################

from openerp import tools, models, fields, api, _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    nro_ticket_impreso = fields.Char(
            'Nro ticket impreso'
    )


class ProductProduct(models.Model):
    _inherit = 'product.product'

    tax_rate = fields.Float(
            'Tasa IVA',
            compute='_compute_tax_rate'
    )
    lst_price_with_vat = fields.Float(
            'Precio c/IVA',
            compute='_compute_lst_price_with_vat'
    )

    @api.one
    def _compute_lst_price_with_vat(self):
        if self.taxes_id.ids:
            for tax_id in self.taxes_id.ids:
                tax = self.env['account.tax'].browse(tax_id)
                self.lst_price_with_vat = (1 + tax.amount) * self.lst_price

    @api.one
    def _compute_tax_rate(self):
        if self.taxes_id.ids:
            for tax_id in self.taxes_id.ids:
                tax = self.env['account.tax'].browse(tax_id)
                self.tax_rate = tax.amount
