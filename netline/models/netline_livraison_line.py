# # -*- coding: utf-8 -*-
# from tarfile import _BZ2Proxy

from odoo import models, fields, api


class Netline_livraison_line_transient(models.Model):
    _name = 'netline.livraison.line'

    reception_line_id = fields.Many2one('netline.reception.line', 'Reception Ligne')
    n_porteur = fields.Char(related="reception_line_id.n_porteur", readonly=True, store=True)

    laundry_product_name = fields.Char(related='reception_line_id.product_id.name', readonly=True)
    pressing_product_name = fields.Char(related='reception_line_id.product_pressing_id.name', readonly=True)
    vt_product_name = fields.Char(related='reception_line_id.product_vt_id.name', readonly=True)

    n_chambre = fields.Char(related='reception_line_id.n_chambre')
    nom_porteur = fields.Char(related='reception_line_id.nom_porteur')

    traitement = fields.Selection(related='reception_line_id.traitement', store=True, readonly=True)
    livraison_id = fields.Many2one('netline.livraison', 'livraison')
    livraison_state = fields.Selection(string="Etat de la livraison", selection=[('cancelled', 'Annulé'),
                                                                       ('waiting', 'A valider'),
                                                                       ('ready', 'Prêt à facturer'),
                                                                       ('invoiced', 'Facturé')], related='livraison_id.state', store=True)

    to_deliver_quantity = fields.Integer("Quantité à livrer")
    available_quantity = fields.Integer(related='reception_line_id.available_quantity', readonly=True, store=True)
    original_quantity = fields.Integer(related='reception_line_id.quantity', readonly=True, store=True)

    sale_order_line_id = fields.Many2one('sale.order.line', 'Sale order line')

    price_location= fields.Float('Prix Location')
    is_location = fields.Boolean('is Location')

    n_bon = fields.Char(related="livraison_id.sale_order_name", string="N° Bon")
    date_livraison = fields.Datetime(related="livraison_id.date_livraison", string="Date livraison")

    @api.onchange('to_deliver_quantity')
    def onchange_to_deliver_quantity(self):
        if self.to_deliver_quantity > self.available_quantity+self._origin.to_deliver_quantity:
            self.to_deliver_quantity = 0
            return {
                'warning': {
                    'title': "Message d'erreur",
                    'message': "La quantité que vous avez saisi depasse l'encours actuel !",
                }
            }


    def unlink(self):
        receptions =[]
        for s in self:
            s.sale_order_line_id.unlink()
            quantity = s.to_deliver_quantity + s.reception_line_id.available_quantity
            reception_id = s.reception_line_id.reception_id.id
            s.reception_line_id.write ({'delivered_quantity' : s.reception_line_id.delivered_quantity-s.to_deliver_quantity})
            livraison_line= super(Netline_livraison_line_transient, s).unlink()
            reception = s.env['netline.reception'].search([('id', '=', reception_id)])
            if reception not in receptions:
                receptions.append(reception)
        for reception_to_define in receptions:
            reception_to_define.define_state()
        if len(self)>0:
            return livraison_line

    @api.model
    def create(self, values):
        #print "create"
        to_deliver_quantity = values.get('to_deliver_quantity')
        available_quantity = values.get('available_quantity')
        is_laundry = False
        is_vt = False
        is_pressing = False
        reception_line = self.env['netline.reception.line'].search([('id', '=', values.get('reception_line_id'))])
        product = None
        print ('values.get --------------', values)
        print ('reception line --------------', reception_line)
        print ('product id--------------', reception_line.product_id)
        print ('product id vt--------------', reception_line.product_vt_id)
        print ('product id pressing--------------', reception_line.product_pressing_id)
        if reception_line.product_id.id is not False:
            is_laundry = True
            product = reception_line.product_id
        if reception_line.product_vt_id.id is not False:
            is_vt = True
            product = reception_line.product_vt_id
        if reception_line.product_pressing_id.id is not False:
            product = reception_line.product_pressing_id
            is_pressing = True
        if 'traitement' in values:
            price = product.get_price(values['traitement'])
        else:
            price = product.get_price('lavage')
        livraison = self.env['netline.livraison'].search([('id', '=', values.get('livraison_id'))])
        #print "livraison ", livraison
        #print "livraison ", self.livraison_id.sale_order_id.id
        client = self.env['res.partner'].search([('id', '=', livraison.client_id.id)])
        devise = client.devise
        if devise.id is not False:
            devise = self.env.user.company_id.currency_id
        order_line = self.env['sale.order.line'].create({
            'product_uom_qty': to_deliver_quantity,
            'product_uom': 1,
            'product_id': product.product_id.id,
            'customer_lead': 0,
            'price_unit': price,
            'order_id': livraison.sale_order_id.id,
            'currency_id': devise.id,
            'traitement': values.get('traitement')
        })
        values['sale_order_line_id']=order_line.id
        if type(values['reception_line_id']) is not int:
            values['reception_line_id'] = values['reception_line_id'][0]
        livraison_line= super(Netline_livraison_line_transient, self).create(values)

        return livraison_line


    @api.model
    def write(self, values):
        #if self.livraison_id.state == 'invoiced'
        #do not write
        #print "write"
        to_deliver_quantity = values.get('to_deliver_quantity')
        product = None
        available_quantity = self.available_quantity
        if self.reception_line_id.product_vt_id.id is not False:
            product = self.reception_line_id.product_vt_id
        if self.reception_line_id.product_id.id is not False:
            product = self.reception_line_id.product_id
        if self.reception_line_id.product_pressing_id.id is not False:
            product = self.reception_line_id.product_pressing_id
        #values
        if 'traitement' in values:
            price = product.get_price(values['traitement'])
        else:
            price = product.get_price(self.traitement)
        self.sale_order_line_id.write({'price_unit': price})
        if 'to_deliver_quantity' in values :
            self.sale_order_line_id.write({'price_unit': price, 'product_uom_qty': values.get("to_deliver_quantity")})
        livraison_line= super(Netline_livraison_line_transient, self).write(values)
        self.reception_line_id.reception_id.define_state()
        return livraison_line


class Netline_sale_order_line(models.Model):
    _name = 'sale.order.line'
    _inherit = 'sale.order.line'

    traitement = fields.Char(string = "Traitement")
    netline_livraison_line_ids = fields.One2many('netline.livraison.line', 'sale_order_line_id')
    is_netline = fields.Boolean('Is Netline')

    def recalculate_prices(self):
        return self.reset_lines(price=True)


    def reset_lines(self, price=False):
        """
        Reset lines according informations on products and price list
        :param price: boolean to indicate if we are resetting price or
                      descriptions
        """
        try:
            for line in self.mapped('order_line'):
                order = line.order_id
                res = line.product_id_change(
                    order.pricelist_id.id, line.product_id.id,
                    qty=line.product_uom_qty, uom=line.product_uom.id,
                    qty_uos=line.product_uos_qty, uos=line.product_uos.id,
                    name=line.name, partner_id=order.partner_id.id, lang=False,
                    update_tax=True, date_order=order.date_order, packaging=False,
                    fiscal_position=order.fiscal_position.id, flag=price)
                if price:
                    line.write(res['value'])
                else:
                    if 'name' in res['value']:
                        line.write({'name': res['value']['name']})
        except:
            print("")
            #"no recalculate required"


    def unlink(self):
        #"unlink called"
        self.recalculate_prices()
        return super(Netline_sale_order_line, self).unlink()
