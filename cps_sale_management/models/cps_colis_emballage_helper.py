from odoo import models, fields, api

class CpsColisEmballageHelper(models.Model):
    _name = 'cps.colis.emballage.helper'
    _description = 'Wizard de création des bons de livraison'

    product_id = fields.Many2one("cps.product.production", string="Commande")
    qte = fields.Integer('Quantité')
    qte_par_colis = fields.Integer('Quantité/Colis')
    type_sortie = fields.Selection([('normal','Normal'), ('2eme','2eme Choix'), ('declasse','Déclassé')], string='Type sortie', required=True, default='normal')

    def create_sale_order(self):
        emballage = self.env['cps.colis.emballage'].create({
            'product_production_id': self.product_id.id,
            'qte': self.qte,
            'qte_emballer': self.qte_par_colis,
            'type_sortie': self.type_sortie,
        })
        self.product_id.compute_total_sortie_emballage()
        result = {
            'name': "Emballage colis",
            'view_type': 'form',
            'res_model': 'cps.colis.emballage',
            'res_id': emballage.id,
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
        }
        return result

    def unlink(self):
        for p in self:
            p.product_id.total_sortie_emballage()



