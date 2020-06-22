from odoo import models, fields, api

class StockReturnPicking(models.TransientModel):
    _name = 'stock.return.picking'
    _inherit = 'stock.return.picking'

    def create_returns(self):
        returns = super(StockReturnPicking, self)._create_returns()
        new_picking = self.env['stock.picking'].search([('id', '=', returns[0])])
        new_picking.product_template_livraison_id = self.picking_id.product_template_reception_id.id
        new_picking.product_template_reception_id = []
        new_picking.move_ids_without_package.product_template_livraison_id = self.picking_id.product_template_reception_id.id
        new_picking.move_ids_without_package.product_template_reception_id = []
        return returns
