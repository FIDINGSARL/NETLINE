from odoo import models, fields, api, _


class AccountMoveLine(models.Model):
    _name = 'account.move.line'
    _inherit = 'account.move.line'

    facturation_line_id = fields.Many2one('account.invoice.sale.line', string="Lignes assistant facture")

    debit_in_words = fields.Char(string="Debit in Words", compute="_onchange_debit")

   # @api.onchange('debit')
    @api.depends('move_id', 'debit')
    def _onchange_debit(self):
        for s in self:
        #res = super(AccountMoveLine, self)._onchange_debit()
            s.debit_in_words = s.move_id.currency_id.amount_to_text(s.debit) if s.move_id.currency_id else ''
        #return res