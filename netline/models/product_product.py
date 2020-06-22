# -*- coding: utf-8 -*-
from odoo import models, fields, api

class Netline_laundry_product_product(models.Model):
    _name = 'product.product'
    _inherit = 'product.product'

    product_id = fields.One2many("netline.product", 'product_id')
    is_laundry = fields.Boolean("laundry", default=False)
    is_pressing = fields.Boolean("pressing", default=False)
    is_sale = fields.Boolean("sale", default=False)
    is_netline = fields.Boolean("netline", default=False)
    is_compteur = fields.Boolean("compteur", default=False)
    is_vt = fields.Boolean("Vetement Travail", default=False)
    is_generic = fields.Boolean("Generic", default=False)
    is_achat = fields.Boolean("Achat", default=False)
    category_name = fields.Char(related = "categ_id.name")
    pret_emploi = fields.Boolean("Prêt à l'emploi", default=True)
    dosage = fields.Float('Dosage')
    # code_article = fields.Integer("ID Article")
    # famille_id = fields.Many2one('netline.famille', string="Famille", ondelete='restrict', required=True)
    # sfamille_id = fields.Many2one('netline.sfamille', string="Sous-famille", ondelete='restrict', domain= '[("famille_id", "=", famille_id)]', required=True)
    # categorie_id = fields.Many2one('netline.categorie', string="Catégorie", ondelete='restrict', domain= '[("sfamille_id", "=", sfamille_id)]', required=True)
    reservation_count = fields.Float(
        compute='_compute_reservation_count',
        string='# Sales')

    @api.model
    def create (self, values):
        if 'creationtype' in self.env.context:
            if self.env.context['creationtype'] is not False:
                #self.env.context['creationtype']
                if self.env.context['creationtype'] == 0:
                    values['is_laundry'] = True
                if self.env.context['creationtype'] == 1:
                    values['is_sale'] = True
                if self.env.context['creationtype'] == 2:
                    values['is_compteur'] = True
                if self.env.context['creationtype'] == 3:
                    values['is_generic'] = True
                if self.env.context['creationtype'] == 4:
                    values['is_pressing'] = True
                if self.env.context['creationtype'] == 5:
                    values['is_vt'] = True
                if self.env.context['creationtype'] == 7:
                    values['is_achat'] = True
                values['is_netline'] = True

        return super(Netline_laundry_product_product, self).create(values)


    def name_get(self):
        res = []
        #designation_client, designation, type, couleur
        for rec in self:
            name = rec.get_name()
            res.append((rec.id, name))
        return res
    
    def get_name(self):
        name = ""
        if self.is_laundry is not False:
            if self.categ_id.name is not False:
                name = name + self.categ_id.name + " - "
        if self.name is not False:
            name = name + self.name + " - "
        if len(name) > 0:
            name = name[:-3]
        return name

    @api.onchange('famille_id')
    def onchange_famille_id(self):
        self.sfamille_id=""
        self.categorie_id=""

    @api.onchange('sfamille_id')
    def onchange_sfamille_id(self):
        self.categorie_id=""

    @api.onchange('categorie_id')
    def onchange_categorie_id(self):
        self.id_article = self.env['product.template'].search([('id', '>=', 0)], order='id_article desc', limit=1).id_article+1
        if self.famille_id.code is not False:
            self.default_code=self.famille_id.code
        if self.sfamille_id.code is not False:
            self.default_code =self.default_code+self.sfamille_id.code
        if self.categorie_id.code is not False:
            self.default_code = self.default_code + self.categorie_id.code  + str(self.id_article).zfill(4)


    def _compute_reservation_count(self):
        for product in self:
            domain = [('product_id', '=', product.id),
                      ('state', 'in', ['draft', 'assigned'])]
            reservations = self.env['stock.reservation'].search(domain)
            product.reservation_count = sum(reservations.mapped('product_qty'))


    def action_view_reservations(self):
        self.ensure_one()
        ref = 'netline.action_stock_reservation_tree'
        action_dict = self.env.ref(ref).read()[0]
        action_dict['domain'] = [('product_id', '=', self.id)]
        action_dict['context'] = {
            'search_default_draft': 1,
            'search_default_reserved': 1
            }
        return action_dict
