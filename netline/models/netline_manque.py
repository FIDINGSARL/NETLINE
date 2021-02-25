# -*- coding: utf-8 -*-
from odoo import models, api, fields, _
from docutils.nodes import line
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, copy
from datetime import date
 
class Netline_manque(models.Model):
    _name = 'netline.manque'
    manque_lines_ids = fields.One2many('netline.manque.line', 'manque_line_id', string="Produits")
    date_manque= fields.Datetime("Date Manque", readyonly=True)
    client_id = fields.Many2one('res.partner', "Client", domain='[("reception_ids", "!=", False)]')

    @api.model
    def create(self, values):
        return super(Netline_manque, self).create(values)

    @api.onchange("client_id")
    def onchange_client_id(self):
        if self.client_id.id is not False:
            receptions = self.env['netline.reception'].search([('state', '=', 'partial_delivred'),('client_id', '=', self.client_id.id)])
        else:
            receptions = self.env['netline.reception'].search([('state', '=', 'partial_delivred')])
        self.date_manque=date.today()
        manque_line_new_values = []
        for reception in receptions:
            for reception_line in reception.receptionline_ids:
                product_name=""
                if reception_line.product_id.id is not False:
                    product_name = reception_line.product_id.name
                elif reception_line.product_textil_id.id is not False: _id.name
                elif reception_line.product_echantillon_id.id is not False:
                    if reception_line.product_echantillon_id.solde == False:
                        product_name = reception_line.product_echantillon_id.name
                elif reception_line.product_vt_id.id is not False:
                    product_name = reception_line.product_vt_id.name
                elif reception_line.product_pressing_id.id is not False:
                    product_name = reception_line.product_pressing_id.name
                if product_name!='':
                    new_line = (0, 0, {'client_name': reception.client_name, 'n_bon_entree': reception.product_order_name,
                                       'n_bon_client': reception.n_bon_client,
                                       'date_bon': reception.date_reception,
                                       'designation_article': product_name,
                                       'quantity_received': reception_line.quantity,
                                       'quantity_remaining': reception_line.available_quantity,
                                       'quantity_delivered': reception_line.quantity - reception_line.available_quantity})
                    if reception_line.available_quantity > 0:
                        manque_line_new_values.append(new_line)
        print('manque values-------------------', manque_line_new_values)
        #manque_line_new_values
        return {'value': {'manque_lines_ids': manque_line_new_values}}

class Netline_manque_line(models.Model):
    _name = 'netline.manque.line'
    _order = 'client_name asc'
    manque_line_id = fields.Many2one('netline.manque', 'manque_lines_ids')
    client_name = fields.Char('Client')
    n_bon_entree = fields.Char('N° Bon')
    n_bon_client = fields.Char('N° Bon Client')
    date_bon=fields.Datetime('Date Bon')
    designation_article = fields.Char('Désignation')
    quantity_received = fields.Integer("Quantité reçue")
    quantity_delivered = fields.Integer("Quantité livrée")
    quantity_remaining = fields.Integer("Reste a livrer")

    @api.model
    def create(self, values):
        print ("create---------------------------------------", values)
        manques = super(Netline_manque_line, self).create(values)
        return manques
