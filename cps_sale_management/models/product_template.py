from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_echantillon = fields.Boolean("Est un échantillon", default=False)
    is_commande = fields.Boolean("Est une commande", default=False)
    reception_helper_ids = fields.One2many("cps.reception.helper", 'product_id', string="Produit")
    product_echantillon_id = fields.One2many("cps.product.echantillon", 'product_id', string="Produit")
    design_interne = fields.Char('Désign. interne')
