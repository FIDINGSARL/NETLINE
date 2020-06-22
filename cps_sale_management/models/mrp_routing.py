from odoo import models, fields, api

class MrpRouting(models.Model):
    _name = 'mrp.routing'
    _inherit = 'mrp.routing'

    template_id =  fields.Many2one('cps.product.template', string="Echantillons")
    # echantillon_ids =  fields.Many2one('cps.product.echantillon', string="Echantillons")
    # production_ids =  fields.Many2one('cps.product.production', string="COmmandes")
