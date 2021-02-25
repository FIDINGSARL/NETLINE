# # -*- coding: utf-8 -*-
from unittest.case import _AssertRaisesContext

from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError, AccessError


import datetime
class Netline_purchase_order(models.Model):
    _inherit = 'purchase.order'
    
    # reception_id = fields.One2many('netline.reception', 'purchase_order_id', string="receptions")
    is_laundry = fields.Boolean(default=True)

class Netline_purchase_order_line(models.Model):
    _inherit = 'purchase.order.line'

    reception_line_id = fields.Many2one('netline.reception.line', string="reception Ligne")
    is_netline = fields.Boolean(default=False)


class Netline_reception(models.Model):
    _name = "netline.reception"
    _order = "id desc"
    #client
    client_id = fields.Many2one('res.partner', "Client")
    client_name = fields.Char(related='client_id.name')
    atelier = fields.Many2one("res.partner", 'of_atelier_id', domain='[("is_atelier", "=", True)]')
    #list de lignes pour produits quant et traitement
    receptionline_ids = fields.One2many('netline.reception.line', "reception_id", string="Produits")
    product_names = fields.Char("Produits", compute="_compute_product_names", store=True)
    purchase_order_id = fields.Many2one('purchase.order', "Ordre d'achat")
    product_order_name = fields.Char(related="purchase_order_id.name", readonly=True, store=True)

    livraison_ids = fields.One2many('netline.livraison', 'reception_laundry_ids', 'Livraisons laundry')
    livraison_pressing_ids = fields.One2many('netline.livraison', 'reception_pressing_ids', 'Livraisons pressing')
    livraison_vt_ids = fields.One2many('netline.livraison', 'reception_vt_ids', 'Livraisons V.T.')

    n_bon_client = fields.Char("N° Bon Client")
    reception_document= fields.Binary("Bon d'enlèvement", attachment=True)
    state = fields.Selection(string="Etat de la réception", selection=[('cancelled', 'Annulé'),
                                                                       ('draft', 'Enlevé'),
                                                                       ('received', 'En préparation'),
                                                                       ('in_progress', 'En production'),
                                                                       ('ready', 'Prêt a livrer'),
                                                                       ('partial_delivred', 'Livré partiellement'),
                                                                       ('delivred', 'Soldé')])

    # reception_avoir_ids = fields.One2many('netline.reception.avoir', 'reception_id')
    is_laundry= fields.Boolean(default=False)
    is_pressing = fields.Boolean(default=False)
    is_vt = fields.Boolean(default=False)
    n_porteur = fields.Char(string = "Numéro Porteur", store=False)

    date_reception = fields.Datetime("Date", required=True)
    # pressing_product_selection_ids = fields.One2many("netline.pressing_product_selection_helper", "reception_id")
    n_chambre = fields.Char(string = "Numéro de chambre")

    delivred_quantity = fields.Integer(compute="_compute_delivred_quantity", readonly=True)
    quality_quantity = fields.Integer(compute="_compute_quality_quantity", readonly=True)
    original_quantity = fields.Integer(compute="_compute_original_quantity", readonly=True)
    available_quantity = fields.Integer(compute="_compute_available_quantity", readonly=True)

    def _compute_original_quantity(self):
        for s in self:
            original_quantity = 0
            for reception_line in s.receptionline_ids:
                original_quantity += reception_line.quantity
            s.original_quantity = original_quantity


    def _compute_available_quantity(self):
        for s in self:
            original_quantity = 0
            for reception_line in s.receptionline_ids:
                original_quantity += reception_line.quantity
            delivred_quantity = 0
            for reception_line in s.receptionline_ids:
                delivred_quantity += (reception_line.delivered_quantity)
                # delivred_quantity += (reception_line.delivered_quantity+reception_line.quality_quantity)
            s.available_quantity = original_quantity - delivred_quantity


    def _compute_delivred_quantity(self):
        for s in self:
            delivred_quantity = 0
            for reception_line in s.receptionline_ids:
                delivred_quantity += reception_line.delivered_quantity
            s.delivred_quantity = delivred_quantity


    def _compute_quality_quantity(self):
        quality_quantity = 0
        for reception_line in self.receptionline_ids:
            quality_quantity += reception_line.quality_quantity
        self.quality_quantity = quality_quantity



    def name_get(self):
        res = []
        #designation_client, designation, type, couleur
        for rec in self:
            products = ""
            if not rec.product_order_name :
                name = ""
            else:
                date = rec.create_date
                if rec.date_reception is not False:
                    date = rec.date_reception
                name = rec.product_order_name + ' | ' + rec.n_bon_client + ' | ' + str(date) #+ ' | ' + products
            res.append((rec.id, name))
        return res



    @api.model
    def testadd(self, values):
        for reception in values:
            self.env['netline.reception'].create(reception)



    # def action_make_livraison(self):
    #     if self.is_textil:
    #         livraison_lines=[]
    #         netline_livraison = self.env['netline.livraison'].create({
    #             'client_id': self.client_id.id,
    #             'atelier_id': self.atelier.id,
    #             'is_textil': True,
    #             'date_livraison': datetime.datetime.now(),
    #             'reception_textil_ids': [(4, self.id)]
    #         })
    #         livraison_lines = []
    #         for reception_line in self.receptionline_ids:
    #             done_qte = 0
    #             previous_livraison_line = self.env['netline.livraison.line'].search([('reception_line_id', '=', reception_line.id)])
    #             for pll in previous_livraison_line:
    #                 done_qte += pll.to_deliver_quantity
    #             previous_retour_line = self.env['netline.retour.line'].search([('reception_line_id', '=', reception_line.id)])
    #             for prl in previous_retour_line:
    #                 done_qte += prl.to_return_quantity
    #             available_quantity = reception_line.quantity - done_qte
    #             #reception_line.id
    #             new_line = (0, 0, {'reception_line_id': reception_line.id, 'original_quantity': reception_line.quantity, 'available_quantity': available_quantity, 'to_deliver_quantity': 0})
    #             if available_quantity > 0:
    #                 livraison_lines.append(new_line)
    #         netline_livraison.write({'livraison_lines_ids': livraison_lines})
    #         is_textil = True
    #         ac = self.env['ir.model.data'].xmlid_to_res_id('netline.netline_livraison_form_view', raise_if_not_found=True)
    #         result = {
    #             'name': "netline.livraison",
    #             'view_type': 'form',
    #             'view_id': ac,
    #             'res_id': netline_livraison.id,
    #             'res_model': 'netline.livraison',
    #             'type': 'ir.actions.act_window',
    #             'view_mode': 'form',
    #             'domain': {'is_textil': is_textil},
    #             'context' : {'is_textil': is_textil}
    #         }
    #         return result
    #     elif self.is_echantillon:
    #             livraison_lines = []
    #             netline_livraison = self.env['netline.livraison'].create({
    #                 'client_id': self.client_id.id,
    #                 'atelier_id': self.atelier.id,
    #                 'is_echantillon': True,
    #                 'date_livraison': datetime.datetime.now(),
    #                 'reception_echantillon_ids': [(4, self.id)]
    #             })
    #             livraison_lines = []
    #             for reception_line in self.receptionline_ids:
    #                 done_qte = 0
    #                 previous_livraison_line = self.env['netline.livraison.line'].search(
    #                     [('reception_line_id', '=', reception_line.id)])
    #                 for pll in previous_livraison_line:
    #                     done_qte += pll.to_deliver_quantity
    #                 previous_retour_line = self.env['netline.retour.line'].search(
    #                     [('reception_line_id', '=', reception_line.id)])
    #                 for prl in previous_retour_line:
    #                     done_qte += prl.to_return_quantity
    #                 available_quantity = reception_line.quantity - done_qte
    #                 # reception_line.id
    #                 new_line = (0, 0,
    #                             {'reception_line_id': reception_line.id, 'original_quantity': reception_line.quantity,
    #                              'available_quantity': available_quantity, 'to_deliver_quantity': 0})
    #                 if available_quantity > 0:
    #                     livraison_lines.append(new_line)
    #             netline_livraison.write({'livraison_lines_ids': livraison_lines})
    #             is_echantillon = True
    #             ac = self.env['ir.model.data'].xmlid_to_res_id('netline.netline_livraison_form_view',
    #                                                            raise_if_not_found=True)
    #             result = {
    #                 'name': "netline.livraison",
    #                 'view_type': 'form',
    #                 'view_id': ac,
    #                 'res_id': netline_livraison.id,
    #                 'res_model': 'netline.livraison',
    #                 'type': 'ir.actions.act_window',
    #                 'view_mode': 'form',
    #                 'domain': {'is_echantillon': is_echantillon},
    #                 'context': {'is_echantillon': is_echantillon}
    #             }
    #             return result
    #     else:
    #         raise UserError(_("Cette fonctionnalité est accessible uniquement dans le module textil"))

    def action_make_livraison(self):
        is_laundry = False
        is_vt = False
        is_pressing = False

        if self.is_laundry:
            is_laundry = True
            netline_livraison = self.env['netline.livraison'].create({
                'client_id': self.client_id.id,
                'atelier_id': self.atelier.id,
                'is_laundry': self.is_laundry,
                'is_vt': self.is_vt,
                'is_pressing': self.is_pressing,
                'date_livraison': datetime.datetime.now(),
                'reception_laundry_ids': [(4, self.id)],
            })
        elif self.is_vt:
            is_vt = True
            netline_livraison = self.env['netline.livraison'].create({
                'client_id': self.client_id.id,
                'atelier_id': self.atelier.id,
                'is_laundry': self.is_laundry,
                'is_vt': self.is_vt,
                'is_pressing': self.is_pressing,
                'date_livraison': datetime.datetime.now(),
                'reception_vt_ids': [(4, self.id)],
            })
        elif self.is_pressing:
            is_pressing = True
            netline_livraison = self.env['netline.livraison'].create({
                'client_id': self.client_id.id,
                'atelier_id': self.atelier.id,
                'is_laundry': self.is_laundry,
                'is_vt': self.is_vt,
                'is_pressing': self.is_pressing,
                'date_livraison': datetime.datetime.now(),
                'reception_pressing_ids': [(4, self.id)]
            })

        livraison_lines = []
        for reception_line in self.receptionline_ids:
            done_qte = 0
            previous_livraison_line = self.env['netline.livraison.line'].search([('reception_line_id', '=', reception_line.id)])
            for pll in previous_livraison_line:
                done_qte += pll.to_deliver_quantity
            available_quantity = reception_line.quantity - done_qte
            #reception_line.id
            new_line = (0, 0, {'reception_line_id': reception_line.id, 'original_quantity': reception_line.quantity, 'available_quantity': available_quantity, 'to_deliver_quantity': 0})
            if available_quantity > 0:
                livraison_lines.append(new_line)
        netline_livraison.write({'livraison_lines_ids': livraison_lines})
        ac = self.env['ir.model.data'].xmlid_to_res_id('netline.netline_livraison_form_view', raise_if_not_found=True)

        result = {
            'name': "netline.livraison",
            'view_type': 'form',
            'view_id': ac,
            'res_id': netline_livraison.id,
            'res_model': 'netline.livraison',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'domain': {'is_laundry' : is_laundry, 'is_vt': is_vt, 'is_pressing': is_pressing},
            'context' : {'is_laundry' : is_laundry, 'is_vt': is_vt, 'is_pressing': is_pressing}
        }
        return result

    @api.onchange("client_id")
    def on_change_client_id(self):
        if self._origin.id is not False:
            return
        if self.client_id.id is False:
            return
        client_netline_products = self.env['netline.product'].search([('client_id', '=', self.client_id.id),]).sorted(key=lambda p: p.n_ligne)
        reception_lines_values = []
        if self.env.context['is_laundry'] is 1:
            for netline_product in client_netline_products:
                line_value = (0,0, {'product_id': netline_product.id, 'quantity': 0, 'traitement': 'lavage'})
                reception_lines_values.append(line_value)
            return {'value': {'receptionline_ids': reception_lines_values}}
        return

    @api.onchange("n_chambre")
    def onchange_n_chambre(self):
        #"numero chambre changed"
        if self.client_id is False or self.client_id is None:
            return {
                'warning': {
                    'title': "Message d'erreur",
                    'message': "Sélectionnez un client",
                }
            }
        pressing_products = self.env["netline.pressing_product"].search([("client_id", "=", self.client_id.id)]).sorted(key=lambda p: p.n_ligne)
        new_lines = []
        for pressing_product in pressing_products:
            new_line = (0, 0, {"n_chambre": self.n_chambre, "product_pressing_id": pressing_product.id, "traitement": 'lavage',
                               'quantity': 0})
            new_lines.append(new_line)

        return {'value': {'pressing_product_selection_ids': new_lines}}


    # @api.onchange("pressing_product_selection_ids")
    # def onchange_pressing_product_selection(self):
    #     #self.n_chambre
    #     new_reception_line_ids = []
    #     for reception_line in self.receptionline_ids:
    #         new_line = (0, 0, {'n_chambre': reception_line.n_chambre, 'nom_porteur': reception_line.nom_porteur,
    #                            'product_pressing_id': reception_line.product_pressing_id.id, 'traitement': reception_line.traitement,
    #                            'quantity':reception_line.quantity})
    #
    #         new_reception_line_ids.append(new_line)
    #     for product in self.pressing_product_selection_ids:
    #         new_line = (0, 0, {'n_chambre': self.n_chambre, 'nom_porteur': "", 'product_pressing_id': product.id,
    #                                        'traitement': 'lavage', 'quantity': 1})
    #         new_reception_line_ids.append(new_line)
    #     #type(self.pressing_product_selection_ids)
    #     return {'value': {'receptionline_ids': new_reception_line_ids}}

    def action_add_pressing_lines(self):
        new_pressing_reception_lines = []
        #"action_add_pressing_lines"
        #self.receptionline_ids
        for reception_line in self.receptionline_ids:
            new_line = (1, reception_line.id, {})
            new_pressing_reception_lines.append(new_line)
        for line in self.pressing_product_selection_ids:
            #line
            new_line = (0,0, {"n_chambre": self.n_chambre, "product_pressing_id": line.product_pressing_id.id, "traitement": line.traitement, 'quantity': line.quantity})
            if line.quantity > 0:
                new_pressing_reception_lines.append(new_line)
        #new_pressing_reception_lines
        self.receptionline_ids = new_pressing_reception_lines
        return False


    @api.onchange("n_porteur")
    def onchange_nporteur(self):
        if self.n_porteur is False:
            return
        porteur = self.env['netline.porteur'].search([('n_porteur', '=', self.n_porteur), ('client_id', '=', self.client_id.id)])
        #self.client_id
        #self.n_porteur
        #porteur
        reception_line_new_values = []
        for reception_line in self.receptionline_ids:
            if type(reception_line.id) is not 'int':
                try:
                    quantity = reception_line[0]['quantity']
                except:
                    quantity = 0
                new_line = (0, 0, {'n_porteur': reception_line.n_porteur, 'product_vt_id': reception_line.product_vt_id.id,
                                   'quantity': quantity,
                                   'traitement': reception_line.traitement})
                reception_line_new_values.append(new_line)
            else:
                try:
                    quantity = reception_line[2]['quantity']
                except:
                    quantity = 0
                new_line = (0, 0, {'n_porteur': reception_line.n_porteur, 'product_vt_id': reception_line.product_vt_id.id,
                                   'quantity': quantity,
                                   'traitement': reception_line.traitement})
                reception_line_new_values.append(new_line)


        if len(porteur) is 0:
            #"creating line porteur non existant"
            new_line = (0, 0, {'n_porteur': self.n_porteur,'product_vt_id': None, 'quantity': 0, 'traitement': 'lavage'})
            reception_line_new_values.append(new_line)
        elif len(porteur) is 1:
            #"creating line with porteur"
            for article in porteur.product_ids:
                new_line = (0, 0, {'n_porteur': self.n_porteur ,'product_vt_id': article.id, 'quantity': 0,
                                   'traitement': 'lavage'})
                reception_line_new_values.append(new_line)
        return {'value': {'receptionline_ids': reception_line_new_values}}


    @api.onchange("receptionline_ids")
    def onchangetest(self):
        for reception_line in self.receptionline_ids:
            if reception_line.n_porteur is "":
                if self.n_porteur is not False and self.n_porteur is not "":
                    reception_line.n_porteur = self.n_porteur

    @api.model
    def create(self, values):
        #get netline_reception_lines values (traitement, quantity)
        print('create----')
        values['state'] = 'draft'
        values['is_laundry'] = False
        values['is_pressing'] = False
        values['is_vt'] = False
        try:
            if self.env.context['is_laundry'] == 1:
                values['is_laundry']=True
            if self.env.context['is_pressing'] == 1:
                values['is_pressing']=True
            if self.env.context['is_vt'] == 1:
                values['is_vt']=True
        except:
            #request from mobile
            values['is_laundry'] = True
            pass
        #todo use currency of client
        pOrder = self.env['purchase.order'].create({
            'picking_type_id': 2,
            'company_id': self.env.user.company_id.id,
            'partner_id': values['client_id'],
            'date_order': values['date_reception'],
            'date_planned': values['date_reception'],
            'currency_id': self.env.user.company_id.currency_id.id,
            'is_netline': True
        })
        #create purchase order with the informations given
        values['purchase_order_id'] = pOrder.id
        #delete reception lines with quantity = 0
        if values['receptionline_ids'] is not False:
            new_receptionline_ids = []
            if values['is_laundry'] is True or values['is_pressing'] is True:
                for reception_line in values['receptionline_ids']:
                    if reception_line[2].get('quantity') != 0:
                        new_receptionline_ids.append(reception_line)
            elif values['is_vt'] is True:
                for reception_line in values['receptionline_ids']:
                    #voir si le numero porteur contient les articles dans la liste
                    n_porteur = reception_line[2]['n_porteur']
                    #"befor porteur creation"
                    #values['client_id']
                    #n_porteur
                    porteur = self.env['netline.porteur'].search([("n_porteur", "=", n_porteur), ("client_id", "=", values['client_id'])])
                    #porteur
                    if len(porteur) is 0:
                        #on cree le porteur
                        porteur = self.env["netline.porteur"].create({
                            'n_porteur': n_porteur,
                            'client_id': values['client_id']
                        })
                for reception_line in values['receptionline_ids']:
                    n_porteur = reception_line[2]['n_porteur']
                    product_vt_id = reception_line[2]['product_vt_id']
                    porteur = self.env['netline.porteur'].search([("n_porteur", "=", n_porteur), ("client_id", "=" ,values['client_id'])])
                    if len(porteur) > 1:
                        porteur = porteur[0]
                    porteur_product_ids = []
                    for p in porteur.product_ids:
                        porteur_product_ids.append(p.id)
                    article_test = self.env['netline.vt_product'].search([("id", "=", product_vt_id)])
                    if article_test.id not in porteur_product_ids:
                        porteur_product_ids.append(article_test.id)
                    new_line_value = (0,0, {'product_vt_id': product_vt_id, 'quantity': reception_line[2]['quantity'],
                                            'traitement': reception_line[2]['traitement'],
                                            'n_porteur': n_porteur})
                    new_receptionline_ids.append(new_line_value)
                    porteur.write({'product_ids': [(6, True, porteur_product_ids)]})

            values['receptionline_ids'] = new_receptionline_ids
            picking = self.env['stock.picking'].search([('origin', '=', pOrder.name)])
            picking.write({'is_laundry': True})
        # pOrder.button_confirm()
        reception = super(Netline_reception, self).create(values)

        return reception

    def action_cancel(self):

        netline_reception_avoir_lines = []
        for reception_line in self.receptionline_ids:
            #reception_line.product_id
            new_line = (0, 0, {'quantity': reception_line.quantity, 'traitement': reception_line.traitement,
                               'product_id': reception_line.product_id.id,
                               'product_vt_id': reception_line.product_vt_id.id,
                               'product_pressing_id': reception_line.product_pressing_id.id,
                               'n_porteur': reception_line.n_porteur,
                               'nom_porteur': reception_line.nom_porteur, 'n_chambre': reception_line.n_chambre})
            netline_reception_avoir_lines.append(new_line)
            livraison_lines = self.env['netline.livraison.line'].search([('reception_line_id', "=", reception_line.id)])
            for line in livraison_lines:
                line.unlink()
        try:
            for reception in self:
                #self.env['purchase.order.line'].search([('order_id', '=', reception.purchase_order_id.id)]).unlink()
                self.env['purchase.order'].search([('id', '=', reception.purchase_order_id.id)]).button_cancel()
                #self.env['purchase.order'].search([('id', '=', reception.purchase_order_id.id)]).unlink()
                #self.env['stock.picking'].search([('purchase_id', '=', reception.purchase_order_id.id)]).unlink()
        except:
            "Error while deleting"
        self.write({'state': 'cancelled'})
        #for rline in self.receptionline_ids:
        #    rline.unlink()


    def unlink(self):
        raise UserError(_("Les réceptions ne peuvent pas être supprimé, Cliquez sur annuler la réception pour l'annuler"))



    def write(self, values):
        if 'client_id' in values:
            if len(self.receptionline_ids)>0:
                raise UserError(
                    _("Vous ne pouvez pas changer le client !"))
            else:
                self.purchase_order_id.write({'partner_id': values['client_id']})

        if 'date_reception' in values:
            self.purchase_order_id.write({'date_order': values['date_reception'],
                                          'date_planned': values['date_reception']})

        reception=super(Netline_reception, self).write(values)

        return reception

    def action_validate(self):
        #self.purchase_order_id.button_confirm()
        self.write({'state': 'ready'})
        return True

    def action_add_reception_line(self):
        print("")

    def set_delivred(self):
        # for picking in self.purchase_order_id.picking_ids:
        #     picking.do_transfer()
        self.write({'state': 'delivred'})

    def set_partial_delivred(self):
        self.write({'state': 'partial_delivred'})

    def set_ready(self):
        self.write({'state': 'ready'})

    def define_state(self):
        print('define state')
        delivered = False
        partial_delivered = False
        qty_delivered = 0
        qty_received = 0
        for reception_line in self.receptionline_ids.filtered(lambda t: t.reception_id.state != 'cancelled'):
            qty_received+= reception_line.quantity
            for livraison_line in reception_line.livraison_line_ids:
                qty_delivered+=livraison_line.to_deliver_quantity
        if qty_delivered > 0:
            delivered = True
        if qty_delivered < qty_received and qty_delivered>0:
            partial_delivered = True
        qty_delivered = 0
        qty_quality = 0
        qty_quality = 0
        for reception_line in self.receptionline_ids.filtered(lambda t: t.reception_id.state != 'cancelled'):
            qty_delivered = 0
            qty_quality = 0
            for livraison_line in reception_line.livraison_line_ids:
                qty_delivered+=livraison_line.to_deliver_quantity
            reception_line.write(
                {'delivered_quantity': qty_delivered, 'available_quantity': reception_line.quantity - qty_delivered, 'quality_quantity': qty_quality})

        if delivered:
            if partial_delivered:
                self.set_partial_delivred()
            else:
                self.set_delivred()
        else:
            self.set_ready()