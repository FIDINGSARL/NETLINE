# # -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime, timedelta

class CpsHrHoraire(models.Model):
    _name = 'cps.hr.horaire'

    date_debut = fields.Datetime('Début application horaire')
    date_fin = fields.Datetime('Fin application horaire')

    horaire_debut = fields.Datetime('Heure debut')
    horaire_fin = fields.Datetime('Heure Fin')
    duree_pause = fields.Float('Durée pause')

    name = fields.Char("name", compute="compute_name", store=True)

    def name_get(self):
        res = []
        #designation_client, designation, type, couleur
        for rec in self:
            name = rec.name
            res.append((rec.id, name))
        return res

    @api.depends('horaire_debut','horaire_fin')
    def compute_name(self):
        recs = []
        for p in self:
            name = ""
            if p.horaire_debut is not False:
                name = name + " DE " + (datetime.strptime(p.horaire_debut.strftime('%H:%M:%S'), '%H:%M:%S') + timedelta(hours=1)).strftime('%H:%M')
            if p.horaire_fin is not False:
                name = name + " A " +(datetime.strptime(p.horaire_fin.strftime('%H:%M:%S'), '%H:%M:%S') + timedelta(hours=1)).strftime('%H:%M')
            p.name=name
