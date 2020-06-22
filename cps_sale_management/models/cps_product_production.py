# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError, AccessError
from datetime import date, timedelta, datetime

filter_condition = ""
active_view_name = ""

class CpsProductProduction(models.Model):
    _name = 'cps.product.production'
    _inherits = {'cps.product.template': 'product_tmpl_id'}
    _description = 'Liste des commandes de production'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("name", compute='compute_name', store=True)
    state = fields.Selection([('pret', 'Pret'), ('traitement','Traitement'), ('fait','Traité'), ('solde','Soldé')], string='Statut', required=True, default='pret')
    state_fact = fields.Selection([('to_fact','A facturer'), ('fact_part','Fact. Partiellement'), ('fact','Facturé')], string='Statut Fact.', required=True, default='to_fact', compute="compute_state_fact", store=True)
    product_id = fields.Many2one('product.product', 'Produit Odoo')

    product_tmpl_id = fields.Many2one('cps.product.template', 'Product Template', auto_join=True, ondelete="cascade", required=True)
    atelier_id = fields.Many2one("res.partner", 'Atelier', domain=[('is_atelier', '=', True),('supplier_rank', '=', 0),('is_company', '=', True)])
    commande_client = fields.Char("N° commande client")
    date_ok = fields.Date('Date OK')
    date_export = fields.Date("Date d'export")
    ctw = fields.Boolean('Clean to Wear')
    echantillon_id = fields.Many2one("cps.product.echantillon", "Echantillon d'origine")
    echantillon_name = fields.Char(related='echantillon_id.name', string="Nom des echantillons d'origine")
    emballage_ids = fields.One2many('cps.colis.emballage', 'product_production_id', 'Colis emballage')
    chariot_ids = fields.One2many('cps.chariot', 'product_production_id', 'Chariot')
    date_emballage = fields.Datetime(related='emballage_ids.create_date', string="Date emballage")
    total_sortie_emballage_2 = fields.Integer(compute="compute_total_sortie_emballage", string="Emb.", store=True)
    total_sortie_emballage_dynamique = fields.Integer(compute="compute_total_sortie_emballage_dynamique", string="Sorties Emb.")
    total_sortie_emballage_jour = fields.Integer(string="Emb. j.")

    total_chariot_cree = fields.Integer(compute="compute_total_chariot", string="Char.", store=True)

    total_sorties_emballage_dynamique = fields.Integer(compute='_compute_total_sortie_emballage', search='_search_receptions', string='Sorties emballage')
    total_sorties_magasin_dynamique = fields.Integer(compute='_compute_total_sortie_magasin', search='_search_receptions', string='Sorties magasin')
    total_entrees_magasin_dynamique = fields.Integer(compute='_compute_total_reception_magasin', search='_search_receptions', string='Receptions magasin')

    def compute_solde(self):
        for s in self:
            # print(".product_tmpl_id.total_encours-----------------", s.product_tmpl_id.total_encours)
            if s.product_tmpl_id.total_encours<=0 and s.product_tmpl_id.total_sortie>0 and s.product_tmpl_id.total_sortie>=s.product_tmpl_id.qte:
                s.set_solde()

    def compute_solde_schedule(self):
        cps_product = self.env['cps.product.production'].search([], order='code_article')
        cps_product.compute_solde()

    @api.depends('emballage_ids')
    def _compute_total_sortie_emballage(self):
        global filter_condition
        # print('iso calendar----------------------', date.today().isocalendar())
        for p in self:
            totalentree = 0
            if filter_condition == 'today':
                date_filter = date.today().strftime('%Y-%m-%d')
                for e in p.emballage_ids.filtered(lambda t: t.product_production_id.id == p.id and t.create_date.strftime('%Y-%m-%d') == date_filter):
                    totalentree += e.qte
            elif filter_condition == 'yesterday':
                date_filter = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
                for e in p.emballage_ids.filtered(lambda t: t.product_production_id.id == p.id and t.create_date.strftime('%Y-%m-%d') == date_filter):
                    totalentree += e.qte
            elif filter_condition == 'this_week':
                date_filter = date.today().isocalendar()[1]
                for e in p.emballage_ids.filtered(lambda t: t.product_production_id.id == p.id and t.create_date.isocalendar()[1] == date_filter):
                    totalentree += e.qte
            elif filter_condition == 'last_week':
                date_filter = 52 if date.today().isocalendar()[1] - 1 == 0 else date.today().isocalendar()[1] - 1
                for e in p.emballage_ids.filtered(lambda t: t.product_production_id.id == p.id and t.create_date.isocalendar()[1] == date_filter):
                    totalentree += e.qte
            elif filter_condition == 'this_month':
                date_filter = datetime.strptime(str(date.today()), '%Y-%m-%d').month
                for e in p.emballage_ids.filtered(lambda t: t.product_production_id.id == p.id and datetime.strptime(t.create_date.strftime('%Y-%m-%d'), '%Y-%m-%d').month == date_filter):
                    totalentree += e.qte
            elif filter_condition == 'last_month':
                date_filter = datetime.strptime(str(date.today()), '%Y-%m-%d').month - 1 if datetime.strptime(str(date.today()), '%Y-%m-%d').month - 1 > 0 else 12
                for e in p.emballage_ids.filtered(lambda t: t.product_production_id.id == p.id and datetime.strptime(t.create_date.strftime('%Y-%m-%d'), '%Y-%m-%d').month == date_filter):
                    totalentree += e.qte
            elif filter_condition == 'this_year':
                date_filter = datetime.strptime(str(date.today()), '%Y-%m-%d').year
                for e in p.emballage_ids.filtered(lambda t: t.product_production_id.id == p.id and datetime.strptime(t.create_date.strftime('%Y-%m-%d'), '%Y-%m-%d').year == date_filter):
                    totalentree += e.qte
            elif filter_condition == 'last_year':
                date_filter = datetime.strptime(str(date.today()), '%Y-%m-%d').year - 1
                for e in p.emballage_ids.filtered(lambda t: t.product_production_id.id == p.id and datetime.strptime(t.create_date.strftime('%Y-%m-%d'), '%Y-%m-%d').year == date_filter):
                    totalentree += e.qte
            else:
                for e in p.emballage_ids.filtered(lambda t: t.product_production_id.id == p.id):
                    totalentree += e.qte
            filter_condition = ""
            p.total_sorties_emballage_dynamique =totalentree

    @api.depends('livraison_ids')
    def _compute_total_sortie_magasin(self):
        global filter_condition
        for p in self:
            totalsortie = 0
            # print('p-----------------------', p)
            source_location = self.env['res.config.settings'].get_livraison_type().default_location_src_id.id
            if filter_condition == 'today':
                date_filter = date.today().strftime('%Y-%m-%d')
                # print('date_filter-----------------------', date_filter)
                for e in p.livraison_line_ids.filtered(lambda t: t.product_template_livraison_id.id == p.product_tmpl_id.id and t.location_id.id == source_location and t.date_expected.strftime('%Y-%m-%d') == date_filter and t.picking_id.sale_id.id is not False):
                    totalsortie += e.product_uom_qty
            elif filter_condition == 'yesterday':
                date_filter = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
                for e in p.livraison_line_ids.filtered(lambda t: t.product_template_livraison_id.id == p.product_tmpl_id.id and t.location_id.id == source_location and t.date_expected.strftime('%Y-%m-%d') == date_filter and t.picking_id.sale_id.id is not False):
                    totalsortie += e.product_uom_qty
            elif filter_condition == 'this_week':
                date_filter = date.today().isocalendar()[1]
                for e in p.livraison_line_ids.filtered(lambda t: t.product_template_livraison_id.id == p.product_tmpl_id.id and t.location_id.id == source_location and t.date_expected.isocalendar()[1] == date_filter and t.picking_id.sale_id.id is not False):
                    totalsortie += e.product_uom_qty
            elif filter_condition == 'last_week':
                date_filter = 52 if date.today().isocalendar()[1] - 1 == 0 else date.today().isocalendar()[1] - 1
                for e in p.livraison_line_ids.filtered(lambda t: t.product_template_livraison_id.id == p.product_tmpl_id.id and t.location_id.id == source_location and t.date_expected.isocalendar()[1] == date_filter and t.picking_id.sale_id.id is not False):
                    totalsortie += e.product_uom_qty
            elif filter_condition == 'this_month':
                date_filter = datetime.strptime(str(date.today()), '%Y-%m-%d').month
                for e in p.livraison_line_ids.filtered(lambda t: t.product_template_livraison_id.id == p.product_tmpl_id.id and t.location_id.id == source_location and datetime.strptime(t.date_expected.strftime('%Y-%m-%d'), '%Y-%m-%d').month == date_filter and t.picking_id.sale_id.id is not False):
                    totalsortie += e.product_uom_qty
            elif filter_condition == 'last_month':
                date_filter = datetime.strptime(str(date.today()), '%Y-%m-%d').month - 1 if datetime.strptime(str(date.today()), '%Y-%m-%d').month - 1 > 0 else 12
                for e in p.livraison_line_ids.filtered(lambda t: t.product_template_livraison_id.id == p.product_tmpl_id.id and t.location_id.id == source_location and datetime.strptime(t.date_expected.strftime('%Y-%m-%d'), '%Y-%m-%d').month == date_filter and t.picking_id.sale_id.id is not False):
                    totalsortie += e.product_uom_qty
            elif filter_condition == 'this_year':
                date_filter = datetime.strptime(str(date.today()), '%Y-%m-%d').year
                for e in p.livraison_line_ids.filtered(lambda t: t.product_template_livraison_id.id == p.product_tmpl_id.id and t.location_id.id == source_location and datetime.strptime(t.date_expected.strftime('%Y-%m-%d'), '%Y-%m-%d').year == date_filter and t.picking_id.sale_id.id is not False):
                    totalsortie += e.product_uom_qty
            elif filter_condition == 'last_year':
                date_filter = datetime.strptime(str(date.today()), '%Y-%m-%d').year-1
                for e in p.livraison_line_ids.filtered(lambda t: t.product_template_livraison_id.id == p.product_tmpl_id.id and t.location_id.id == source_location and datetime.strptime(t.date_expected.strftime('%Y-%m-%d'), '%Y-%m-%d').year == date_filter and t.picking_id.sale_id.id is not False):
                    totalsortie += e.product_uom_qty
            else:
                for e in p.livraison_line_ids.filtered(lambda t: t.product_template_livraison_id.id == p.product_tmpl_id.id and t.location_id.id == source_location and t.picking_id.sale_id.id is not False):
                    totalsortie += e.product_uom_qty
            p.total_sorties_magasin_dynamique =totalsortie
        filter_condition=""

    @api.depends('reception_ids')
    def _compute_total_reception_magasin(self):
        global filter_condition
        for p in self:
            totalentree = 0
            dest_location = self.env['res.config.settings'].get_reception_type().default_location_dest_id.id
            if filter_condition == 'today':
                date_filter = date.today().strftime('%Y-%m-%d')
                for e in p.reception_line_ids.filtered(lambda t: t.product_template_reception_id.id == p.product_tmpl_id.id and t.location_dest_id.id == dest_location and t.date_expected.strftime('%Y-%m-%d') == date_filter):
                    totalentree += e.product_uom_qty
            elif filter_condition == 'yesterday':
                date_filter = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
                for e in p.reception_line_ids.filtered(lambda t: t.product_template_reception_id.id == p.product_tmpl_id.id and t.location_dest_id.id == dest_location and t.date_expected.strftime('%Y-%m-%d') == date_filter):
                    totalentree += e.product_uom_qty
            elif filter_condition == 'this_week':
                date_filter = date.today().isocalendar()[1]
                for e in p.reception_line_ids.filtered(lambda t: t.product_template_reception_id.id == p.product_tmpl_id.id and t.location_dest_id.id == dest_location and t.date_expected.isocalendar()[1] == date_filter):
                    totalentree += e.product_uom_qty
            elif filter_condition == 'last_week':
                date_filter = 52 if date.today().isocalendar()[1] - 1 == 0 else date.today().isocalendar()[1] - 1
                for e in p.reception_line_ids.filtered(lambda t: t.product_template_reception_id.id == p.product_tmpl_id.id and t.location_dest_id.id == dest_location and t.date_expected.isocalendar()[1] == date_filter):
                    totalentree += e.product_uom_qty
            elif filter_condition == 'this_month':
                date_filter = datetime.strptime(str(date.today()), '%Y-%m-%d').month
                for e in p.reception_line_ids.filtered(lambda t: t.product_template_reception_id.id == p.product_tmpl_id.id and t.location_dest_id.id == dest_location and datetime.strptime(t.date_expected.strftime('%Y-%m-%d'), '%Y-%m-%d').month == date_filter):
                    totalentree += e.product_uom_qty
            elif filter_condition == 'last_month':
                date_filter = datetime.strptime(str(date.today()), '%Y-%m-%d').month - 1 if datetime.strptime(str(date.today()), '%Y-%m-%d').month - 1 > 0 else 12
                for e in p.reception_line_ids.filtered(lambda t: t.product_template_reception_id.id == p.product_tmpl_id.id and t.location_dest_id.id == dest_location and datetime.strptime(t.date_expected.strftime('%Y-%m-%d'), '%Y-%m-%d').month == date_filter):
                    totalentree += e.product_uom_qty
            elif filter_condition == 'this_year':
                date_filter = datetime.strptime(str(date.today()), '%Y-%m-%d').year
                for e in p.reception_line_ids.filtered(lambda t: t.product_template_reception_id.id == p.product_tmpl_id.id and t.location_dest_id.id == dest_location and datetime.strptime(t.date_expected.strftime('%Y-%m-%d'), '%Y-%m-%d').year == date_filter):
                    totalentree += e.product_uom_qty
            elif filter_condition == 'last_year':
                date_filter = datetime.strptime(str(date.today()), '%Y-%m-%d').year-1
                for e in p.reception_line_ids.filtered(lambda t: t.product_template_reception_id.id == p.product_tmpl_id.id and t.location_dest_id.id == dest_location and datetime.strptime(t.date_expected.strftime('%Y-%m-%d'), '%Y-%m-%d').year == date_filter):
                    totalentree += e.product_uom_qty
            else:
                for e in p.reception_line_ids.filtered(lambda t: t.product_template_reception_id.id == p.product_tmpl_id.id and t.location_dest_id.id == dest_location):
                    totalentree += e.product_uom_qty
            p.total_entrees_magasin_dynamique =totalentree
        filter_condition=""


    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        global active_view_name
        res = super(CpsProductProduction, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )
        view_name = self.env['ir.ui.view'].search([('id', '=', view_id)]).name
        if view_name is not False:
            active_view_name = view_name
        return res

    def _search_receptions(self, operator, operand):
        if operator not in ('=', '!=', '<', '<=', '>', '>=', 'in', 'not in'):
            return []
        global filter_condition
        global active_view_name
        filter_condition = operand
        if active_view_name == "cps.product.production.emballages.trees":
            query = "SELECT product_production_id FROM cps_colis_emballage"
            where = ""
            date_field = "create_date"
        elif active_view_name == "cps.product.production.livraison.tree":
            dest_location = self.env['res.config.settings'].get_reception_type().default_location_dest_id.id
            query = "SELECT cps_product_production.id FROM stock_move left join cps_product_production on stock_move.product_template_livraison_id=cps_product_production.product_tmpl_id"
            where = " and origin not like '%Retour%' and location_id=" + str(dest_location)
            date_field = "date_expected"
        elif active_view_name == "cps.product.production.reception.tree":
            source_location = self.env['res.config.settings'].get_livraison_type().default_location_src_id.id
            query = "SELECT cps_product_production.id FROM stock_move left join cps_product_production on stock_move.product_template_reception_id=cps_product_production.product_tmpl_id"
            where = " and location_dest_id=" + str(source_location)
            date_field = "date_expected"
        if filter_condition =='today':
            date_filter = date.today().strftime('%Y-%m-%d')
            query += " where " + date_field + "::TIMESTAMP::DATE = '" + date_filter + "'" + where
        elif filter_condition=='yesterday':
            date_filter = (date.today()-timedelta(days=1)).strftime('%Y-%m-%d')
            query +=" where " + date_field + "::TIMESTAMP::DATE = '" + date_filter + "'" + where
        elif filter_condition=='this_week':
            date_filter = date.today().isocalendar()[1]
            query += " where date_part('week', " + date_field + "::TIMESTAMP::DATE) = " + str(date_filter) + where
        elif filter_condition=='last_week':
            date_filter = 52 if date.today().isocalendar()[1]-1==0 else date.today().isocalendar()[1]-1
            query += " where date_part('week', " + date_field + "::TIMESTAMP::DATE) = " + str(date_filter) + where
        elif filter_condition=='this_month':
            date_filter = datetime.strptime(str(date.today()), '%Y-%m-%d').month
            query += " where date_part('month', " + date_field + "::TIMESTAMP::DATE) = " + str(date_filter) + where
        elif filter_condition=='last_month':
            date_filter = datetime.strptime(str(date.today()), '%Y-%m-%d').month-1 if datetime.strptime(str(date.today()), '%Y-%m-%d').month-1>0 else 12
            query += " where date_part('month', " + date_field + "::TIMESTAMP::DATE) = " + str(date_filter) + where
        elif filter_condition=='this_year':
            date_filter = datetime.strptime(str(date.today()), '%Y-%m-%d').year
            query += " where date_part('year', " + date_field + "::TIMESTAMP::DATE) = " + str(date_filter) + where
        elif filter_condition=='last_year':
            date_filter = datetime.strptime(str(date.today()), '%Y-%m-%d').year-1
            query += " where date_part('year', " + date_field + "::TIMESTAMP::DATE) = " + str(date_filter) + where
        self.env.cr.execute(query)
        ids = [t[0] for t in self.env.cr.fetchall()]
        return [('id', 'in', ids)]

    def compute_total_sortie_emballage_dynamique(self):
        for p in self:
            totalsortieemballage = 0
            for sortieemballage in self.emballage_ids.filtered(lambda t: t.product_production_id.id == p.id):
                totalsortieemballage+=sortieemballage.qte
            p.total_sortie_emballage_dynamique =totalsortieemballage

    @api.depends('chariot_ids')
    @api.onchange('chariot_ids')
    def compute_total_chariot(self):
        for p in self:
            totalchariot = 0
            #totalsortiejour = 0
            for chariot in p.chariot_ids:
                totalchariot+=chariot.qte_reel
                # if date.today().strftime('%Y-%m-%d') == sortie.create_date.strftime('%Y-%m-%d'):
                #     totalsortiejour+=sortie.qte
            p.total_chariot_cree=totalchariot
            #p.total_sortie_emballage_jour=totalsortiejour

    @api.depends('emballage_ids')
    @api.onchange('emballage_ids')
    def compute_total_sortie_emballage(self):
        for p in self:
            totalsortie = 0
            totalsortiejour = 0
            for sortie in p.emballage_ids:
                totalsortie += sortie.qte
                if date.today().strftime('%Y-%m-%d') == sortie.create_date.strftime('%Y-%m-%d'):
                    totalsortiejour += sortie.qte
            p.total_sortie_emballage_2 = totalsortie
            p.total_sortie_emballage_jour = totalsortiejour

    def compute_state_fact(self):
        for p in self:
            if p.total_facturee == 0:
                p.state_fact = "to_fact"
            else:
                if p.total_facturee >= p.total_sortie:
                    p.state_fact = "fact"
                else:
                    p.state_fact = "fact_part"


    def set_solde(self):
        for s in self:
            s.state='solde'

    def set_unsolde(self):
        self.state = 'pret'

    def set_solde_multi(self):
        active_ids = self._context.get('active_ids')
        pps = self.env['cps.product.production'].search([('id', 'in', active_ids)])
        for s in pps:
            s.state='solde'

    def set_unsolde_multi(self):
        active_ids = self._context.get('active_ids')
        pps = self.env['cps.product.production'].search([('id', 'in', active_ids)])
        for s in pps:
            s.state='pret'

    def action_generer_fiche_procede(self):
        procedes = self.product_tmpl_id.action_generer_fiche_procede()
        if procedes is not False:
            return {
                'name': 'Fiches procédés',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'fiche.procede',
                'domain': [('id', 'in', procedes)],
                # 'views': [(tree_id, 'tree'), (form_id, 'form')],
                'target': 'current',
            }

    @api.depends('type_article_id', 'commande_client', 'reference', 'coloriss_client')
    def compute_name(self):
        name=""
        if self.type_article_id.name is not False:
            name = str(self.type_article_id.name)
        if self.reference is not False:
            name = name + " Ref. " + str(self.reference)
        if self.commande_client is not False:
            name = name + " Cde. " + str(self.commande_client)
        if self.coloriss_client.name is not False:
            name = name + " Col. " + str(self.coloriss_client.name)
        self.name = name

    def action_view_receptions(self):
        reception = self.product_tmpl_id.action_view_receptions()
        return {
            'name': 'Liste des réceptions',
            'res_model': 'stock.picking',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', reception.ids)],
            'type': 'ir.actions.act_window',
            'target': 'current'  # will open a popup with mail.message list
        }

    def action_view_retours(self):
        retour = self.product_tmpl_id.action_view_retours()
        return {
            'name': 'Liste des retours S.T.',
            'res_model': 'stock.picking',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', retour.ids)],
            'type': 'ir.actions.act_window',
            'target': 'current'  # will open a popup with mail.message list
        }

    def action_view_retours_correction(self):
        retour = self.product_tmpl_id.action_view_retours_correction()
        return {
            'name': 'Liste des retours pour correction',
            'res_model': 'stock.picking',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', retour.ids)],
            'type': 'ir.actions.act_window',
            'target': 'current'  # will open a popup with mail.message list
        }


    # def action_creer_livraison(self):
    #     livraison = self.product_tmpl_id.action_creer_livraison()
    #     return {
    #         'name': 'Créer Livraison',
    #         'res_model': 'cps.livraison.helper',
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'res_id': livraison.id,
    #         # 'context': {'is_echantillon': True},
    #         'type': 'ir.actions.act_window',
    #         'target': 'new'  # will open a popup with mail.message list
    #     }

    def action_view_livraisons(self):
        livraison = self.product_tmpl_id.action_view_livraisons()
        return {
            'name': 'Liste des livraisons',
            'res_model': 'stock.picking',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', livraison.ids)],
            'type': 'ir.actions.act_window',
            'target': 'current'  # will open a popup with mail.message list
        }

    def action_creer_livraison_emballage(self):
        livraison = self.env['cps.colis.emballage.helper'].create({
            'product_id': self.id,
        })
        return {
            'name': 'Créer Livraison',
            'res_model': 'cps.colis.emballage.helper',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': livraison.id,
            # 'context': {'is_echantillon': True},
            'type': 'ir.actions.act_window',
            'target': 'new'  # will open a popup with mail.message list
        }

    def action_creer_chariot(self):
        chariot = self.env['cps.chariot.helper'].create({
            'product_id': self.id,
        })
        return {
            'name': 'Créer Chariot',
            'res_model': 'cps.chariot.helper',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': chariot.id,
            # 'context': {'is_echantillon': True},
            'type': 'ir.actions.act_window',
            'target': 'new'  # will open a popup with mail.message list
        }

    def action_view_chariot(self):
        return {
            'name': 'Liste des chariots',
            'res_model': 'cps.chariot',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.chariot_ids.ids)],
            'type': 'ir.actions.act_window',
            'target': 'current'  # will open a popup with mail.message list
        }

    def action_view_livraisons_emballage(self):
        return {
            'name': 'Liste des emballages',
            'res_model': 'cps.colis.emballage',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.emballage_ids.ids)],
            'type': 'ir.actions.act_window',
            'target': 'current'  # will open a popup with mail.message list
        }

    def action_view_factures(self):
        factures = self.product_tmpl_id.action_view_factures()
        return {
            'name': 'Liste des factures',
            'res_model': 'account.invoice.sale',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', factures.ids)],
            'type': 'ir.actions.act_window',
            'target': 'current'  # will open a popup with mail.message list
        }

    def action_view_flux(self):
        flux = self.product_tmpl_id.action_view_flux()
        return {
            'name': 'Liste des flux',
            'res_model': 'cps.flux',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id':self.flux_id.id,
            'type': 'ir.actions.act_window',
            'target': 'current'  # will open a popup with mail.message list
        }

    def action_view_route(self):
        routes = self.product_tmpl_id.action_view_route()
        return {
            'name': 'Liste des routes',
            'res_model': 'mrp.routing',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', routes.ids)],
            'type': 'ir.actions.act_window',
            'target': 'current'  # will open a popup with mail.message list
        }
    def action_view_bom(self):
        boms = self.product_tmpl_id.action_view_bom()
        return {
            'name': 'Liste des nomenclatures',
            'res_model': 'mrp.bom',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', boms.ids)],
            'type': 'ir.actions.act_window',
            'target': 'current'  # will open a popup with mail.message list
        }

    def action_view_procede(self):
        procedes = self.product_tmpl_id.action_view_procede()
        return {
            'name': 'Liste des fiches procédés',
            'res_model': 'fiche.procede',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', procedes.ids)],
            'type': 'ir.actions.act_window',
            'target': 'current'  # will open a popup with mail.message list
        }

    @api.model
    def create(self, values):
        query = 'select code_article from cps_product_template  where code_article is not null order by code_article::int desc LIMIT 1'
        self.env.cr.execute(query)
        results = self.env.cr.fetchall()
        if values['code_article'] == 0:
            values['code_article'] = str(int(results[0][0]) + 1)
        else :
            product_prod= self.env['cps.product.production'].search([('code_article', '=', values['code_article'])])
            if len(product_prod) > 0 :
                raise UserError(_("Ce numéro de commande existe, la commande ne peut pas être enregistrée."))
        product_production = super(CpsProductProduction, self).create(values)
        if product_production.commande_client is not False:
            product_production.product_tmpl_id.product_id.name = product_production.product_tmpl_id.code_article + " - " + product_production.product_tmpl_id.product_id.name + " cde " + product_production.commande_client
        product_production.product_id=product_production.product_tmpl_id.product_id
        return product_production

    def write(self, values):
        product_product = super(CpsProductProduction, self).write(values)
        if 'commande_client' in values:
            if values['commande_client'] is not False:
                self.product_tmpl_id.product_id.name = self.product_tmpl_id.product_id.name + " cde " + values['commande_client']

    def create_invoice(self):
        user = self.env['res.users'].browse(self.env.uid)
        if user.has_group('cps_sale_management.group_finance') is False:
            raise UserError(_("Vous n'avez pas le droit de facturer cet OF !"))

        cps_facturation_lines = []
        clients = []
        ateliers = []
        active_ids = self._context.get('active_ids')
        pps = self.env['cps.product.production'].search([('id', 'in', active_ids)])
        if len(pps)>0:
            ateliers.append(pps[0].atelier_id.id)
        i=0
        for l in pps:
            i+=1
            cps_facturation_lines.append((0, 0, { 'product_id': l.product_id.id, 'product_description' : l.product_id.name, 'sequence': i, 'qty_to_invoice': l.total_en_souffrance}))
            if l.client_id.id not in clients:
                clients.append(l.client_id.id)
                # if len(clients) > 1:
                #     raise UserError(
                #         _("Les bons sélectionnés doivent être du même client"))

        cps_facture = {
            'client_id': clients[0],
            'atelier_id' : ateliers[0],
            'client_fact_id': clients[0],
            'date_facture' : date.today().strftime('%Y-%m-%d'),
            'facturation_lines_ids' : cps_facturation_lines
        }
        facture = self.env['account.invoice.sale'].create(cps_facture)
        facture._compute_client_fact_id()


        return {
            'name': "Facture",
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.invoice.sale',
            'res_id': facture.id,
            'type': 'ir.actions.act_window',
            'target': 'current'
        }

    def unlink(self):
        for s in self:
            if s.total_entree>0:
                raise UserError(_("Vous ne pouvez pas supprimer une commande qui contient des mouvements de stock"))
            s.product_tmpl_id.product_id.unlink()
            return super(CpsProductProduction, s).unlink()

    def copy(self, default=None):
        default = dict(default or {})
        default.update ({'code_article': 0,
                         })
        new_product_template = super(CpsProductProduction, self).copy(default)
        return new_product_template
