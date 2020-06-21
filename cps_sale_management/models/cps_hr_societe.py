# # -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import date, datetime, timedelta



class CpsHrSociete(models.Model):

    _name = 'cps.hr.societe'

    name = fields.Char('Nom', compute="compute_name")
    societe = fields.Char('Société')
    type_societe=fields.Selection([('permanent', 'Permanent'), ('interimaire', 'Interimaire')], string='Type société', default='permanent')

    def name_get(self):
        res = []
        for rec in self:
            name = rec.name
            res.append((rec.id, name))
        return res

    def get_name(self):
        for s in self:
            name = ""
            if s.name is not False:
                name = name + s.societe + " " + s.type_societe
            return name

    @api.depends('societe','type_societe')
    def compute_name(self):
        recs = []
        for p in self:
            name = ""
            if p.societe is not False:
                name = name + str(p.societe)
            if p.type_societe is not False:
                name = name + " (" + str(p.type_societe) + ")"
            p.name=name
