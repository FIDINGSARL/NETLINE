from odoo import models, fields, api

class ProductTemplate(models.Model):
    _name = 'product.product'
    _inherit = 'product.product'

    reception_helper_ids = fields.One2many("cps.reception.helper", 'product_id', string="Produit reception")
    template_ids = fields.One2many("cps.product.template", 'product_id', string="Produit template")
    echantillon_ids = fields.One2many("cps.product.echantillon", 'product_id', string="Produit echantillon")
    production_ids = fields.One2many("cps.product.production", 'product_id', string="Produit production")
