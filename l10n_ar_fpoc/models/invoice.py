# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp.osv import osv, fields
from openerp.tools.translate import _

_vat = lambda x: x.tax_code_id.parent_id.name == 'IVA'

document_type_map = {
    "DNI":      "D",
    "CUIL":     "L",
    "CUIT":     "T",
    "CPF":      "C",
    "CIB":      "C",
    "CIK":      "C",
    "CIX":      "C",
    "CIW":      "C",
    "CIE":      "C",
    "CIY":      "C",
    "CIM":      "C",
    "CIF":      "C",
    "CIA":      "C",
    "CIJ":      "C",
    "CID":      "C",
    "CIS":      "C",
    "CIG":      "C",
    "CIT":      "C",
    "CIH":      "C",
    "CIU":      "C",
    "CIP":      "C",
    "CIN":      "C",
    "CIQ":      "C",
    "CIL":      "C",
    "CIR":      "C",
    "CIZ":      "C",
    "CIV":      "C",
    "PASS":     "P",
    "LC":       "V",
    "LE":       "E",
}

responsability_map = {
    "IVARI":    "I",  # Inscripto,
    "IVARNI":   "N",  # No responsable,
    "RM":       "M",  # Monotributista,
    "IVAE":     "E",  # Exento,
    "NC":       "U",  # No categorizado,
    "CF":       "F",  # Consumidor final,
    "RMS":      "T",  # Monotributista social,
    "RMTIP":    "P",  # Monotributista trabajador independiente promovido.
    "1":        "I",  # Inscripto,
    "2":        "N",  # No responsable,
    "6":        "M",  # Monotributista,
    "4":        "E",  # Exento,
    "7":        "U",  # No categorizado,
    "5":        "F",  # Consumidor final,
    "13":       "T",  # Monotributista social,
}


class Invoice(osv.osv):

    _name = 'account.invoice'
    _inherits = {  }
    _inherit = ['account.invoice']

    def check_counters(self, cr, uid, ids, sequences, context=None):
        """ Verificar que las secuencias son correctas o generar una excepcion
        """
        # import wdb;wdb.set_trace()
        FA = sequences['last_a_sale_document']
        NA = sequences['last_a_credit_document']
        FB = sequences['last_b_sale_document']
        NB = sequences['last_b_credit_document']

        for inv in self.browse(cr, uid, ids, context):
            if inv.type == 'out_invoice':
                if inv.journal_document_class_id.afip_document_class_id.document_letter_id.name == 'A':
                    next_number = int(FA) + 1
                if inv.journal_document_class_id.afip_document_class_id.document_letter_id.name == 'B':
                    next_number = int(FB) + 1
            if inv.type == 'out_refund':
                if inv.journal_document_class_id.afip_document_class_id.document_letter_id.name == 'A':
                    next_number = int(NA) + 1
                if inv.journal_document_class_id.afip_document_class_id.document_letter_id.name == 'B':
                    next_number = int(NB) + 1

            if next_number != inv.next_invoice_number:
                raise osv.except_osv(u'Error de secuencia',
                                     'Proximo numero Odoo {} - Proximo numero Controlador Fiscal {}'.format(
                                         inv.next_invoice_number,
                                         next_number)
                                     )

    def action_number(self, cr, uid, ids, context=None):
        """ sobreescribir action_number para chequear las secuencias antes de mandar a imprimir el ticket
        """
        for inv in self.browse(cr, uid, ids, context):
            if inv.validation_type == 'fiscal_controller':
                res = inv.journal_id.fiscal_printer_id.get_counters()
                sequences = res[inv.journal_id.fiscal_printer_id.id]
                self.check_counters(cr, uid, ids, sequences, context)

        super(Invoice, self).action_number(cr, uid, ids, context)

    def get_validation_type(self, cr, uid, ids, context=None):
        """ detectar cuando el journal esta asociado a una impresora fiscal para poner luego el boton correcto
        """
        super(Invoice, self).get_validation_type(cr, uid, ids, context)

        for inv in self.browse(cr, uid, ids, context):
            if not inv.validation_type and inv.journal_id.fiscal_printer_id:
                inv.validation_type = 'fiscal_controller'

    def action_fiscal_printer(self, cr, uid, ids, context=None):
        picking_obj = self.pool.get('stock.picking')
        user_obj = self.pool.get('res.users')

        r = {}
        if len(ids) > 1:
            raise osv.except_osv(_(u'Cancelling Validation'),
                                 _(u'Please, validate one ticket at time.'))
            return False

        for inv in self.browse(cr, uid, ids, context):
            if inv.journal_id.use_fiscal_printer:
                if inv.amount_total > 999 and inv.partner_id.id == inv.journal_id.fiscal_printer_anon_partner_id.id:
                    raise osv.except_osv(_(u'Cancelling Validation'),
                             _(u'No se pueden emitir tickets superiores a $1,000 a Consumidor Final.'))
                journal = inv.journal_id
                ticket = {
                    "turist_ticket": False,
                    "debit_note": False,
                    "partner": {
                        "name": inv.partner_id.name,
                        "name_2": "",
                        "address": inv.partner_id.street,
                        "address_2": inv.partner_id.city,
                        "address_3": inv.partner_id.country_id.name,
                        "document_type": document_type_map.get(inv.partner_id.document_type_id.code, "D"),
                        "document_number": inv.partner_id.document_number,
                        "responsability": responsability_map.get(inv.partner_id.responsability_id.code, "F"),
                    },
                    #"related_document": (picking_obj.search_read(cr, uid, [('origin','=',inv.origin or '')], ["name"]) +
                    #                    [{'name': _("No picking")}])[0]['name'],
                    "related_document_2": inv.origin or "",
                    "turist_check": "",
                    "lines": [ ],
                    "cut_paper": True,
                    "electronic_answer": False,
                    "print_return_attribute": False,
                    "current_account_automatic_pay": False,
                    "print_quantities": True,
                    "tail_no": 1 if inv.user_id.name else 0,
                    "tail_text": _("Saleman: %s") % inv.user_id.name if inv.user_id.name else "",
                    "tail_no_2": 0,
                    "tail_text_2": "",
                    "tail_no_3": 0,
                    "tail_text_3": "",
                }
                if picking_obj:
                    ticket['related_document'] = \
                        (picking_obj.search_read(cr, uid, [('origin', '=', inv.origin or '')],
                                                 ["name"]) + [{'name': _("No picking")}])[0]['name']
                else:    
                    ticket['related_document'] = 'N/A'
                if inv.origin:
                    ticket['origin_document'] = inv.origin
                for line in inv.invoice_line:
                    ticket["lines"].append({
                        "item_action": "sale_item",
                        "as_gross": False,
                        "send_subtotal": True,
                        "check_item": False,
                        "collect_type": "q",
                        "large_label": "",
                        "first_line_label": "",
                        "description": "",
                        "description_2": "",
                        "description_3": "",
                        "description_4": "",
                        "item_description": line.name,
                        "quantity": line.quantity,
                        "unit_price": line.price_unit,
                        "vat_rate": line.product_id.tax_rate * 100,
                        "fixed_taxes": 0,
                        "taxes_rate": 0
                    })
                    if line.discount > 0: ticket["lines"].append({
                        "item_action": "discount_item",
                        "as_gross": False,
                        "send_subtotal": True,
                        "check_item": False,
                        "collect_type": "q",
                        "large_label": "",
                        "first_line_label": "",
                        "description": "",
                        "description_2": "",
                        "description_3": "",
                        "description_4": "",
                        "item_description": "%5.2f%%" % line.discount,
                        "quantity": line.quantity,
                        "unit_price": line.price_unit * (line.discount/100.),
                        "vat_rate": line.product_id.tax_rate,
                        "fixed_taxes": 0,
                        "taxes_rate": 0
                    })

                #import pdb;pdb.set_trace()
                if inv.type == 'out_invoice':	
                    r = journal.make_fiscal_ticket(ticket)[inv.journal_id.id]
                if inv.type == 'out_refund':
                    if 'payments' not in ticket.keys():
                        ticket['payments'] = [{
                                'extra_description': '',
                                'amount': inv.amount_total,
                                'type': 'pay',
                                'description': 'Cuenta corriente del cliente'
                                }]
                    if not ticket['debit_note']:
                        ticket['debit_note'] = ''
                    if not ticket['turist_ticket']:
                        ticket['turist_ticket'] = ''
                    if not ticket['current_account_automatic_pay']:
                        ticket['current_accountautomatic_pay'] = ''
                    r = journal.make_fiscal_refund_ticket(ticket)[inv.journal_id.id]

        if r and 'error' not in r:
            #  import wdb; wdb.set_trace()
            if 'document_number' in r:
                nro_impreso = '{:0>4}-{:0>8}'.format(
                        inv.journal_id.point_of_sale,
                        r['document_number'])
                vals = {
                        'nro_ticket_impreso': nro_impreso
                       }
                self.pool.get('account.invoice').write(cr, uid, inv.id, vals)
            return True

        elif r and 'error' in r:
            #import wdb;wdb.set_trace()
            raise osv.except_osv(_(u'Cancelling Validation'),
                                 _('Error: %s') % r['error'])
        else:
            if inv.journal_id.use_fiscal_printer:
                raise osv.except_osv(_(u'Cancelling Validation'),
                                     _(u'Unknown error.'))
            else:
                return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
