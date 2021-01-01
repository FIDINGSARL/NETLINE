# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions

class Netline_compteur_template(models.Model):
    _name = 'netline.compter'
    _description = 'Gestion des compteurs'

    product_cpt_id = fields.Many2one('product.product', 'Netline Compteur', domain='[("is_compteur", "=", True)]')
    product_name = fields.Char("Nom Compteur")
    product_price = fields.Float("Prix compteur")
    product_unit_id = fields.Many2one('uom.uom', 'Unité')
    product_type = fields.Selection([('incrementiel', 'Incrementiel'), ('decrementiel', 'Decrementiel')], string='Type Compteur', required=True, default='incrementiel')
    is_compteur = fields.Boolean("compteur", default=True)
    # consomation_line_ids = fields.One2many('netline.consomation', 'product_id', string="Produits")
    compteur_principale = fields.Boolean("Compteur principal", default=True)

    @api.model
    def create(self, values):
        netline_compter = self.env['netline.compter'].search([('product_name', 'ilike', values.get('product_name'))])
        if len(netline_compter) == 0 :
            pProduct = self.env['product.product'].create({
                    'name': values.get('product_name'),
                    'uom_po_id':values.get('product_unit_id'),
                    'uom_id':values.get('product_unit_id'),
                    'type':'service',
                    'standard_price':values.get('product_price')
                })
            values['product_cpt_id'] = pProduct.id
            Product = super(Netline_compteur_template, self).create(values)
            return Product
        else:
            raise exceptions.ValidationError("Ce compteur existe déjà !")


    def write(self, values):
        Product = super(Netline_compteur_template, self).write(values)
        netline_compter = self.env['product.product'].search([('id', '=', self.product_cpt_id.id)])
        #"name", self.product_name
        #'uom_po_id',self.product_unit_id.id
        #'standard_price',self.product_price

        netline_compter.write({'name': self.product_name,
                'uom_po_id':self.product_unit_id.id,
                'uom_id':self.product_unit_id.id,
                'type':'service',
                'standard_price':self.product_price}
                )
        #"written"
        return Product


    def unlink(self):
        netline_compter = self.env['product.product'].search([('id', '=', self.product_cpt_id.id)]).unlink()
        Product = super(Netline_compteur_template, self).unlink()
        return Product

    def get_name(self):
        name = ""
        name = self.product_name
        return name
    

    def name_get(self):

        #"gettin compter name"
        res = []
        name = ""
        for rec in self:
            if rec.product_name is not False:
                name=rec.product_name
            else:
                name = "unamed"
            res.append((rec.id, name))
        return res
