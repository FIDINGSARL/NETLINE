from odoo import models, fields, api

class CpsChariotHelper(models.Model):
    _name = 'cps.chariot.helper'
    _description = 'Wizard de création des chariot'

    product_id = fields.Many2one("cps.product.production", string="Commande")
    poids = fields.Integer('Poids')
    qte_reel = fields.Integer('Quantité réelle')
    qte = fields.Integer('Quantité prévue', readonly=True, compute="compute_quantite")


    def create_chariot(self):
        chariot = self.env['cps.chariot'].create({
            'product_production_id': self.product_id.id,
            'poids': self.poids,
            'qte_reel': self.qte_reel,
        })

        result = {
            'name': "Chariot",
            'view_type': 'form',
            'res_model': 'cps.chariot',
            'res_id': chariot.id,
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
        }
        return result


    @api.depends('poids','product_id')
    @api.onchange('poids')
    def compute_quantite(self):
        for p in self:
            qte = 0
            if p.poids is not False and p.product_id.product_tmpl_id.poids is not False  :
                if p.product_id.product_tmpl_id.poids != 0 :
                    qte = qte + (p.poids/p.product_id.product_tmpl_id.poids)
            p.qte = qte


