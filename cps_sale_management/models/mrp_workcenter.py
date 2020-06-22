from odoo import models, fields, api

class MrpWorkCenter(models.Model):
    _name = 'mrp.workcenter'
    _inherit = 'mrp.workcenter'

    echantillon_id = fields.One2many('cps.product.traitement', 'section_id', string="Section")
