from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _name = 'purchase.order'
    _inherit = 'purchase.order'

    product_template_reception_id = fields.Many2one('cps.product.template', 'Livraisons echantillons')
    is_echantillon = fields.Boolean('Est un échantillon')
    is_commande = fields.Boolean('Est une commande')
    is_netline = fields.Boolean('Est une commande Netline')
    # reception_id = fields.One2many('netline.reception', 'purchase_order_id', string="receptions")
    purchase_order_id = fields.Many2one('netline.purchase.da', 'Demande achat')

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    purchase_order_line_id = fields.Many2one('netline.purchase.da.line', 'Demande achat')
