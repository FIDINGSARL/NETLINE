# # -*- coding: utf-8 -*-
from odoo import models, fields, api, tools, _
from odoo.modules import get_module_resource
from odoo.exceptions import UserError, AccessError

class Netline_reception_line(models.Model):
    _name = 'netline.reception.line'

    reception_id = fields.Many2one('netline.reception', 'Réception')
    reception_state = fields.Selection(string="Etat de la réception", selection=[('cancelled', 'Annulé'),
                                                                       ('draft', 'Enlevé'),
                                                                       ('received', 'En préparation'),
                                                                       ('in_progress', 'En production'),
                                                                       ('ready', 'Prêt a livrer'),
                                                                       ('partial_delivred', 'Livré partiellement'),
                                                                       ('delivred', 'Soldé')], store=True)
    categ_name = fields.Char(related="product_id.product_id.categ_id.name")
    product_id = fields.Many2one('netline.product', 'Article Laundry', domain= '[("client_id", "=", parent.client_id)]')
    product_pressing_id = fields.Many2one('netline.pressing_product', 'Article Pressing', domain= '[("client_id", "=", parent.client_id)]')
    product_vt_id = fields.Many2one('netline.vt_product', 'Article V.T.', domain= '[("client_id", "=", parent.client_id)]')

    n_porteur = fields.Char("Numéro porteur")
    traitement = fields.Selection([('lavage', 'Lavage'), ('lavage_sec', 'Lavage a sec'),('detachage', 'Detachage'), ('repassage', 'Repassage'), ('decatissage', 'Décatissage')], default='lavage')
    extra_quantity = fields.Integer(string="Quantite extra")
    livraison_line_ids = fields.One2many('netline.livraison.line', 'reception_line_id')
    purchase_order_line_ids = fields.One2many('purchase.order.line', "reception_line_id")

    quantity = fields.Integer(string="Quantite")
    delivered_quantity = fields.Integer(string="Quantite Livrée")
    quality_quantity = fields.Integer(string="Quantite en réparation")

    available_quantity = fields.Integer('Quantité restante')
    declared_quantity = fields.Integer('Quantité controlée')
    diff_quantity = fields.Integer(compute='_compute_diff_qte', string='Différence')

    n_chambre = fields.Char("N° Chambre")
    nom_porteur = fields.Char("Nom Porteur")

    reception_line_name=fields.Char(readonly=True)

    # n_bon = fields.Char(string="N° Bon")
    # n_bon_client = fields.Char(string="N° Bon Client")
    # date_reception = fields.Datetime(string="Date reception")

    is_controlled=fields.Boolean('Controlée')


    def _compute_diff_qte(self):
        for reception_line in self:
            self.diff_quantity = reception_line.declared_quantity-reception_line.quantity

    # copy_it = fields.Boolean("dup")
    #
    # @api.onchange('copy_it')
    # def copy_line(self):
    #     record_id = self.pool.get('netline.reception.line').search([], order='id desc', limit=1)
    #     print record_id



    def unlink(self):
        if len(self.livraison_line_ids)==0:
            if len(self.purchase_order_line_ids) is 1:
                self.purchase_order_line_ids[0].unlink()
            reception_line= super(Netline_reception_line, self).unlink()
            return reception_line
        else:
            raise UserError(
                _("Vous ne pouvez pas supprimer cette ligne !"))


    @api.model
    def write(self, values):
        #self
        #values
        print('write line')
        for rline in self:
            price = 0
            if 'traitement' in values:
                if rline.product_id.id is not False:
                    price = rline.product_id.get_price(values['traitement'])
                if rline.product_vt_id.id is not False:
                    price = rline.product_vt_id.get_price(values['traitement'])
                if rline.product_pressing_id.id is not False:
                    price = rline.product_pressing_id.get_price(values['traitement'])
                self.purchase_order_line_ids[0].write({'price_unit': price, 'traitement': values['traitement']})
            reception_line = super(Netline_reception_line, self).write(values)

            if 'quantity' in values:
                self.reception_id.define_state()
                self.purchase_order_line_ids[0].write({'product_qty': values['quantity']})
            if ('product_id' in values) or ('product_vt_id' in values) or ('product_pressing_id' in values):
                raise UserError(
                    _("Vous ne pouvez pas modifier un article déja livré !"))
                return
            return rline

    @api.model
    def create(self, values):
        #"creating reception line"
        is_vt = False
        is_laundry = False
        is_pressing = False
        product = None
        if 'product_vt_id' in values and values['product_vt_id'] != False:
            is_vt = True
            #'product_vt_id'
            product = self.env['netline.vt_product'].search([('id', '=', values.get('product_vt_id'))])
        if 'product_id' in values and values['product_id'] != False:
            is_laundry = True
            product = self.env['netline.product'].search([('id', '=', values.get('product_id'))])
        if 'product_pressing_id' in values and values['product_pressing_id'] != False:
            is_pressing = True
            product = self.env['netline.pressing_product'].search([('id', '=', values.get('product_pressing_id'))])
        #product

        if product is not None:
            price = product.get_price(values['traitement'])
            reception = self.env['netline.reception'].search([('id', '=', values.get('reception_id'))])
            reception_line = super(Netline_reception_line, self).create(values)
            purchase_order_line = {
                    'product_uom': 1,
                    'product_qty': values.get('quantity'),
                    'product_id': product.product_id.id,
                    'name': product.name,
                    'price_unit': price,
                    'order_id': reception.purchase_order_id.id,
                    'reception_line_id': reception_line.id,
                    'date_planned': reception.date_reception,
                    'is_netline':True
                }
            pol = self.env['purchase.order.line'].create(purchase_order_line)
            return reception_line
        # else:
        #     return True

    @api.onchange('quantity')
    def onchange_to_receive_quantity(self):
        #self._origin.id
        if self._origin.id is not False:
            if self.quantity < self.delivered_quantity:
                return {
                    'warning': {
                        'title': "Message d'erreur",
                        'message': "La quantité que vous avez saisi est inférieure à l'encours actuel !",
                    }
                }
        if self.declared_quantity==0:
            self.declared_quantity=self.quantity
        self.diff_quantity=self.declared_quantity-self.quantity

    @api.onchange('declared_quantity')
    def onchange_declared_quantity(self):
        if self.quantity==0:
            self.quantity=self.declared_quantity
        self.diff_quantity = self.declared_quantity - self.quantity


    # def name_get(self):
    #     res = []
    #     designation_client, designation, type, couleur
        # for rec in self:
        #     name = rec.get_name()
        #     res.append((rec.id, name))
        # return res

    # def get_name(self):
    #     for p in self:
    #         name = ""
            # if p.product_textil_id.name is not False:
            #     name = name + p.product_textil_id.name
            # if p.product_echantillon_id.name is not False:
            #     name = name + p.product_echantillon_id.name
            #print name
            # p.name= name

class Pressing_Product_Selection_Helper(models.Model):
    _name="netline.pressing_product_selection_helper"

    product_pressing_id = fields.Many2one('netline.pressing_product', 'Article Laundry', domain='[("client_id", "=", parent.client_id)]')
    traitement = fields.Selection([('lavage', 'Lavage'), ('lavage_sec', 'Lavage a sec'),('detachage', 'Detachage'), ('repassage', 'Repassage'), ('decatissage', 'Décatissage')], default='lavage')
    quantity = fields.Integer("Quantité")
    # reception_id = fields.Many2one("netline.reception", "products")
