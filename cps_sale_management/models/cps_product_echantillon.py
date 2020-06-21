# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError

class CpsProductEchantillon(models.Model):
    _name = 'cps.product.echantillon'
    _inherits = {'cps.product.template': 'product_tmpl_id'}
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Liste des echantillons'
    # traitement_ids = fields.One2many("cps.product.traitement.liste", 'echantillon_id', "Traitement fait")
    # traitement_name = fields.Char(compute='compute_traitement_name', string='Traitement')
    # route_ids = fields.One2many("mrp.routing", "echantillon_ids", string="Route")
    # route_count = fields.Integer(compute='compute_count_route')
    name = fields.Char("name", compute='compute_name', store=True)
    state = fields.Selection([('pret', 'Pret'), ('recu','Reçu'), ('traitement','Traitement'), ('fait','Traité'), ('controle','Controlé'), ('expedie','Expédié'), ('valide','Validé'), ('annule','Sans suite'), ('prod','En prod')], string='Statut', required=True, default='pret')
    product_id = fields.Many2one('product.product', 'Produit Odoo')
    numero_demande = fields.Integer(string="N° Demande")
    production_ids= fields.One2many("cps.product.production", "echantillon_id", "Ordre de fabribation")
    production_name = fields.Char(related="production_ids.name", string="Nom des ordres de fabrication")
    production_count = fields.Integer(compute='compute_count_production')

    product_tmpl_id = fields.Many2one('cps.product.template', 'Product Template', auto_join=True, ondelete="cascade", required=True)

    @api.onchange('type_article_id')
    @api.depends('type_article_id')
    def change_type_article(self):
        cat = self.env['res.config.settings'].get_cat_mere_vente()
        pcs = self.env['product.category'].search([("parent_id", "=", cat.id)])
        ids = []
        for pc in pcs:
            ids.append(pc.id)
        return {'domain': {'type_article_id': [('id', 'in', ids)]}}

    def set_recu(self):
        self.state='recu'

    def set_traitement(self):
        self.state='traitement'

    def set_traite(self):
        self.state='fait'

    def set_controle(self):
        self.state='controle'

    def set_expedie(self):
        self.state='expedie'

    def set_valide(self):
        self.state='valide'

    def set_annule(self):
        self.state='annule'

    def set_prod(self):
        self.state='prod'

    def action_generer_fiche_procede(self):
        self.product_tmpl_id.action_generer_fiche_procede()

    def compute_count_production(self):
        self.production_count = len(self.production_ids)

    @api.depends('type_article_id', 'reference', 'coloriss_client')
    def compute_name(self):
        name=""
        if self.type_article_id.name is not False:
            name = str(self.type_article_id.name)
        if self.reference is not False:
            name = name + " Ref. " + str(self.reference)
        if self.coloriss_client.name is not False:
            name = name + " Col. " + str(self.coloriss_client.name)
        self.name = name

    def action_creer_reception(self):
        reception = self.product_tmpl_id.action_creer_reception()
        self.state="recu"
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

    def action_view_receptions(self):
        reception = self.product_tmpl_id.action_view_receptions()
        return {
            'name': 'Liste des réceptions',
            'res_model': 'stock.picking',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', reception.ids)],
            'type': 'ir.actions.act_window',
            'target': 'current'  # will open a popup with mail.message list
        }

    def action_creer_livraison(self):
        livraison = self.product_tmpl_id.action_creer_livraison()
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

    def action_view_livraisons(self):
        livraison = self.product_tmpl_id.action_view_livraisons()
        return {
            'name': 'Liste des livraisons',
            'res_model': 'stock.picking',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', livraison.ids)],
            'type': 'ir.actions.act_window',
            'target': 'current'  # will open a popup with mail.message list
        }

    def action_view_retours(self):
        retour = self.product_tmpl_id.action_view_retours()
        return {
            'name': 'Liste des retours',
            'res_model': 'stock.picking',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', retour.ids)],
            'type': 'ir.actions.act_window',
            'target': 'current'  # will open a popup with mail.message list
        }

    def action_view_flux(self):
        flux = self.product_tmpl_id.action_view_flux()
        return {
            'name': 'Liste des flux',
            'res_model': 'cps.flux',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id':self.flux_id.id,
            'type': 'ir.actions.act_window',
            'target': 'current'  # will open a popup with mail.message list
        }

    def action_creer_of(self):
        of = self.product_tmpl_id.action_creer_of()
        return {
            'name': 'Créer ordre de fabrication',
            'res_model': 'cps.of.helper',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': of.id,
            'type': 'ir.actions.act_window',
            'target': 'new'  # will open a popup with mail.message list
        }

    def action_view_product_production(self):
        if len(self.production_ids) > 0:
            return {
                'name': 'Ordre de fabrication',
                'res_model': 'cps.product.production',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'domain': [('id', 'in', self.production_ids.ids)],
                'type': 'ir.actions.act_window',
                'target': 'current'  # will open a popup with mail.message list
            }
        else :
            raise UserError(_("Aucun OF n'est encore disponible !"))

    def action_transformer_en_production(self):
        product_production = self.env['cps.product.production'].create({
            'image_devant' : self.image_devant,
            'image_dos' : self.image_dos,
            'client_id' : self.client_id.id,
            'client_principal_id' : self.client_principal_id.id,
            'reference' : self.reference,
            'segment' : self.segment,
            'coloriss_client' : self.coloriss_client.id,
            'marque' : self.marque.id,
            'matiere_id' : self.matiere_id.id,
            'composition_id' : self.composition_id.id,
            'poids' : self.poids,
            'state' : 'pret',
            'price' : 0,
            'type_couleur' : self.type_couleur,
            'type_article_id' : self.type_article_id.id,
            'pantone_id' : self.pantone_id.id,
            'echantillon_id': self.id,
            # 'fiche_procede_ids' : [(4, procedes)],
        })
        default = None
        default = dict(default or {})
        default.update({
            'template_id': product_production.product_tmpl_id.id
        })
        new_traitements = self.traitement_ids.copy(default)
        product_production.write({'traitement_ids' : new_traitements.ids})

        default = None
        default = dict(default or {})
        default.update({
            'template_id': product_production.product_tmpl_id.id
        })
        new_procedes = self.fiche_procede_ids.copy(default)
        product_production.write({'fiche_procede_ids' : new_procedes.ids})

        self.state="prod"
        return {
            'name': 'Ordre de fabrication',
            'res_model': 'cps.product.production',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': product_production.id,
            'type': 'ir.actions.act_window',
            'context' : {'is_production': True},
            'target': 'current'  # will open a popup with mail.message list
        }

    def action_view_route(self):
        routes = self.product_tmpl_id.action_view_route()
        return {
            'name': 'Liste des routes',
            'res_model': 'mrp.routing',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', routes.ids)],
            'type': 'ir.actions.act_window',
            'target': 'current'  # will open a popup with mail.message list
        }

    def action_view_bom(self):
        boms = self.product_tmpl_id.action_view_bom()
        return {
            'name': 'Liste des nomenclatures',
            'res_model': 'mrp.bom',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', boms.ids)],
            'type': 'ir.actions.act_window',
            'target': 'current'  # will open a popup with mail.message list
        }

    def action_view_procede(self):
        procedes = self.product_tmpl_id.action_view_procede()
        return {
            'name': 'Liste des fiches procédés',
            'res_model': 'fiche.procede',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', procedes.ids)],
            'type': 'ir.actions.act_window',
            'target': 'current'  # will open a popup with mail.message list
        }

    @api.model
    def create(self, values):
        last_demande = self.env['cps.product.echantillon'].search([("numero_demande", "<>", "")], order='numero_demande desc', limit=1)
        values['numero_demande'] = str(int(last_demande.numero_demande) + 1)
        product_echantillon = super(CpsProductEchantillon, self).create(values)
        product_echantillon.product_id=product_echantillon.product_tmpl_echantillon_ids.product_id
        return product_echantillon

    @api.onchange('poids')
    def compute_quantite_machine(self):
        for p in self.fiche_procede_ids:
            p._compute_qte_machine()
        for p in self.traitement_ids:
            p.poids_article = self.poids

    @api.onchange("traitement_ids")
    def on_change_traitement_ids(self):
        self.traitement_ids.poids_article = self.poids

