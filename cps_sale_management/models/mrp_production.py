from odoo import models, fields, api

class MrpProduction(models.Model):
    _name = 'mrp.production'
    _inherit = 'mrp.production'

    poids = fields.Integer('Poids')
