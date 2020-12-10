# -*- coding: utf-8 -*-

from odoo import models, fields, api

class CpsFlux(models.Model):
    _name = 'cps.flux'
    _description = "Liste des flux de l'article"

    name = fields.Char("name", compute="compute_name")
    template_ids = fields.One2many('cps.product.template', 'flux_id', ondelete="cascade", required=True)
    reception_line_ids = fields.One2many('stock.move', 'flux_reception_id', compute="compute_reception_lines", string="Liste des récéptions")
    livraison_line_ids = fields.One2many('stock.move', 'flux_livraison_id', compute="compute_livraison_lines", string="Liste des livraisons")
    retourSansTraitment_line_ids = fields.One2many('stock.move', 'flux_reception_id', compute="compute_retourST_lines", string="Liste des retours sans traitement")
    retourReparation_line_ids = fields.One2many('stock.move', 'flux_reception_id', compute="compute_retourRP_lines", string="Retours pour réparation")
    livraisonReparation_line_ids = fields.One2many('stock.move', 'flux_livraison_id', compute="compute_livraisonRP_lines", string="Livraisons réparation")
    reference = fields.Char(related='template_ids.reference',string="Référence")
    type_article_id = fields.Many2one('product.category',related='template_ids.type_article_id')
    commande_client = fields.Char("N° commande client",related='template_ids.product_tmpl_production_ids.commande_client')
    client_id = fields.Char(related='template_ids.client_id.name', string='Client')
    atelier_id = fields.Many2one("res.partner",related='template_ids.product_tmpl_production_ids.atelier_id', string='Atelier')

    total_encours = fields.Integer(related='template_ids.total_encours', string="En cours")


    def action_creer_reception(self):
        reception = self.template_ids.action_creer_reception()
        return {
            'name': 'Créer réception',
            'res_model': 'cps.reception.helper',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': reception.id,
            'type': 'ir.actions.act_window',
            # 'context' : {'is_echantillon': True},
            'target': 'new'  # will open a popup with mail.message list
        }

    def action_creer_reception_correction(self):
        reception = self.template_ids.action_creer_reception_correction()
        return {
            'name': 'Créer correction',
            'res_model': 'cps.reception.helper',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': reception.id,
            'type': 'ir.actions.act_window',
            # 'context' : {'is_echantillon': True},
            'target': 'new'  # will open a popup with mail.message list
        }

    def action_creer_livraison(self):
        livraison = self.template_ids.action_creer_livraison()
        return {
            'name': 'Créer Livraison',
            'res_model': 'cps.livraison.helper',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': livraison.id,
            # 'context': {'is_echantillon': True},
            'type': 'ir.actions.act_window',
            'target': 'new'  # will open a popup with mail.message list
        }

    @api.depends('template_ids')
    def compute_name(self):
        res = []
        # designation_client, designation, type, couleur
        for p in self:
            name = ""
            if p.template_ids.name is not False:
                name = name + p.template_ids.name
            p.name = "flux" + " - " + name

    @api.depends('template_ids')
    def compute_reception_lines(self):

        for p in self:
            p.reception_line_ids=self.env['stock.move'].search([("product_template_reception_id", "=", p.template_ids.id),("to_refund", "=", False),("state", "!=", 'cancel'),('location_dest_id','=',self.env['res.config.settings'].get_reception_type().default_location_dest_id.id)])

    @api.depends('template_ids')
    def compute_livraison_lines(self):
        for p in self:
            p.livraison_line_ids= self.env['stock.move'].search([("product_template_livraison_id", "=", p.template_ids.id),("to_refund", "=", False),("state", "!=", 'cancel'),('location_id','=',self.env['res.config.settings'].get_livraison_type().default_location_src_id.id)])

    @api.depends('template_ids')
    def compute_retourST_lines(self):
        for p in self:
            p.retourSansTraitment_line_ids = self.env['stock.move'].search(
                [("product_template_livraison_id", "=", p.template_ids.id), ("to_refund", "=", True),("state", "!=", 'cancel'),('location_id','=',self.env['res.config.settings'].get_livraison_type().default_location_src_id.id)])

    @api.depends('template_ids')
    def compute_retourRP_lines(self):
        for p in self:
            p.retourReparation_line_ids = self.env['stock.move'].search(
                [("product_template_reception_id", "=", p.template_ids.id),("state", "!=", 'cancel'), ('location_dest_id','=',self.env['res.config.settings'].get_reception_reparation_type().default_location_dest_id.id)])

    @api.depends('template_ids')
    def compute_livraisonRP_lines(self):
        for p in self:
            p.livraisonReparation_line_ids = self.env['stock.move'].search(
                [("product_template_livraison_id", "=", p.template_ids.id),("state", "!=", 'cancel'), ('location_id','=',self.env['res.config.settings'].get_livraison_reparation_type().default_location_src_id.id)])
