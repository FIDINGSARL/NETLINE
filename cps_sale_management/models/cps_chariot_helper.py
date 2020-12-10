from odoo import models, fields, api

class CpsChariotHelper(models.Model):
    _name = 'cps.chariot.helper'
    _description = 'Wizard de création des chariot'

    product_id = fields.Many2one("cps.product.production", string="Commande")
    poids = fields.Integer('Poids')
    qte_reel = fields.Integer('Quantité réelle')
    qte = fields.Integer('Quantité prévue', readonly=True, compute="compute_quantite")

    def create_chariot(self):
        bom_id = self.env['mrp.bom'].search([('product_tmpl_id', '=', self.product_id.product_id.product_tmpl_id.id)], order='id desc', limit=1)
        chariot = self.env['mrp.production'].create({
            'product_id': self.product_id.product_id.id,
            'product_uom_id': self.product_id.product_id.uom_id.id,
            'product_qty': self.qte_reel,
            'poids': self.poids,
            'bom_id' : bom_id.id,
            'routing_id' : bom_id.routing_id.id
        })
        chariot._onchange_move_raw()
        chariot.action_confirm()

        # location_id = bom_line_id and product.property_stock_production or self.location_id
        # location_dest_id = bom_line_id and self.location_dest_id or product.with_context(force_company=self.company_id.id).property_stock_production
        # warehouse = location_dest_id.get_warehouse()
        print('Creation stock move----------------------------------------------------')
        mo_type = self.env['res.config.settings'].get_mo_type()
        picking = self.env['stock.picking'].create({
            'picking_type_id': mo_type.id,
            'location_id': mo_type.default_location_src_id.id,
            'location_dest_id': mo_type.default_location_dest_id.id,
        })
        mo_stock_move = self.env['stock.move'].create({
            'picking_id': picking.id,
            'picking_type_id': mo_type.id,
            'product_id': self.product_id.product_id.id,
            'product_uom_qty': self.qte,
            'product_uom': self.product_id.product_id.uom_id.id,
            'location_id': mo_type.default_location_src_id.id,
            'location_dest_id': mo_type.default_location_dest_id.id,
            'name': chariot.name,
            'state': 'confirmed',
        })
        print('Creation stock move----------------------------------------------------', mo_stock_move.location_dest_id.name)
        mo_stock_move._action_assign()
        mo_stock_move._set_quantity_done(self.qte)
        mo_stock_move._action_done()

        result = {
            'name': "Chariot",
            'view_type': 'form',
            'res_model': 'mrp.production',
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


