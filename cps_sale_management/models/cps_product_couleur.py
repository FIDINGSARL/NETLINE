# -*- coding: utf-8 -*-
from odoo import models, fields, api


class CpsProductCouleur(models.Model):
    _name = 'cps.product.couleur'
    _description = 'Cps product couleur'

    name = fields.Char("Couleur", required=True)
    # product_textil_id = fields.Many2one('cps.textil', 'comment_ids')
    template_id = fields.One2many("cps.product.template", 'coloriss_client', "Produits")
    pantone_id = fields.One2many("cps.pantone", 'couleur_id', "Pantones")