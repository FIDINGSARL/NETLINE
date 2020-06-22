# -*- coding: utf-8 -*-

from odoo import models, fields, api

class CpsProduTraitement(models.Model):
    _name = 'cps.product.traitement'
    _order = "name"
    _description = "Traitements de l'article"

    name = fields.Char("Traitement", required=True)
    state = fields.Selection([('nok', 'Non validé'), ('ok', 'Validé'), ('annule', 'Annulé')], required=True,
                             default='nok')
    section_id = fields.Many2one('mrp.workcenter', 'Section')
    # demanded_work_echantillon_ids = fields.One2many('cps.product.echantillon', 'demanded_work_ids', string="Traitement demandé")
    # done_work_echantillon_ids = fields.One2many('cps.product.echantillon', 'done_work_ids', string="Traitement fait")
    # traitement_effectuee_echantillon_ids = fields.One2many('cps.product.echantillon', 'traitement_effectuee_ids', string="Traitement")
    # traitement_echantillon_prix = fields.One2many('cps.textil.traitement.prix', 'traitement_echantillon',
    #                                               string="Prix Traitement")
    # traitement_production_prix = fields.One2many('cps.textil.traitement.production.prix', 'traitement',
    #                                              string="Prix Traitement")
    fiche_procede_ids = fields.One2many('fiche.procede', 'traitement_id', string='Fiches procédés')





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
                name = name + s.name
            return name

    def set_valide(self):
        for s in self:
            s.state = "ok"

    def set_annule(self):
        for s in self:
            s.state = "annule"
