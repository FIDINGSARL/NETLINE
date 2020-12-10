# -*- coding: utf-8 -*-

from odoo import models, fields, api

class CpsColisEmballage(models.Model):
    _name = 'cps.colis.emballage'
    _description = "Liste des colis d'emballage"



    product_production_id = fields.Many2one("cps.product.production", string="Article")
    client_id = fields.Many2one("res.partner", related='product_production_id.client_id')
    atelier_id = fields.Many2one("res.partner", related='product_production_id.atelier_id')
    qte = fields.Integer('Quantité à emballer')
    qte_emballer = fields.Integer('Quantité / colis')
    colis_details = fields.One2many('cps.colis.emballage.lines', 'colis_id', 'Détail des colis')
    type_sortie = fields.Selection([('normal','Normal'), ('2eme','2eme Choix'), ('declasse','Déclassé')], string='Type sortie', required=True, default='normal')
    state = fields.Selection([('draft','Brouillon'), ('ready','Pret'), ('printed','Imprimé')], string='Statut', required=True, default='ready')

    # def action_print(self):
    #     self.state="printed"
    #     print('imprimer')

    def print_report(self):
        self.state = "printed"
        return self.env.ref('cps_sale_management.emballage_report_id').report_action(self)


    @api.model
    def create(self, values):
        colis_emballage = super(CpsColisEmballage, self).create(values)
        if 'qte' in values:
            sequence = 1
            colis = []
            reste=values['qte']
            while True:
                if reste >= values['qte_emballer']:
                    colis.append((0, 0, {'qte': values['qte'], 'sequence': sequence, 'qte_emballer': values['qte_emballer']}))
                else:
                    colis.append((0, 0, {'qte': values['qte'], 'sequence': sequence, 'qte_emballer': reste}))
                sequence += 1
                reste -= values['qte_emballer']
                if reste<=0:
                    break
        colis_emballage.colis_details = colis
        self.state="ready"
        return colis_emballage

