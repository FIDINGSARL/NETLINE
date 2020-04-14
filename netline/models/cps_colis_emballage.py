# -*- coding: utf-8 -*-

from odoo import models, fields, api

class CpsColisEmballage(models.Model):
    _name = 'cps.colis.emballage'
    _description = "Liste des colis d'emballage"



    product_product_id = fields.Many2one("product.product", string="Article")
    qte = fields.Float('Quantité à emballer')
    qte_emballer = fields.Float('Quantité / colis')
    colis_details = fields.One2many('cps.colis.emballage.lines', 'colis_id', 'Détail des colis')
    # qte_disponible = fields.Float(related='product_id.qty_available', string='Quantité Disponible')
    # parametres_id = fields.Many2one("cps.colis.emballage.setting", string="paramètres")
    # source = fields.Char(related='parametres_id.stock_location_source.name', string='Emplacement source')
    # destination = fields.Char(related='parametres_id.stock_location_destination.name', string='Emplacement destination')

    # @api.model
    # def create(self, values):
    #     last_setting = self.env['cps.colis.emballage.setting'].search([("stock_location_source", "!=", ""),("stock_location_destination", "!=", "")], order='id desc', limit=1)
    #     values['parametres_id'] = last_setting.id
    #     colis_emballage = super(CpsColisEmballage, self).create(values)
    #     return colis_emballage

    # def action_creer_colis(self):
        # partner_location = self.env['stock.location'].search([('usage', '=', 'customer')])
        # stock_picking = self.env['stock.picking'].create({
        #     'picking_type_id': self.parametres_id.stock_picking_type_id.id,
        #     'move_type': 'direct',
        #     'location_id':self.parametres_id.stock_location_source.id,
        #     'location_dest_id': self.parametres_id.stock_location_destination.id,
        #     # 'n_bon_client': self.n_bon_client,
        #     # 'partner_id': self.partner_id.id,
        #     'move_ids_without_package': [(0, 0, {
        #         'product_id': self.product_id.id,
        #         'description_picking': self.product_id.name,
        #         'name': self.product_id.name,
        #         # 'n_bon_client': self.n_bon_client,
        #         'product_uom_qty': self.qte,
        #         # 'product_echantillon_reception_id': self.product_id.echantillon_ids.id,
        #         'product_uom': self.product_id.uom_id.id,
        #         # 'qty_done' : self.qte_emballer,
        #         'is_echantillon': True,
        #         # 'is_commande': False
        #     })]
        # })
        # stock_picking.action_confirm()
        # stock_picking.action_assign()

       # faire les colis
       #  qte = self.qte
       #  totalQtcolis=0
       #  sequence = 1
       #  colis =[]
       #  while True:
       #      reste =  qte - totalQtcolis
       #      if(reste >= self.qte_emballer ) :
       #          totalQtcolis += self.qte_emballer
       #          colis = (0,0, {'qte': self.qte_emballer, 'sequence': sequence, 'qte_emballer' : self.qte_emballer})
       #          # stock_picking.move_line_ids[0].write({'qty_done': self.qte_emballer})
       #          # stock_picking.put_in_pack()
       #      else :
       #          totalQtcolis += reste
       #          colis = (0,0, {'qte': reste, 'sequence': sequence, 'qte_emballer' : self.qte_emballer})
       #          # stock_picking.move_line_ids[0].write({'qty_done': reste})
       #          # stock_picking.put_in_pack()
       #      if (totalQtcolis >= self.qte):
       #          break
       #      colis.append(colis)
       #      sequence+=1

        # self.colis_details = colis
        # valider le transfert en interne
        # stock_picking.button_validate()
        # result = {
        #     'name': "stock.picking",
        #     'view_type': 'form',
        #     'res_model': 'stock.picking',
        #     'res_id': stock_picking.id,
        #     'type': 'ir.actions.act_window',
        #     'view_mode': 'form',
        #     'traget':'new'
        # }
        # return result

    @api.model
    def create(self, values):
        colis_emballage = super(CpsColisEmballage, self).create(values)
        if 'qte' in values:
            sequence = 1
            colis = []
            reste=values['qte']
            while True:
                if reste >= values['qte_emballer']:
                    colis.append((0, 0, {'qte': values['qte'], 'sequence': sequence, 'qte_emballer': values['qte_emballer']}))
                else:
                    colis.append((0, 0, {'qte': values['qte'], 'sequence': sequence, 'qte_emballer': reste}))
                sequence += 1
                reste -= values['qte_emballer']
                if reste<=0:
                    break
        # print('colis---------------------------------', colis)
        colis_emballage.colis_details = colis
        return colis_emballage

