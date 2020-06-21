from odoo import models, fields, api

class StockMove(models.Model):
    _name = 'stock.move'
    _inherit = 'stock.move'

    product_template_reception_id = fields.Many2one('cps.product.template', 'Receptions echantillons tmpl' )
    product_template_livraison_id = fields.Many2one('cps.product.template', 'Livraisons echantillons tpml')
    flux_reception_id = fields.Many2one('cps.flux', 'Receptions echantillons')
    flux_livraison_id = fields.Many2one('cps.flux', 'Livraisons echantillons')
    is_echantillon = fields.Boolean('Est un échantillon')
    is_commande = fields.Boolean('Est une commande')
    n_bon_client = fields.Char('N° bon client')
    date_done = fields.Datetime(related='picking_id.date_done')

    product_template_reception_code_article = fields.Char(related='product_template_reception_id.code_article')
    product_template_livraison_code_article = fields.Char(related='product_template_livraison_id.code_article')

    def open_line(self):
        return {
            'name': 'Réception',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'stock.picking',
            'res_id': self.picking_id.id,
            'type': 'ir.actions.act_window',
            'target': 'current'
        }

    def write(self, values):
        stock_move = super(StockMove, self).write(values)
        if len(self.product_template_reception_id)>0:
            self.product_template_reception_id.compute_all()
        if len(self.product_template_livraison_id)>0:
            self.product_template_livraison_id.compute_all()
        return stock_move

    @api.model
    def create(self, values):
        stock_move = super(StockMove, self).create(values)
        if len(stock_move.product_template_reception_id)>0:
            stock_move.product_template_reception_id.compute_all()
        if len(stock_move.product_template_livraison_id)>0:
            stock_move.product_template_livraison_id.compute_all()
        return stock_move

