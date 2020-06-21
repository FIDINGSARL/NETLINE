from odoo import models, fields, api

class StockReturnPicking(models.Model):
    _name = 'stock.location'
    _inherit = 'stock.location'

    # settings_reception_location = fields.One2many("res.config.settings", 'test', string='Emplacement de réception')
    # settings_livraison_location = fields.One2many("cps.settings", 'default_livraison_location', string='Emplacement de livraison')
