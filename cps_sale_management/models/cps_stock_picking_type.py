from odoo import models, fields, api

class StockPicking(models.Model):
    _name = 'stock.picking.type'
    _inherit = 'stock.picking.type'

    group_filter = fields.Many2one('res.groups', "Groupe d'utilisateur")
