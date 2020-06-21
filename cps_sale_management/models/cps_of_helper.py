from odoo import models, fields, api

class CpsOFHelper(models.Model):
    _name = 'cps.of.helper'
    _description = 'Wizard de création des ordres de fabrication'

    product_id = fields.Many2one("product.product", string="Commande")
    qte = fields.Integer('Quantité')

    def create_of(self):
        bom_id = self.env['mrp.bom'].search([('product_id', '=', self.product_id.id)], order='id desc', limit=1)
        of = self.env['mrp.production'].create({
            'product_id': self.product_id.id,
            'product_uom_id' : self.product_id.uom_id.id,
            'product_qty':self.qte,
            'product_uom_qty': self.qte,
            'bom_id' : bom_id.id
        })
        # of.action_confirm()
        # of.action_assign()
        # of.button_plan()
        result = {
            'name': "Ordre de fabrication",
            'view_type': 'form',
            'res_model': 'mrp.production',
            'res_id': of.id,
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
        }
        return result



