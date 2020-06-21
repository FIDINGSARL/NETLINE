from odoo import models, fields, api

class MrpBomLine(models.Model):
    _name = 'mrp.bom.line'
    _inherit = 'mrp.bom.line'

    procede_id =  fields.Many2one('fiche.procede', string="Fiche Procede")
    product_qty = fields.Float('Quantité',digits='Dosification')