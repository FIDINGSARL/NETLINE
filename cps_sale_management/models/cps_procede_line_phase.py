# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import date

class FicheProcedeLinePhase(models.Model):
    _name = 'fiche.procede.line.phase'

    name = fields.Char(string="Phase", required=True)
    procede_line_id = fields.One2many('fiche.procede.line', "phase_id", string="Phase")
    # passe_line_id = fields.One2many('netline.passe.line', "phase_id", string="Phase")
