# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import date

class CpsProductComment(models.Model):
    _name = 'cps.product.comment'
    _description = 'Commentaires sur les produits'

    name = fields.Char("Nom", required=True)
    # product_textil_id = fields.Many2one('cps.textil', 'comment_ids')
    product_echantillon_id = fields.Many2one('cps.product.echantillon', 'comment_ids')
