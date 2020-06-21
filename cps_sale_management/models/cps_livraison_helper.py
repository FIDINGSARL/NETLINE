from odoo import models, fields, api

class CpsLivraisonHelper(models.Model):
    _name = 'cps.livraison.helper'
    _description = 'Wizard de création des bons de livraison'

    partner_id = fields.Many2one("res.partner", 'Client', required=True)
    product_id = fields.Many2one("product.product", string="Commande")
    qte = fields.Integer('Quantité')

    def create_sale_order(self):
        sOrder = self.env['sale.order'].create({
            'picking_policy': 'direct',
            'partner_shipping_id': self.partner_id.id,
            'partner_invoice_id': self.partner_id.id,
            'partner_id': self.partner_id.id,
            'product_template_livraison_id' : self.product_id.template_ids.id,
            'is_echantillon' : self.env.context.get('is_echantillon', False),
            'is_commande': self.env.context.get('is_production', False)
        })
        order_line = self.env['sale.order.line'].create({
            'product_uom_qty': self.qte,
            'product_id': self.product_id.id,
            'price_unit': self.product_id.list_price,
            'order_id': sOrder.id,
        })

        order_line._compute_tax_id()

        sOrder.action_confirm()
        out = self.env['res.config.settings'].get_livraison_type()
        # print('livraison type', out.default_location_src_id.name)
        sOrder.picking_ids[0].product_template_livraison_id = self.product_id.template_ids.id
        sOrder.picking_ids[0].location_id = out.default_location_src_id.id
        sOrder.picking_ids[0].move_lines[0].write({'location_id' : out.default_location_src_id.id, 'product_template_livraison_id' :self.product_id.template_ids.id })
        # sOrder.picking_ids[0].move_lines[0].product_template_livraison_id = self.product_id.template_ids.id


        result = {
            'name': "stock.picking",
            'view_type': 'form',
            'res_model': 'stock.picking',
            'res_id': sOrder.picking_ids[0].id,
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
        }
        return result



