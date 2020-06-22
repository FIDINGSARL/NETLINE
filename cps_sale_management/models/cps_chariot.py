# -*- coding: utf-8 -*-

from odoo import models, fields, api

class CpsChariot(models.Model):
    _name = 'cps.chariot'
    _description = "Liste des chariots "

    numero = fields.Char('Chariot N°',readonly=True)
    name = fields.Char("name", compute="compute_name")
    product_production_id = fields.Many2one("cps.product.production", string="Article")
    qte = fields.Integer('Quantité prévue',readonly=True,compute="compute_quantite")
    qte_reel = fields.Integer('Quantité réelle')
    # poids = fields.Integer('Poids', compute="compute_poids")
    poids = fields.Integer('Poids')
    state = fields.Selection([('draft', 'Brouillon'), ('ready', 'Pret'), ('printed', 'Imprimé')], string='Statut', required=True, default='ready')

    @api.depends('product_production_id')
    def compute_name(self):
        for p in self:
            name = ""
            if p.numero is not False:
                name = name +  p.numero + ' ' + p.product_production_id.product_tmpl_id.client_id.name + ' / ' + p.product_production_id.atelier_id.name
            p.name =  name

    # @api.depends('product_production_id','qte')
    # def compute_poids(self):
    #     for p in self:
    #         poids = 0
    #         if p.product_production_id.poids is not False:
    #             poids = poids + (p.product_production_id.product_tmpl_id.poids*p.qte)
    #         p.poids = poids



    @api.model
    def create(self, vals) :
        #seq = self.env['ir.sequence'].next_by_code('cps.chariot')
        product_chariot = self.env['cps.chariot'].search([('product_production_id', '=', vals['product_production_id'])])
        cps_p= self.env['cps.product.production'].search([('id', '=', vals['product_production_id'])])
        vals['numero']= cps_p.code_article+'-'+str(len(product_chariot)+1)
        return super(CpsChariot, self).create(vals)


    @api.depends('poids','product_production_id')
    @api.onchange('poids')
    def compute_quantite(self):
        for p in self:
            qte = 0
            if p.poids is not False and p.product_production_id.product_tmpl_id.poids is not False  :
                if p.product_production_id.product_tmpl_id.poids != 0 :
                    qte = qte + (p.poids/p.product_production_id.product_tmpl_id.poids)
            p.qte = qte