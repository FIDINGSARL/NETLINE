# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date, datetime, timedelta
from odoo.exceptions import UserError, AccessError
import time
#modules consomation energie
    
class Netline_Consomation(models.Model):
    _name = "netline.consomation"
    global consommation_lines_global
    consommation_lines_global = []
    
    consommation_date = fields.Datetime(String="Date de saisie")
    # consomationline_ids = fields.One2many('netline.consomation.line', "consommation_id", string="Consommations")
    purchase_order_id = fields.Many2one('purchase.order', "Ordre d'achat")
    product_order_name = fields.Char(related="purchase_order_id.name", readonly=True)
    product_id = fields.Many2one('netline.compter', 'Compteur', required=True)
    compteur_initial=fields.Integer(string="Compteur initial", store=True)
    compteur_final=fields.Integer(string="Compteur final")
    image_small = fields.Binary("image_small", attachment=True)
    quantity = fields.Integer(string="Quantité", readonly=True, compute="compute_quantity")
    unite_mesure = fields.Char(related='product_id.product_unit_id.name', string='Unité de Mesure', store=True)

    @api.onchange("product_id")
    def onchange_product_id(self):
        netline_compteur = self.env['netline.consomation'].search([('product_id', '=', self.product_id.id)])
        compteur_ini=0
        for r in netline_compteur:
            compteur_ini = r.compteur_final
        res = {
            'value': {
                'compteur_initial': compteur_ini,
            }
        }
        return res

    def compute_quantity(self):
        for c in self:
            if c.product_id.id is not False:
                if c.product_id.product_type == "incrementiel":
                    c.quantity = c.compteur_initial - c.compteur_final
                else:
                    c.quantity =  c.compteur_final - c.compteur_initial

    def name_get(self):
        res = []
        for rec in self:
            name = rec.create_date
            res.append((rec.id, name))
        return res

    def compute_compteur_initial(self,compteur_id):
        netline_compteur = self.env['netline.consomation'].search([('product_id', '=', compteur_id)])
        compteur_ini=0
        for r in netline_compteur:
            compteur_ini = r.compteur_final
        return compteur_ini

    @api.model
    def create(self, values):
        netline_compteur = self.env['netline.consomation'].search([('product_id', '=', values['product_id'])])
        compteur_ini=0
        for r in netline_compteur:
            compteur_ini = r.compteur_final
        values['compteur_initial']=compteur_ini
        consommation = super(Netline_Consomation, self).create(values)
        return consommation

    def process_verification_consommation(self):
        if datetime.now().hour >= 9:
            netline_compteurs = self.env['netline.compter'].search([])
            yes_date=date.today() - timedelta(1)
            yes_date=yes_date.strftime('%Y-%m-%d')
            for netline_compteur in netline_compteurs:
                netline_conso = self.env['netline.consomation'].search([('product_id', '=', netline_compteur.id)], order='consommation_date desc', limit=1)
                if len(netline_conso)>0:
                    if datetime.strptime(netline_conso.consommation_date, '%Y-%m-%d %H:%M:%S').strftime("%Y-%m-%d")< yes_date:
                        su_id = self.env['res.partner'].search([('email','=', 'odoo@netline.ma')])
                        template_id = self.env['ir.model.data'].get_object_reference('netline', 'verification_saisie_consommation_email_template')[1]
                        template_browse = self.env['mail.template'].browse(template_id)
                        if template_browse:
                            email_to = self.env['hr.employee'].search([('work_email', '=', 'tech@netline.ma')]).work_email
                            values = template_browse.generate_email(su_id.id, fields=None)
                            values['email_to'] = email_to
                            values['email_from'] = su_id.email
                            values['res_id'] = False
                            if not values['email_to'] and not values['email_from']:
                                pass
                            mail_mail_obj = self.env['mail.mail']
                            msg_id = mail_mail_obj.create(values)
                            if msg_id:
                                mail_mail_obj.send(msg_id)
                            if datetime.now().hour==10 or datetime.now().hour==16:
                                email_to = self.env['hr.employee'].search([('work_email', '=', 'hanafi@netline.ma')]).work_email
                                values = template_browse.generate_email(su_id.id, fields=None)
                                values['email_to'] = email_to
                                values['email_from'] = su_id.email
                                values['res_id'] = False
                                if not values['email_to'] and not values['email_from']:
                                    pass
                                mail_mail_obj = self.env['mail.mail']
                                msg_id = mail_mail_obj.create(values)
                                if msg_id:
                                    mail_mail_obj.send(msg_id)
                            return True
