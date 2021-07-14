# # -*- coding: utf-8 -*-
from unittest.case import _AssertRaisesContext

from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError, AccessError


import datetime
class Netline_purchase_da(models.Model):
    _name = "netline.purchase.da"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    #client
    # name = fields.Char("name", compute="compute_name", store=True)
    employee_id = fields.Many2one('hr.employee', "Demandeur")
    state = fields.Selection(string="Etat de la réception", selection=[('cancelled', 'Annulé'),
                                                                       ('ready', 'A valider'),
                                                                       ('done_partial', 'Validé partiellement'),
                                                                       ('done', 'Validé')], default='ready')

    date_da = fields.Datetime("Date", required=True)
    purchase_da_lines_ids = fields.One2many('netline.purchase.da.line', "purchase_da_id", string="Produits")
    # total_bc = fields.Integer(compute="_compute_total_achats", string="Bons de commande", store=True)
    # 
    # def _compute_total_achats(self):
    #     for p in self:
    #         total_bc = 0
    #         for s in p.purchase_da_lines_ids:
    #             total_bc += p.purchase_da_lines_ids
    # 
    #         p.total_bc = p.total_entree-p.total_sortie-p.total_retour+p.total_retour_correction

    def define_state(self):
        partial=False
        for line in self.purchase_da_lines_ids:
            if line.fournisseur_id.id==0:
                partial=True
        if partial:
            self.state="done_partial"
        else:
            self.state="done"

    # @api.multi
    # def compute_name(self):
    #     recs = []
    #     print "compute_name"
    #     for p in self:
    #         name = "DA"
    #         print "name"
    #         if p.id is not False:
    #             name = name + p.id
    #         print "name"
    #         p.name = name

    def action_cancel(self):
        invoice_obj = self.env['purchase.order']
        i_line_obj = self.env['purchase.order.line']
        order_lines = []

        for line in self.purchase_da_lines_ids:
            if line.fournisseur_id.id>0 and line.quantity>0 and line.is_bc_created==False:
                fournisseur_en_cours = line.fournisseur_id.id
                pOrder = self.env['purchase.order'].create({
                    'picking_type_id': 1,
                    'company_id': self.env.user.company_id.id,
                    'partner_id': line.fournisseur_id.id,
                    'date_order': datetime.datetime.now(),
                    'date_planned': datetime.datetime.now(),
                    'currency_id': line.fournisseur_id.property_purchase_currency_id.id,
                })
                for line_bc in self.purchase_da_lines_ids:
                    if line_bc.fournisseur_id.id== fournisseur_en_cours:
                        supplierPrice = self.env['product.supplierinfo'].search([('name', '=', line_bc.fournisseur_id.name), ('product_tmpl_id', '=', line_bc.product_id.product_tmpl_id.id)]).price
                        purchase_order_line = {
                            'product_uom': line_bc.product_id.uom_id.id,
                            'product_qty': line_bc.quantity,
                            'product_id': line_bc.product_id.id,
                            'name': line_bc.product_id.name,
                            'price_unit':supplierPrice,
                            'order_id': pOrder.id,
                            'date_planned': datetime.datetime.now(),
                            'taxes_id': [(6, 0, line_bc.product_id.supplier_taxes_id.ids)],
                        }
                        pol = self.env['purchase.order.line'].create(purchase_order_line)
                        line_bc.purchase_order_id = pOrder
                        line_bc.purchase_order_line_id=pol
                        line_bc.is_bc_created = True
                        print ("pOrder line ", pol)
        self.define_state()
    def action_view_bc(self):
        bcs = self.env['purchase.order'].search([("id", "in", self.purchase_da_lines_ids.purchase_order_id.ids)])
        # flux = self.purchase_da_lines_ids.purchase_order_id.ids
        return {
            'name': 'Liste des bons de commande',
            'res_model': 'purchase.order',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', bcs.ids)],
            'type': 'ir.actions.act_window',
            'target': 'current'  # will open a popup with mail.message list
        }

    # @api.model
    # def create(self, values):
    #     pOrder = self.env['purchase.order'].create({
    #         'picking_type_id': 2,
    #         'company_id': self.env.user.company_id.id,
    #         'partner_id': values['client_id'],
    #         'date_order': values['date_reception'],
    #         'date_planned': values['date_reception'],
    #         'currency_id': self.env.user.company_id.currency_id.id,
    #         'is_netline': True
    #     })
    #     #create purchase order with the informations given
    #     values['purchase_order_id'] = pOrder.id
    #     #delete reception lines with quantity = 0
    #     if values['receptionline_ids'] is not False:
    #         new_receptionline_ids = []
    #         for purchase_da_line in values['purchase_da_lines_ids']:
    #             if purchase_da_line[2].get('quantity') != 0:
    #                 new_receptionline_ids.append(purchase_da_line)
    #         values['purchase_da_lines_ids'] = new_receptionline_ids
    #     reception = super(Netline_purchase_da, self).create(values)
    #
    #     return reception

class Netline_purchase_da_line(models.Model):
    _name = "netline.purchase.da.line"

    purchase_da_id = fields.Many2one('netline.purchase.da', 'Demande achat')
    product_id = fields.Many2one('product.product', 'Article Laundry', domain='[("is_compteur", "=", False)]', required=True)
    quantity = fields.Integer(string="Quantité a demander")
    fournisseur_id = fields.Many2one('res.partner', "Fournisseur", domain=[('supplier_rank', '!=', 0),('is_company', '=', True)])
    is_bc_created =fields.Boolean('Commande crée')
    purchase_order_id = fields.One2many('purchase.order', "purchase_order_id", string="Commande")
    purchase_order_line_id = fields.One2many('purchase.order.line', "purchase_order_line_id", string="Ligne commande")
    purchase_orders_name = fields.Char(compute='compute_order_name', string="BC")

    def compute_order_name(self):
        partial=False
        # if self.purchase_order_id is not False:
        #     print "self.purchase_order_id ", self.purchase_order_id
        self.purchase_orders_name = "test"
    
class Netline_requisition(models.Model):
    _inherit = 'purchase.requisition'
    is_laundry = fields.Boolean(default=True)
    typeprestation_ids = fields.Many2one('netline.prestation_client', string="Prestation")
    affaire_ids = fields.Many2one('netline.affaire', string="Affaire")


