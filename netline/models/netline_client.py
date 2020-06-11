# # -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions
import datetime
        
class Netline_clients(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    product_ids = fields.One2many('netline.product', 'client_id')
    latitude = fields.Float('latitude', digits=(3, 8))
    longitude = fields.Float('longitude', digits=(3, 8))
    # liste_prix_ids = fields.One2many('netline.liste_prix', 'client_id')
    liste_pressing_ids = fields.One2many('netline.pressing_product', 'client_id')
    liste_vt_ids = fields.One2many('netline.vt_product', 'client_id')
    reception_ids = fields.One2many('netline.reception', 'client_id', domain=[('is_laundry', '=', True),('state', 'in', ('ready','partial_delivred'))])
    reception_vt_ids = fields.One2many('netline.reception', 'client_id', domain=[('is_vt', '=', True),('state', 'in', ('ready','partial_delivred'))])
    reception_pressing_ids = fields.One2many('netline.reception', 'client_id', domain=[('is_pressing', '=', True),('state', 'in', ('ready','partial_delivred'))])
    livraison_ids = fields.One2many('netline.livraison', 'client_id', domain=[('is_laundry', '=', True)])
    livraison_vt_ids = fields.One2many('netline.livraison', 'client_id', domain=[('is_vt', '=', True)])
    livraison_pressing_ids = fields.One2many('netline.livraison', 'client_id', domain=[('is_pressing', '=', True)])
    nom_commercial = fields.Char('Enseigne Client')
    clientprst_id = fields.One2many('res.partner', 'typeprestation_ids', string="Client")
    type_client=fields.Selection([('permanent_contrat', 'Permanent contrat'), ('permanent_bc', 'Permanent B.C.'), ('occasionnel_bc', 'Occasionnel B.C.')], string='Type Client', default='permanent_contrat')
    typeprestation_ids = fields.Many2many('netline.prestation_client','clientprst_id',string="Prestation")
    is_client = fields.Boolean("is_client", default=False)
    is_atelier = fields.Boolean("is_atelier", default=False)
    numero_ice= fields.Char("Numéro ICE")
    numero_rc= fields.Char("Numéro RC")
    code_client =fields.Char("Code Client")
    plafond_credit = fields.Integer("Plafond crédit")
    caution = fields.Integer("Caution")
    dossier_complet = fields.Boolean("Dossier Complet", default=False)
    devise = fields.Many2one("res.currency","Devise")

    total_entree = fields.Integer("Total reçu", compute="_compute_totaux")
    total_sortie = fields.Integer("Total sortie")
    total_encours = fields.Integer("Total encours")
    total_detachage = fields.Integer("Total détachage")

    def action_creer_reception_laundry(self):
        netline_reception = self.env['netline.reception'].create({
            'client_id': self.id,
            'is_laundry': True,
            'date_reception': datetime.datetime.now(),
            'receptionline_ids':False
        })
        client_netline_products = self.env['netline.product'].search([('client_id', '=', self.id),]).sorted(key=lambda p: p.n_ligne)
        reception_lines_values = []

        for netline_product in client_netline_products:
            line_value = (0,0, {'product_id': netline_product.id, 'quantity': 0, 'traitement': 'lavage'})
            reception_lines_values.append(line_value)
        print ('reception lines', reception_lines_values)
        netline_reception.write({'receptionline_ids': reception_lines_values})
        # netline_reception.receptionline_ids = reception_lines_values

        ac = self.env['ir.model.data'].xmlid_to_res_id('netline.netline_reception_form_view', raise_if_not_found=True)

        result = {
            'name': "netline.reception",
            'view_type': 'form',
            'view_id': ac,
            'res_id': netline_reception.id,
            'res_model': 'netline.reception',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'domain': {'is_laundry' : True},
            'context': {'is_laundry':1, 'is_pressing':0, 'is_vt':0}
        }
        return result

    def action_creer_reception_pressing(self):
        netline_reception = self.env['netline.reception'].create({
            'client_id': self.id,
            'is_pressing': True,
            'date_reception': datetime.datetime.now(),
            'receptionline_ids':False
        })


        ac = self.env['ir.model.data'].xmlid_to_res_id('netline.netline_reception_form_view', raise_if_not_found=True)

        result = {
            'name': "netline.reception",
            'view_type': 'form',
            'view_id': ac,
            'res_id': netline_reception.id,
            'res_model': 'netline.reception',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'domain': {'is_pressing' : True},
            'context': {'is_laundry':0, 'is_pressing':1, 'is_vt':0}
        }
        return result

    def action_creer_reception_vt(self):
        netline_reception = self.env['netline.reception'].create({
            'client_id': self.id,
            'is_vt': True,
            'date_reception': datetime.datetime.now(),
            'receptionline_ids':False
        })


        ac = self.env['ir.model.data'].xmlid_to_res_id('netline.netline_reception_form_view', raise_if_not_found=True)

        result = {
            'name': "netline.reception",
            'view_type': 'form',
            'view_id': ac,
            'res_id': netline_reception.id,
            'res_model': 'netline.reception',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'domain': {'is_pressing' : True},
            'context': {'is_laundry':0, 'is_pressing':0, 'is_vt':1}
        }
        return result

    def _compute_totaux(self):
        for p in self:
            totalEntree = 0
            totalSortie = 0
            totalEncours = 0
            totalDetachage = 0
            entrees = self.env['netline.reception'].search(['|', ("state", "=", "partial_delivred"),("state", "=", "ready"), ('client_id', '=', p.id)])
            for entree in entrees:
                for entree_line in entree.receptionline_ids:
                    totalEntree += entree_line.quantity
                    totalSortie+= entree_line.delivered_quantity
                    totalEncours += entree_line.available_quantity
            p.total_entree = totalEntree
            p.total_sortie = totalSortie
            p.total_encours = totalEncours
            p.total_detachage = totalDetachage


    def copy(self, default=None):
        default = dict(default or {})
        default.update({
            'company_type': 'company'
        })
        new_partner = super(Netline_clients, self).copy(default)
        product_ids = []
        for p in self.product_ids:
            created_product = p.copy()
            product_ids.append(created_product.id)
        new_partner.product_ids = product_ids

        liste_pressing_ids = []
        for p in self.liste_pressing_ids:
            created_product = p.copy()
            liste_pressing_ids.append(created_product.id)
        new_partner.liste_pressing_ids = liste_pressing_ids

        liste_vt_ids = []
        for p in self.liste_vt_ids:
            created_product = p.copy()
            liste_vt_ids.append(created_product.id)
        new_partner.liste_vt_ids = liste_vt_ids

        return new_partner

    @api.model
    def create(self, values):
        netline_compter = self.env['res.partner'].search([('name', 'ilike', values.get('name'))])
        if len(netline_compter) == 0 :
            if 'creationtype' in self.env.context:
                if self.env.context['creationtype'] is not False:
                    if self.env.context['creationtype'] == 0:
                        values['is_client'] = True
                    if self.env.context['creationtype'] == 1:
                        values['is_atelier'] = True
            listePrix = super(Netline_clients, self).create(values);
            return listePrix
        else:
            raise exceptions.ValidationError("Ce client existe déjà !")

                #
    # def name_get(self):
    #     res = []
    #     #designation_client, designation, type, couleur
    #     for rec in self:
    #         products = ""
    #         if not rec.product_order_name :
    #             name = ""
    #         else:
    #             date = rec.create_date
    #             if rec.date_reception is not False:
    #                 date = rec.date_reception
    #             name = rec.product_order_name + ' | ' + date + ' | ' + products
    #         res.append((rec.id, name))
    #     return res

    
class Netline_prestations_clients(models.Model):
    _name= 'netline.prestation_client'
    
    clientprst_id = fields.One2many('res.partner','typeprestation_ids', string="Client")
    # bcprst_id = fields.One2many('purchase.requisition', 'typeprestation_ids', string="Prestation")
    type_prestation_value = fields.Selection([('Laundry linge', 'Laundry linge'), ('Laundry V.T.', 'Laundry V.T.'), ('Location linge', 'Location linge'), ('Location V.T.', 'Location V.T.'), ('Pressing', 'Pressing'), ('Textile industrie', 'Textile industrie'), ('Location & Entretien linge', 'Location & Entretien linge'), ('Location & Entretien V.T.', 'Location & Entretien V.T.'), ('Vente', 'Vente')], string='Prestation', required=True, default='Laundry linge')
    

    def name_get(self):
        res = []
        for rec in self:
            name = rec.type_prestation_value
            res.append((rec.id, name))
        return res


class Netline_affaire(models.Model):
    _name = 'netline.affaire'

    clientprst_id = fields.One2many('res.partner', 'typeprestation_ids', string="Client")
    name= fields.Char('Affaire')


    def name_get(self):
        res = []
        for rec in self:
            name = rec.name
            res.append((rec.id, name))
        return res