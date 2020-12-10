from odoo import models, fields, api

class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'

    product_template_livraison_id = fields.Many2one('cps.product.template', 'Livraisons echantillons')
    is_echantillon = fields.Boolean('Est un échantillon')
    is_commande = fields.Boolean('Est une commande')