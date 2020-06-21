from odoo import models, fields, api

class StockPicking(models.Model):
    _name = 'stock.picking'
    _inherit = 'stock.picking'

    product_template_reception_id = fields.Many2one('cps.product.template', 'Produits reception')
    product_template_livraison_id = fields.Many2one('cps.product.template', 'Produits livraison')
    # product_echantillon_livraison_id = fields.Many2one('cps.product.echantillon', 'Livraisons', string="Atelier")
    n_bon_client = fields.Char('N° bon client')
    is_echantillon = fields.Boolean('Est un échantillon')
    is_commande = fields.Boolean('Est une commande')

    def button_validate(self):
        rec = super(StockPicking, self).button_validate()
        self.product_template_reception_id.compute_all()
        return rec

    # def action_assign(self):
    #     rec = super(StockPicking, self).button_validate()
    #     if self.state=="confirmed":
    #         self.product_template_reception_id.compute_all()
    #     return rec
    #
    def action_cancel(self):
        rec = super(StockPicking, self).button_validate()
        self.product_template_reception_id.compute_all()
        return rec
