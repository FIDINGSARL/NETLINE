# -*- coding: utf-8 -*-
from odoo import models, fields, api


class CpsProductMatiere(models.Model):
    _name = 'cps.product.matiere'
    _description = 'Cps product matiere'

    name = fields.Char("Matière", required=True)
    # product_textil_id = fields.Many2one('cps.textil', 'comment_ids')
    template_id = fields.One2many("cps.product.template", 'matiere_id', "Produits")