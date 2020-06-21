# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

#
# Please note that these reports are not multi-currency !!!
#

from odoo import api, fields, models, tools


class CpsProductProductionReport(models.Model):
    _name = "cps.product.production.report"
    _description = "Etat de la production"
    _auto = False
    _order = 'code_article desc'

    code_article = fields.Char('N° Cmd.', readonly=True)
    id = fields.Many2one('cps.product.production', 'Cmd ID', readonly=True)
    # qte = fields.Integer(related='id.qte',string='Qté cde', readonly=True)
    client_id = fields.Many2one('res.partner', 'Client', readonly=True)
    client_principal_id = fields.Many2one("res.partner", 'Client principal', domain=[('is_client_principal', '=', True),('supplier_rank', '=', 0),('is_company', '=', True)])
    designation = fields.Char('Désignation', readonly=True)
    traitement_name = fields.Char('Traitement', readonly=True)
    date = fields.Datetime('Date', readonly=True)
    type_de_traitement = fields.Char('Type traitement')
    entree = fields.Integer('Qté reçue', readonly=True)
    sortie = fields.Integer('Livrée', readonly=True)
    valeur = fields.Float('Valeur')

    #encours = fields.Integer('Encours', readonly=True)
    #encours = fields.Integer(compute="compute_encours", string="Encours", store=True)

    # def compute_valeur(self):
    #     for p in self:
    #         print('valeur--------------------', p.id.product_tmpl_id.price)
    #         p.valeur = p.sortie*p.id.product_tmpl_id.price
    #statut = fields.Selection([('lance', 'Lancé'), ('livre', 'Livré'), ('solde', 'Soldé'), ('facture', 'Facturé'),('annule', 'Sans suite')], string='Statut commande', required=True, default='lance')


    def init(self):
        # "init"
        tools.drop_view_if_exists(self._cr, 'cps_product_production_report')
        self._cr.execute("""
                create view cps_product_production_report as (
                    WITH currency_rate as (%s)
                    select cps_product_production.id as id, cps_product_production.name as designation, cps_product_template.code_article,cps_product_template.client_id, cps_product_template.client_principal_id, cps_product_template.type_de_traitement,
                            cps_product_production.product_id, stock_move.n_bon_client, stock_move.date,stock_move_line.qty_done as sortie ,0 as entree ,
							(case when sale_order.pricelist_id=1 then 
								stock_move_line.qty_done*cps_product_template.price*10.8
							else					
								stock_move_line.qty_done*cps_product_template.price
							end) as valeur
                            from cps_product_production
                            left join cps_product_template on cps_product_production.product_tmpl_id = cps_product_template.id
                            left JOIN stock_move  on stock_move.product_template_livraison_id = cps_product_template.id
							left JOIN stock_move_line on stock_move_line.move_id = stock_move.id and stock_move.state = 'done'
							left join stock_picking on stock_move.picking_id= stock_picking.id 
							left join sale_order on stock_picking.sale_id = sale_order.id
							where left(stock_picking.origin,6)<>'Retour'
							Union 
                            select cps_product_production.id as id, cps_product_production.name as designation, cps_product_template.code_article,cps_product_template.client_id, cps_product_template.client_principal_id, cps_product_template.type_de_traitement,
                            cps_product_production.product_id,stock_move.n_bon_client, stock_move.date,0 as sortie, stock_move_line.qty_done as entree, 0 as valeur
                            from cps_product_production
                            left join cps_product_template on cps_product_production.product_tmpl_id = cps_product_template.id
                            left JOIN stock_move  on stock_move.product_template_reception_id = cps_product_template.id
							left JOIN stock_move_line on stock_move_line.move_id = stock_move.id and stock_move.state = 'done')
            """ % self.env['res.currency']._select_companies_rates())