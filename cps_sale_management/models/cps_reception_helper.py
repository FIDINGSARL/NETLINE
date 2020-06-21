from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError

class CpsReceptionHelper(models.Model):
    _name = 'cps.reception.helper'
    _description = 'Wizard des récéptions'

    partner_id = fields.Many2one("res.partner", 'Client', required=True)
    product_id = fields.Many2one("product.product", string="Commande")
    n_bon_client = fields.Char('N° bon client')
    qte = fields.Integer('Quantité')
    is_correction = fields.Boolean('Est une correction')
    def create_stock_move_in(self):
        if self.is_correction:
            if self.qte+self.product_id.template_ids.total_retour_correction > self.product_id.template_ids.total_sortie:
                raise UserError(_("Vous avez dépassé la quantité livrée !"))
        else:
            if self.qte+self.product_id.template_ids.total_entree >self.product_id.template_ids.qte+(self.product_id.template_ids.qte*10/100) and not self.is_correction:
                raise UserError(_("Vous avez dépassé la quantité de la commande !"))
        partner_location = self.env['stock.location'].search([('usage', '=', 'customer')])
        if self.is_correction:
            recept = self.env['res.config.settings'].get_reception_reparation_type()
        else:
            recept = self.env['res.config.settings'].get_reception_type()

        pOrder = self.env['purchase.order'].create({
            'picking_type_id': recept.id,
            'company_id': self.env.user.company_id.id,
            'partner_id': self.partner_id.id,
            'date_order': fields.datetime.now(),
            'date_planned': fields.datetime.now(),
            'currency_id': self.env.user.company_id.currency_id.id,
            'product_template_reception_id' : self.product_id.template_ids.id,
            'is_echantillon' : 0,
            'is_commande': 1,
            'order_line': [(0, 0, {
                            'product_id': self.product_id.id,
                            'name': self.product_id.name,
                            'product_uom_qty': self.qte,
                            'product_qty': self.qte,
                            'price_unit':self.product_id.list_price,
                            'product_uom' : self.product_id.uom_id.id,
                            })]
        })
        pOrder.button_confirm()
        pOrder.date_planned = fields.datetime.now()
        # pOrder.picking_ids[0].picking_type_id=recept.id
        pOrder.picking_ids[0].move_type='direct'
        pOrder.picking_ids[0].location_id=partner_location.id
        pOrder.picking_ids[0].location_dest_id=recept.default_location_dest_id.id
        pOrder.picking_ids[0].product_template_reception_id = self.product_id.template_ids.id
        pOrder.picking_ids[0].n_bon_client = self.n_bon_client
        pOrder.picking_ids[0].move_ids_without_package[0].product_template_reception_id = self.product_id.template_ids.id
        pOrder.picking_ids[0].move_ids_without_package[0].n_bon_client = self.n_bon_client
        pOrder.picking_ids[0].action_confirm()
        pOrder.picking_ids[0].action_assign()
        result = {
            'name': "stock.picking",
            'view_type': 'form',
            'res_model': 'stock.picking',
            'res_id': pOrder.picking_ids[0].id,
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
        }
        return result