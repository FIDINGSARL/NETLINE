# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import date

class FicheProcedeLineOperation(models.Model):
    _name = 'fiche.procede.line.operation'

    name = fields.Char(string="Operation", required=True)
    procede_line_id = fields.One2many('fiche.procede.line', "operation_id", string="Opération")
    # passe_line_id = fields.One2many('netline.passe.line', "operation_id", string="Opération")
