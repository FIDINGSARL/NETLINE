from odoo import models, fields, api
from ast import literal_eval

class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    picking_type_reception = fields.Many2one("stock.picking.type", "Opérations reception")
    picking_type_livraison = fields.Many2one("stock.picking.type", "Opérations livraison")

    picking_type_reception_reparation = fields.Many2one("stock.picking.type", "Opérations reception correction")
    picking_type_livraison_reparation = fields.Many2one("stock.picking.type", "Opérations livraion correction")

    categorie_mere_article = fields.Many2one("product.category", "Catégorie mère des échantillons/productions (Cat. mère : Vendable)")

    categorie_mere_pc = fields.Many2one("product.category", "Catégorie mère des produits chimiques/colorants (Cat. mère : Expenses)")

    # attribut_couleur = fields.Many2one("product.attribute", "Attribut couleur")
    # attribut_marque = fields.Many2one("product.attribute", "Attribut marque")
    # attribut_matiere = fields.Many2one("product.attribute", "Attribut matière")
    # attribut_composition = fields.Many2one("product.attribute", "Attribut composition")

    @api.onchange('categorie_mere_article')
    def change_type_article(self):
        pcs = self.env['product.category'].search([("name", "=", "Vendable")])
        pcs = self.env['product.category'].search([("id", "child_of", pcs.id)])
        ids = []
        for pc in pcs:
            ids.append(pc.id)
        return {'domain': {'categorie_mere_article': [('id', 'in', ids)]}}

    @api.onchange('categorie_mere_pc')
    def change_type_article_pc(self):
        pcs = self.env['product.category'].search([("name", "=", "Expenses")])
        pcs = self.env['product.category'].search([("id", "child_of", pcs.id)])
        ids = []
        for pc in pcs:
            ids.append(pc.id)
        return {'domain': {'categorie_mere_pc': [('id', 'in', ids)]}}

    # def get_couleur(self):
    #     attribut_couleurs = self.env['ir.config_parameter'].sudo().get_param('cps_sale_management_v13.attribut_couleur')
    #     couleur = self.env['product.attribute'].search([("id", "=", attribut_couleurs)])
    #     return couleur
    #
    # def get_marque(self):
    #     attribut_marques = self.env['ir.config_parameter'].sudo().get_param('cps_sale_management_v13.attribut_marque')
    #     marque = self.env['product.attribute'].search([("id", "=", attribut_marques)])
    #     return marque
    #
    # def get_matiere(self):
    #     attribut_matieres = self.env['ir.config_parameter'].sudo().get_param('cps_sale_management_v13.attribut_matiere')
    #     matiere = self.env['product.attribute'].search([("id", "=", attribut_matieres)])
    #     return matiere
    #
    # def get_composition(self):
    #     attribut_compositions = self.env['ir.config_parameter'].sudo().get_param('cps_sale_management_v13.attribut_composition')
    #     composition = self.env['product.attribute'].search([("id", "=", attribut_compositions)])
    #     return composition

    def get_reception_type(self):
        picking_type_receptions = self.env['ir.config_parameter'].sudo().get_param('cps_sale_management_v13.picking_type_reception')
        recept = self.env['stock.picking.type'].search([("id", "=", picking_type_receptions)])
        return recept

    def get_livraison_type(self):
        picking_type_livraisons = self.env['ir.config_parameter'].sudo().get_param('cps_sale_management_v13.picking_type_livraison')
        livraison_type = self.env['stock.picking.type'].search([("id", "=", picking_type_livraisons)])
        return livraison_type

    def get_reception_reparation_type(self):
        picking_type_receptions_reparation = self.env['ir.config_parameter'].sudo().get_param('cps_sale_management_v13.picking_type_reception_reparation')
        recept_reparation = self.env['stock.picking.type'].search([("id", "=", picking_type_receptions_reparation)])
        return recept_reparation

    def get_livraison_reparation_type(self):
        picking_type_livraisons_reparation = self.env['ir.config_parameter'].sudo().get_param('cps_sale_management_v13.picking_type_livraison_reparation')
        livraison_reparation = self.env['stock.picking.type'].search([("id", "=", picking_type_livraisons_reparation)])
        return livraison_reparation

    def get_cat_mere_vente(self):
        cat_mere = self.env['ir.config_parameter'].sudo().get_param('cps_sale_management_v13.categorie_mere_article')
        cat = self.env['stock.location'].search([("id", "=", cat_mere)])
        return cat

    def get_cat_mere_pc(self):
        cat_mere = self.env['ir.config_parameter'].sudo().get_param('cps_sale_management_v13.categorie_mere_pc')
        cat = self.env['stock.location'].search([("id", "=", cat_mere)])
        return cat


    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('cps_sale_management_v13.picking_type_reception', self.picking_type_reception.id)
        self.env['ir.config_parameter'].set_param('cps_sale_management_v13.picking_type_livraison', self.picking_type_livraison.id)
        self.env['ir.config_parameter'].set_param('cps_sale_management_v13.picking_type_reception_reparation', self.picking_type_reception_reparation.id)
        self.env['ir.config_parameter'].set_param('cps_sale_management_v13.picking_type_livraison_reparation', self.picking_type_livraison_reparation.id)
        self.env['ir.config_parameter'].set_param('cps_sale_management_v13.categorie_mere_article', self.categorie_mere_article.id)
        self.env['ir.config_parameter'].set_param('cps_sale_management_v13.categorie_mere_pc', self.categorie_mere_pc.id)
        # self.env['ir.config_parameter'].set_param('cps_sale_management_v13.attribut_couleur', self.attribut_couleur.id)
        # self.env['ir.config_parameter'].set_param('cps_sale_management_v13.attribut_marque', self.attribut_marque.id)
        # self.env['ir.config_parameter'].set_param('cps_sale_management_v13.attribut_matiere', self.attribut_matiere.id)
        # self.env['ir.config_parameter'].set_param('cps_sale_management_v13.attribut_composition', self.attribut_composition.id)
        return res

    def get_values(self):
        """Return a list of the possible values."""
        res = super(ResConfigSettings, self).get_values()
        res.update(picking_type_reception = self.get_reception_type().id)
        res.update(picking_type_livraison = self.get_livraison_type().id)
        res.update(picking_type_reception_reparation = self.get_reception_reparation_type().id)
        res.update(picking_type_livraison_reparation = self.get_livraison_reparation_type().id)
        res.update(categorie_mere_article = self.get_cat_mere_vente().id)
        res.update(categorie_mere_pc = self.get_cat_mere_pc().id)
        # res.update(attribut_couleur = self.get_couleur().id)
        # res.update(attribut_marque = self.get_marque().id)
        # res.update(attribut_matiere = self.get_matiere().id)
        # res.update(attribut_composition = self.get_composition().id)
        return res