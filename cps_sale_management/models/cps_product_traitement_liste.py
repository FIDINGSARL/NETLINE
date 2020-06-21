# -*- coding: utf-8 -*-

from odoo import models, fields, api

class CpsProduTraitementListe(models.Model):
    _name = 'cps.product.traitement.liste'
    _description = "Liste des traitements de l'article"

    sequence = fields.Integer()
    traitement_id = fields.Many2one("cps.product.traitement",  "Traitement fait")
    section = fields.Char(related='traitement_id.section_id.name', string='Section')
    fiche_procede_id = fields.Many2one('fiche.procede', string="Fiche procédé", domain="[('traitement_id', '=', traitement_id )]")
    template_id = fields.Many2one('cps.product.template', string="Traitement")
    gslide = fields.Char('Slide')
    # echantillon_id = fields.Many2one('cps.product.echantillon', string="Traitement fait")
    # production_id = fields.Many2one('cps.product.production', string="Traitement fait")
    poids_article = fields.Float('Poids article')

    @api.onchange('traitement_id')
    @api.depends('traitement_id')
    def change_traitement(self):
        self.fiche_procede_id=''

    def unlink(self):
        traitement_line = self.unlink()
        return  traitement_line