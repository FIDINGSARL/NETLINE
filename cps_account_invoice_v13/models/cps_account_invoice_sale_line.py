# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError

########Cps facturation lines ###########
class AccountInvoiceSaleLine(models.Model):
    _name = 'account.invoice.sale.line'
    _description = 'Lignes de facture'

    #_order = 'product_laundry_id asc, product_pressing_id asc, product_vt_id asc, product_textil_id asc, product_echantillon_id asc'
    sequence = fields.Integer('Sequence')
    name = fields.Char('Nom')
    sale_line_id = fields.Many2one('sale.order.line', 'Ligne de facture', domain= '[("order_partner_id", "=", parent.client_id)]')
    traitement = fields.Char("Traitement",compute="compute_traitement")
    facturation_id = fields.Many2one('account.invoice.sale', string="Facture")
    quantity_livre = fields.Integer("Quantité livrée", compute="_compute_quantites")
    quantity_facture = fields.Integer("Quantité facturée", readonly="True")
    reste_a_facturer = fields.Integer("Reste à facturer", readonly="True")
    qty_to_invoice = fields.Integer("Quantité à facturer")
    montant_ht = fields.Float("Montant HT", compute="compute_montant_ht")
    montant_tva = fields.Float("Montant TVA")
    montant_ttc = fields.Float("Montant TTC")
    account_move_line_ids = fields.One2many('account.move.line', 'facturation_line_id', string='Lignes de facture')

    product_id = fields.Many2one('product.product', string="Article")
    product_description = fields.Char(string="Déscription")
    product_name = fields.Char(related='product_id.name', string="Désignation")
    price = fields.Float("Prix")


    def compute_traitement(self):
        for s in self:
            p = self.env['cps.product.template'].search([("product_id", "=", s.product_id.id)])
            s.traitement = p[0].traitement_name



    @api.onchange('qty_to_invoice', 'price')
    def compute_montant_ht(self):
        for s in self:
            s.montant_ht = s.qty_to_invoice * s.price

    def action_view_es(self):
        pps= self.env['cps.product.template'].search([("product_id", "=", self.product_id.id)])
        return {
            'name': 'Liste des flux',
            'res_model': 'cps.flux',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': pps[0].flux_id.id,
            'type': 'ir.actions.act_window',
            'target': 'current'  # will open a popup with mail.message list
        }


    # filtrer les articles commandé par le client selectionné
    @api.onchange('product_id')
    def change_product(self):
        sols = self.env['sale.order.line'].search([("order_partner_id", "=", self.facturation_id.client_id.name), ('qty_to_invoice','>',0)])
        ids = []
        for sol in sols:
            ids.append(sol.product_id.id)
        return {'domain': {'product_id': [('id', 'in', ids)]}}

    @api.depends('price','qty_to_invoice')
    def _compute_quantites(self):
        for s in self:
            if s.price==0:
                s.price= s.product_id.list_price
            if s.facturation_id.prestation_type=='textil':
                sols = self.env['sale.order.line'].search([("product_id", "=", s.product_id.id), ("order_partner_id", "=", self.facturation_id.client_id[0].name)])
            else:
                sols = s.sale_line_id
            print('sols-------------------------------', sols)
            qty_livre = 0
            quantity_invoiced=0
            reste_a_facturer=0
            for sol in sols:
                print('sol qty-----------------------------', sol.qty_delivered)
                quantity_invoiced+= sol.qty_invoiced
                qty_livre += sol.product_uom_qty
                reste_a_facturer += qty_livre-quantity_invoiced
            s.quantity_livre = qty_livre
            s.quantity_facture=quantity_invoiced
            s.reste_a_facturer=reste_a_facturer
            s.montant_ht = s.qty_to_invoice*s.price
            # print('compute qty')

    @api.model
    def default_get(self, fields):
        res = super(AccountInvoiceSaleLine, self).default_get(fields)

        last_rec = self.search([], order='id desc')

        # if last_rec:
        #     res.update({'your_field_name': last_rec.field_value})
        return res

    @api.model
    def create(self, values):
        product_template = self.env['cps.product.template'].search([("product_id", "=", self.product_id.id)])
        if 'price' in values:
            product_template.price = values['price']

        # same_line = self.search([('product_id', '=', values.get('product_id', False)), ('facturation_id', '=', values.get('facturation_id', False))])
        # if same_line:
        #         raise UserError(_("Il existe des commandes en double dans la facture !"))
        # else:
        return super(AccountInvoiceSaleLine, self).create(values)

    @api.model
    def unlink(self):
        # self.account_move_line_ids.unlink()
        return super(AccountInvoiceSaleLine, self).unlink()

    @api.model
    def write(self, values):
        invoice_line = super(AccountInvoiceSaleLine, self).write(values)
        if 'price' in values:
            product_template = self.env['cps.product.template'].search([("product_id", "=", self.product_id.id)])
            product_template.price = values['price']

        return invoice_line
