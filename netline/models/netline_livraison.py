# # -*- coding: utf-8 -*-
# from tarfile import _BZ2Proxy

from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError, AccessError


class Netline_livraison(models.Model):
    _name = 'netline.livraison'

    client_id = fields.Many2one('res.partner', "Client", domain='[("reception_ids", "!=", False)]')
    atelier_id = fields.Many2one("res.partner", 'Atelier', domain='[("is_atelier", "=", True)]')
    client_name = fields.Char(related="client_id.name")
    sale_order_id = fields.Many2one('sale.order', "Sale Order")
    sale_order_name = fields.Char(related="sale_order_id.name", readonly=True, store=True)
    currency_id = fields.Many2one('res.currency', string='Currency')
    sale_order_montant = fields.Monetary(related="sale_order_id.amount_untaxed")
    devise = fields.Char(related="sale_order_id.currency_id.name")
    reception_line_id = fields.Many2one('netline.reception.line', 'reception_line')
    state = fields.Selection(string="Etat de la livraison", selection=[('cancelled', 'Annulé'),
                                                                       ('waiting', 'A valider'),
                                                                       ('ready', 'Prêt à facturer'),
                                                                       ('invoiced', 'Facturé')])
    date_livraison = fields.Datetime('Date', required=True)
    observation= fields.Char('Observation')

    reception_laundry_ids = fields.Many2many('netline.reception', 'laundry_reception_rel', string="reception laundry", domain= '[("client_id", "=", client_id), ("state", "in", ["ready","partial_delivred"]), ("is_laundry", "=", True)]')
    reception_pressing_ids = fields.Many2many('netline.reception', 'pressing_reception_rel', string="reception pressing", domain='[("client_id", "=", client_id), ("state", "in", ["ready","partial_delivred"]), ("is_pressing", "=", True)]')
    reception_vt_ids = fields.Many2many('netline.reception', 'vt_reception_rel', string="reception vt", domain='[("client_id", "=", client_id), ("state", "in", ["ready","partial_delivred"]), ("is_vt", "=", True)]')

    livraison_lines_ids = fields.One2many('netline.livraison.line', 'livraison_id', string="Produits")

    is_laundry= fields.Boolean(default=False)
    is_pressing = fields.Boolean(default=False)
    is_vt = fields.Boolean(default=False)
    is_location = fields.Boolean(default=False)


    delivred_quantity = fields.Integer(compute="_compute_delivred_quantity")

    def _compute_delivred_quantity(self):
        delivred_quantity = 0
        for livraison_line in self.livraison_lines_ids:
            delivred_quantity += livraison_line.to_deliver_quantity
        self.delivred_quantity = delivred_quantity


    def write(self, values):
        #values
        user = self.env['res.users'].browse(self.env.uid)
        if 'state' not in values:
            if self.state=='ready' and user.has_group('netline.group_admin') is False:
                raise UserError(
                    _("Vous ne pouvez pas modifier un bon validé !"))

        if 'client_id' in values:
            if len(self.livraison_lines_ids) > 0:
                raise UserError(
                    _("Vous ne pouvez pas changer le client !"))
            else:
                self.sale_order_id.write({'partner_id': values.get('client_id')})
        if 'date_livraison' in values:
            self.sale_order_id.write({'date_order':values.get('date_livraison')})

        livraison = super(Netline_livraison, self).write(values)

        receptions = []

        if self.is_laundry is True:
            receptions = self.reception_laundry_ids
        if self.is_vt is True:
            receptions = self.reception_vt_ids
        if self.is_pressing is True:
            receptions = self.reception_pressing_ids
        for reception in receptions:
            for reception_line in reception.receptionline_ids:
                reception_line_livraison_lines = self.env['netline.livraison.line'].search([('reception_line_id', '=', reception_line.id)])
                livraison_line_livred_quantity = 0
                for livraison_line in reception_line_livraison_lines:
                    livraison_line_livred_quantity += livraison_line.to_deliver_quantity
                #"reception line"
                #reception_line
            reception.define_state()
            return livraison



    def unlink(self):
        raise UserError(_("La livraison ne peut pas être supprimé, cliquez sur annuler si vous voulez l'annuler"))
        return super(Netline_livraison, self).unlink()


    def name_get(self):
        res = []
        for rec in self:
            if not rec.sale_order_name :
                name = ""
            else:
                date = rec.create_date
                if rec.date_livraison is not False:
                    date = rec.date_livraison
                name = rec.sale_order_name + ' | ' + date
            res.append((rec.id, name))
        return res

    def set_cancelled(self):
        self.sale_order_id.action_cancel()
        # for livraison_line in self.livraison_lines_ids:
        #     livraison_line.unlink()
        self.livraison_lines_ids.unlink()
        self.write({'state': 'cancelled'})

    def set_ready(self):
        self.write({'state': 'ready'})

    def set_waiting(self):
        self.write({'state': 'waiting'})

    def set_invoiced(self):
        self.write({'state': 'invoiced'})


    def action_update_product_prices(self):
        for livraison_line in self.livraison_lines_ids:
            livraison_line.write({'to_deliver_quantity':livraison_line.to_deliver_quantity})

    @api.model
    def create(self, values):
        values['is_laundry'] = False
        values['is_pressing'] = False
        values['is_vt'] = False
        values['is_location'] = False
        if 'is_laundry' in self.env.context:
            if self.env.context['is_laundry'] == 1:
                values['is_laundry']=True
            if self.env.context['is_pressing'] == 1:
                values['is_pressing']=True
            if self.env.context['is_vt'] == 1:
                values['is_vt']=True
        else:
            values['is_location']= True
        #values
        #"livraison lines avant creation"
        #values.get('livraison_lines_ids')

        #TODO change the warehouse id and the pricelist id
        #TODO change the pricelist_id to the pricelist affected to this client
        client = self.env['res.partner'].search([('id', '=', values['client_id'])])
        #print client
        #print client.devise
        devise = client.devise
        pricelist_id = 1
        fiscal_position=0

        #print "Devise client ", devise
        if devise.id is not False:
            if devise.name == "EUR":
                pricelist_id = self.env['product.pricelist'].search([('name', '=', 'EUR')]).id
                fiscal_position=1
        sOrder = self.env['sale.order'].create({
            'warehouse_id': 1,
            'pricelist_id': pricelist_id,
            'picking_policy': 'direct',
            'partner_shipping_id': values.get('client_id'),
            'fiscal_position_id': fiscal_position,
            'partner_invoice_id': values.get('client_id'),
            'partner_id': values.get('client_id'),
            'date_order': values.get('date_livraison'),
            'is_netline': True,
        })

        values['sale_order_id'] = sOrder.id
        livraison = super(Netline_livraison, self).create(values)
        livraison.set_waiting()

        receptions = []

        if values['is_laundry'] is True:
            receptions = livraison.reception_laundry_ids
        if values['is_vt'] is True:
            receptions = livraison.reception_vt_ids
        if values['is_pressing'] is True:
            receptions = livraison.reception_pressing_ids
        for reception in receptions:
            for reception_line in reception.receptionline_ids:
                reception_line_livraison_lines = self.env['netline.livraison.line'].search([('reception_line_id', '=', reception_line.id)])
                livraison_line_livred_quantity = 0
                for livraison_line in reception_line_livraison_lines:
                    livraison_line_livred_quantity += livraison_line.to_deliver_quantity
                #"reception line"
                #reception_line
            reception.define_state()
        # for picking in sOrder.picking_ids:
        #     picking.write({'is_laundry': True})

        return livraison


    @api.onchange('reception_laundry_ids')
    def onchange_laundry_id(self):
        livraison_lines = []
        for receptionLaundry in self.reception_laundry_ids:
            #receptionLaundry
            for reception_line in receptionLaundry.receptionline_ids:
                done_qte = 0
                previous_livraison_line = self.env['netline.livraison.line'].search([('reception_line_id', '=', reception_line.id)])
                for pll in previous_livraison_line:
                    done_qte += pll.to_deliver_quantity
                available_quantity = reception_line.quantity - done_qte
                #reception_line.id
                new_line = (0, 0, {'reception_line_id': reception_line.id, 'original_quantity': reception_line.quantity, 'available_quantity': available_quantity, 'to_deliver_quantity': available_quantity})
                if available_quantity > 0:
                    livraison_lines.append(new_line)
        return {'value': {'livraison_lines_ids': livraison_lines}}

    @api.onchange('reception_pressing_ids')
    def onchange_pressing_id(self):
        #'onchange pressing'
        livraison_lines = []
        for reception in self.reception_pressing_ids:

            for reception_line in reception.receptionline_ids:
                done_qte = 0
                previous_livraison_line = self.env['netline.livraison.line'].search([('reception_line_id', '=', reception_line.id)])
                for pll in previous_livraison_line:
                    done_qte += pll.to_deliver_quantity
                available_quantity = reception_line.quantity - done_qte
                new_line = (0, 0, {'reception_line_id': reception_line.id, 'original_quantity': reception_line.quantity, 'available_quantity': available_quantity, 'to_deliver_quantity': available_quantity})
                if available_quantity > 0:
                    livraison_lines.append(new_line)
        return {'value': {'livraison_lines_ids': livraison_lines}}

    def action_cancel(self):
        if self.state == 'ready' or self.state == 'invoiced':
            self.set_cancelled()
        else:
            raise UserError(_("La livraison ne peut pas être annuler car elle est déja facturé"))

    def action_invoice_cancelled(self):
        self.write({'state': 'ready'})

    def action_validate(self):
        for netline_livraison in self:
            if netline_livraison.state == 'ready':
                netline_livraison.sale_order_id.action_validate()
                netline_livraison.write({'state': 'invoiced'})



    @api.onchange('reception_vt_ids')
    def onchange_vt_id(self):
        #"on change vt"
        livraison_lines = []
        for reception in self.reception_vt_ids:
            for reception_line in reception.receptionline_ids:
                done_qte = 0
                previous_livraison_line = self.env['netline.livraison.line'].search(
                    [('reception_line_id', '=', reception_line.id)])
                for pll in previous_livraison_line:
                    done_qte += pll.to_deliver_quantity
                available_quantity = reception_line.quantity - done_qte
                new_line = (0, 0, {'reception_line_id': reception_line.id, 'original_quantity': reception_line.quantity,
                                   'available_quantity': available_quantity, 'to_deliver_quantity': available_quantity})
                if available_quantity > 0:
                    livraison_lines.append(new_line)
        return {'value': {'livraison_lines_ids': livraison_lines}}
