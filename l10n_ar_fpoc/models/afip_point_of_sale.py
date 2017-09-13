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
    def check_document_local_controller_number(self):
        #import wdb;wdb.set_trace()
        raise Warning('No esta implementado')
        return

        #TODO Aca hay que implementar un get_fiscal_printer_last_invoice()

        for j_document_class in self.journal_document_class_ids.filtered(
                lambda r: r.journal_id.type in ['sale', 'sale_refund']):
            next_by_ws = int(
                j_document_class.get_pyafipws_last_invoice()['result']) + 1
            next_by_seq = j_document_class.sequence_id.number_next_actual
            if next_by_ws != next_by_seq:
                msg += _(
                    '* Document Class %s (id %i), Local %i, Remote %i\n' % (
                        j_document_class.afip_document_class_id.name,
                        j_document_class.id,
                        next_by_seq,
                        next_by_ws))
        if msg:
            msg = _('There are some doument desynchronized:\n') + msg
            raise Warning(msg)
        else:
            raise Warning(_('All documents are synchronized'))

