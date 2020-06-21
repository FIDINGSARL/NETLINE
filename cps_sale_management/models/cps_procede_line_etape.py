# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import date

class ProcedeLineEtape(models.Model):
    _name = 'fiche.procede.line.etape'

    name = fields.Char(string="Etape", required=True)
    procede_line_id = fields.One2many('fiche.procede.line', "etape_id", string="Etape")
    # passe_line_id = fields.One2many('netline.passe.line', "etape_id", string="Etape")
