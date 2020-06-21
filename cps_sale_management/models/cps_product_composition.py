# -*- coding: utf-8 -*-
from odoo import models, fields, api


class CpsProductComposition(models.Model):
    _name = 'cps.product.composition'
    _description = 'Cps product composition'

    name = fields.Char("Composition", required=True)
    template_id = fields.One2many("cps.product.template", 'composition_id', "Produits")