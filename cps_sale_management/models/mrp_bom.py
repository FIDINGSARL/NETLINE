from odoo import models, fields, api

class MrpBom(models.Model):
    _name = 'mrp.bom'
    _inherit = 'mrp.bom'

    template_id =  fields.Many2one('cps.product.template', string="Fiche Procede")