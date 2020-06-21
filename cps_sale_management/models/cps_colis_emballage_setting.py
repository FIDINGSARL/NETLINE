# -*- coding: utf-8 -*-

from odoo import models, fields, api

class CpsColisEmballageSetting(models.Model):
    _name = 'cps.colis.emballage.setting'
    _description = "Paramétrage colis d'emballage"

    stock_picking_type_id = fields.Many2one('stock.picking.type', string="Type d'opérations")
    stock_location_source = fields.Many2one(related="stock_picking_type_id.default_location_src_id", string="Emplacement source")
    stock_location_destination = fields.Many2one(related="stock_picking_type_id.default_location_dest_id", string="Emplacement destination")
