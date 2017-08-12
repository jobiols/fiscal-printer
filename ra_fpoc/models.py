# -*- coding: utf-8 -*-

from openerp import tools, models, fields, api, _
from openerp.osv import osv
from openerp.exceptions import except_orm, ValidationError
from StringIO import StringIO
import urllib2, httplib, urlparse, gzip, requests, json
import openerp.addons.decimal_precision as dp
import logging
import datetime
import time
from openerp.fields import Date as newdate
from datetime import datetime,date,timedelta

class account_invoice(models.Model):
        _inherit = 'account.invoice'

        nro_ticket_impreso = fields.Char('Nro ticket impreso')


class product_product(models.Model):
        _inherit = 'product.product'

        @api.one
        def _compute_lst_price_with_vat(self):
                if self.taxes_id.ids:
                        for tax_id in self.taxes_id.ids:
                                tax = self.env['account.tax'].browse(tax_id)
                                self.lst_price_with_vat = (1+tax.amount) * self.lst_price

        @api.one
        def _compute_tax_rate(self):
                if self.taxes_id.ids:
                        for tax_id in self.taxes_id.ids:
                                tax = self.env['account.tax'].browse(tax_id)
                                self.tax_rate = tax.amount

        tax_rate = fields.Float('Tasa IVA',compute=_compute_tax_rate)
        lst_price_with_vat = fields.Float('Precio c/IVA',compute=_compute_lst_price_with_vat)

