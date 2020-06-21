# -*- coding: utf-8 -*-
from odoo import models, fields, api


class CpsProductMarque(models.Model):
    _name = 'cps.product.marque'
    _description = 'Cps product marque'

    name = fields.Char("Marque", required=True)
    # product_textil_id = fields.Many2one('cps.textil', 'comment_ids')
    template_id = fields.One2many("cps.product.template", 'marque', "Produits")