from odoo import models, fields, api

class MrpRoutingWorkCenter(models.Model):
    _name = 'mrp.routing.workcenter'
    _inherit = 'mrp.routing.workcenter'

    fiche_procede_ids =  fields.One2many('fiche.procede', 'mrp_routing_workcenter_id')
