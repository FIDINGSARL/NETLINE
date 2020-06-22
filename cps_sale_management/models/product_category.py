from odoo import models, fields, api

class ProductTemplate(models.Model):
    _name = 'product.category'
    _inherit = 'product.category'

    product_template_id = fields.One2many("cps.product.template", 'type_article_id', string="Produit template")
    product_echantillon_id = fields.One2many("cps.product.echantillon", 'type_article_id', string="Produit echantillon")
