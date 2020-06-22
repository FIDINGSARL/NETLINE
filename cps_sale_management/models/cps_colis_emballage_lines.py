# -*- coding: utf-8 -*-

from odoo import models, fields, api

class CpsColisEmballage(models.Model):
    _name = 'cps.colis.emballage.lines'
    _description = "Liste des colis d'emballage"



    qte = fields.Float('Quantité à emballer')
    sequence = fields.Integer('N° Colis')
    qte_emballer = fields.Integer('Quantité / colis')
    colis_id = fields.Many2one('cps.colis.emballage')