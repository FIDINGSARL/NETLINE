# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError
from datetime import date

class CpsProductTemplate(models.Model):
    _name = 'cps.product.template'
    _description = 'Liste des modèles de produits'
    _defaults = {'type_article_id': ''}

    active = fields.Boolean("Is active", default=True)
    image_devant = fields.Binary("Photo article devant", attachment=True)
    image_dos = fields.Binary("Photo article dos", attachment=True)
    client_principal_id = fields.Many2one("res.partner", 'Client principal', domain=[('is_client_principal', '=', True),('supplier_rank', '=', 0),('is_company', '=', True)])
    client_id = fields.Many2one("res.partner", 'Nom client', domain=[('is_client_principal', '=', False),('is_atelier', '=', False),('supplier_rank', '=', 0),('is_company', '=', True)], required=True)
    client_name = fields.Char(related='client_id.name', string="Client", store=True)
    devise = fields.Many2one("res.currency",compute='compute_currency', string='Devise')
    code_article = fields.Char(string="N° Commande")
    reference = fields.Char(string="Modéle")
    segment = fields.Selection([('homme', 'Hommes'), ('femme', 'Femmes'), ('enfant', 'Enfant'), ('fille', 'Fille'), ('garcon', 'Garçon') ], string='Segment', required=True, default='femme')
    #couleur_id = fields.Many2one('product.attribute.value', 'Couleur', domain='[("attribute_name", "=", "Couleur article")]')
    coloriss_client = fields.Many2one('cps.product.couleur', 'Couleur Client')
    marque = fields.Many2one('cps.product.marque', 'Marque')
    matiere_id = fields.Many2one('cps.product.matiere', 'Matière')
    composition_id = fields.Many2one('cps.product.composition', 'Composition')
    poids = fields.Float('Poids (kg)')
    qte = fields.Integer('Quantité')
    traitement_ids = fields.One2many("cps.product.traitement.liste", 'template_id', "Traitement fait", copy=True, store=True)
    product_tmpl_production_ids = fields.One2many("cps.product.production", 'product_tmpl_id', "Template production")
    product_tmpl_echantillon_ids = fields.One2many("cps.product.echantillon", 'product_tmpl_id', "Template echantillon")
    traitement_name = fields.Char(compute='compute_traitement_name', string='Traitement')
    route_ids = fields.One2many("mrp.routing", "template_id", string="Routes")
    route_count = fields.Integer(compute='compute_count_route')
    bom_ids = fields.One2many("mrp.bom", "template_id", string="Nomenclatures")
    bom_count = fields.Integer(compute='compute_count_bom')
    price = fields.Float(string="Prix unitaire")
    state = fields.Selection([('pret', 'Pret')], string='Statut', required=True, default='pret')
    flux_id = fields.Many2one("cps.flux", string="Les flux")
    type_couleur = fields.Selection(string="Type couleur", selection=[('clair', 'Clair'), ('moyen', 'Moyen'), ('fonce', 'Foncé') ])
    type_de_traitement = fields.Selection([('delavage','Délavage'),('teinture','Teinture'),('ts','T.S.')])
    remarque = fields.Char("Remarque")
    montant_cde = fields.Float(String="Montant Cde.", compute="on_change_montant_id", store=True)
    montant_en_souffrance = fields.Float(String="Mnt souff.", compute="compute_montant_souffrance", store=True)
    montant_en_souffrance_mad = fields.Float(String="Mnt souff. Dh", compute="compute_montant_souffrance_dh", store=True)
    image_given = fields.Boolean('Image', compute='compute_image_given')
    procede_given = fields.Boolean('Procede renseigné', compute='compute_procede_given', Store=True)
    sale_order_livraison_ids= fields.One2many("sale.order", 'product_template_livraison_id', string="Liste des B.C. livraisons")
    purchase_order_reception_ids= fields.One2many("purchase.order", 'product_template_reception_id', string="Liste des B.C. receptions")
    reception_line_ids= fields.One2many("stock.move", 'product_template_reception_id', string="Liste des récéptions")
    livraison_line_ids = fields.One2many("stock.move", 'product_template_livraison_id', string="Liste des livraisons", domain= '[("to_refund", "=", False)]')
    reception_ids= fields.One2many("stock.picking", 'product_template_reception_id', string="Liste des mvts d'entrée", domain='[("state", "!=", "cancel")]')
    livraison_ids = fields.One2many("stock.picking", 'product_template_livraison_id', string="Liste des mvts de livraisons")
    date_livraison = fields.Datetime(related='livraison_line_ids.date_expected', string="Date de livraison")
    type_article_id = fields.Many2one('product.category', 'Type article', required=True, domain="[('id', 'child_of', 2)]")
    type_article_name = fields.Char(related='type_article_id.name', string='Type')
    product_id = fields.Many2one('product.product', 'Produit Odoo')
    pantone_id = fields.Many2one('cps.pantone', 'Pantone')

    total_entree = fields.Integer(compute="_compute_total_entree", string="Entrées", store=True)
    total_entree_jour = fields.Integer(compute="_compute_total_entree_jour", string="Entrées j.", store=True)
    total_sortie = fields.Integer(compute="_compute_total_sortie", string="Sorties", store=True)
    total_sortie_dynamique = fields.Integer(compute="_compute_total_sortie_dynamique", string="Sorties")
    total_sortie_jour = fields.Integer(compute="_compute_total_sortie_jour", string="Sorties j.", store=True)
    derniere_sortie = fields.Date(compute="_compute_derniere_sortie", string="Dern. Sor.", store=True)
    total_retour = fields.Integer(compute="_compute_total_retour", string="Retours", store=True)

    total_entree_correction = fields.Integer(compute="_compute_total_entree_correction", string="Sortie  Corrections")
    total_sortie_correction = fields.Integer(compute="_compute_total_sortie_correction", string="Entree Corrections")
    total_retour_correction = fields.Integer(compute="_compute_total_retour_correction", string="Corrections",store=True)

    total_encours = fields.Integer(compute="_compute_total_encours", string="Encours", store=True)
    total_facturee = fields.Integer(compute="_compute_total_facture", string="Facturé", store=True)
    total_en_souffrance = fields.Integer(compute="_compute_total_souffrance", string="Souffrance", store=True)
    total_en_souffrance_dh = fields.Integer(compute="_compute_total_souffrance", string="Souff Dh", store=True)
    fiche_procede_ids = fields.One2many('fiche.procede', 'template_id', string="Fiches procédés")
    procede_count = fields.Integer(compute='compute_count_procede')
    name = fields.Char("name", compute='compute_name', store=True)
    date_de_reception = fields.Datetime(related='reception_line_ids.date_expected', string="Date de reception")

    @api.depends('type_article_id', 'reference', 'coloriss_client')
    def compute_name(self):
        name=""
        if self.type_article_id.name is not False:
            name = str(self.type_article_id.name)
        if self.reference is not False:
            name = name + " Ref. " + str(self.reference)
        if self.coloriss_client.name is not False:
            name = name + " Col. " + str(self.coloriss_client.name)
        self.name = name
        return name

    def action_view_procede(self):
        return self.env['fiche.procede'].search([("template_id", "=", self.id)])

    def action_view_route(self):
        return self.env['mrp.routing'].search([("template_id", "=", self.id)])

    def action_view_bom(self):
        return self.env['mrp.bom'].search([("template_id", "=", self.id)])

    def action_view_receptions(self):
        return self.env['stock.picking'].search([("product_template_reception_id", "=", self.id),("origin", "not ilike", "Retour"), ('location_dest_id', '=', self.env['res.config.settings'].get_reception_type().default_location_dest_id.id)])

    def action_view_livraisons(self):
        return self.env['stock.picking'].search([("product_template_livraison_id", "=", self.id),("origin", "not ilike", "Retour"), ('location_id', '=', self.env['res.config.settings'].get_livraison_type().default_location_src_id.id)])

    def action_view_retours(self):
        return self.env['stock.picking'].search([("product_template_livraison_id", "=", self.id),("origin", "ilike", "Retour"), ('location_id', '=', self.env['res.config.settings'].get_livraison_type().default_location_src_id.id)])

    def action_view_retours_correction(self):
        return self.env['stock.picking'].search([("product_template_reception_id", "=", self.id), ('location_dest_id', '=', self.env['res.config.settings'].get_reception_reparation_type().default_location_dest_id.id)])

    def action_view_flux(self):
        return self.env['cps.flux'].search([("id", "=", self.flux_id.id)])

    def action_view_factures(self):
        facture_lines = self.env['account.invoice.sale.line'].search([("product_id", "=", self.product_id.id)]).facturation_id
        return self.env['account.invoice.sale'].search([("id", "in", facture_lines.ids)])


    def compute_count_route(self):
        self.route_count = len(self.route_ids)

    def compute_count_bom(self):
        self.bom_count = len(self.bom_ids)

    def compute_count_procede(self):
        self.procede_count = len(self.fiche_procede_ids)

    def compute_traitement_name(self):
        for p in self:
            p.traitement_name = ""
            for traitement in self.traitement_ids.sorted(key=lambda p: p.sequence):
                if traitement.traitement_id.name is not False:
                    p.traitement_name = p.traitement_name + traitement.traitement_id.name + " + "
            p.traitement_name=p.traitement_name[:-3]

    @api.depends("qte","price")
    @api.onchange("qte","price")
    def on_change_montant_id(self):
        for p in self:
            p.montant_cde = p.qte * p.price

    def compute_currency(self):
        for p in self:
            if p.client_id.id is not False:
                p.devise= p.client_id.property_product_pricelist.currency_id

    def compute_procede_given(self):
        for i in self:
            i.procede_given=False
            if len(i.fiche_procede_ids)>0:
                i.procede_given=True

    def compute_image_given(self):
        for i in self:
            i.image_given=False
            if (i.image_devant is not False) or (i.image_dos is not False):
                i.image_given=True

    def compute_all(self):
        for p in self:
            p._compute_total_encours()
            p._compute_total_entree()
            p._compute_total_entree_jour()
            p._compute_total_sortie()
            p._compute_total_sortie_jour()
            p._compute_total_retour()
            p._compute_total_entree_correction()
            p._compute_total_sortie_correction()
            p._compute_total_retour_correction()
            p._compute_total_facture()
            p._compute_total_souffrance()
            p.compute_montant_souffrance()
            p.compute_montant_souffrance_dh()
            p._compute_derniere_sortie()
            p._compute_total_encours()

    def compute_all_schedule(self):
        print('compute_ all SCHEDULE--------------------------------------')
        cps_template = self.env['cps.product.template'].search([], order='code_article')
        cps_template.compute_all()

    def _compute_total_encours(self):
        for p in self:
            p.total_encours = p.total_entree-p.total_sortie-p.total_retour+p.total_retour_correction

    def _compute_derniere_sortie(self):
        for p in self:
            derniere_sortie = self.env['stock.picking'].search([("product_template_livraison_id", "=", p.id),("origin", "not ilike", "Retour"),('location_id','=',self.env['res.config.settings'].get_livraison_type().default_location_src_id.id)], order='date desc', limit=1)
            p.derniere_sortie = derniere_sortie.date

    def _compute_total_entree(self):
        for p in self:
            totalEntree = 0
            entrees = self.env['stock.picking'].search([("state", "!=", "cancel"),("product_template_reception_id", "=", p.id),("origin", "not ilike", "Retour"),('location_dest_id','=',self.env['res.config.settings'].get_reception_type().default_location_dest_id.id)])
            for entree in entrees.move_ids_without_package:
                totalEntree+=entree.product_uom_qty
            p.total_entree=totalEntree

    def _compute_total_entree_jour(self):
        for p in self:
            totalEntree = 0
            entrees = self.env['stock.picking'].search([("state", "!=", "cancel"),("product_template_reception_id", "=", p.id),("origin", "not ilike", "Retour"),('location_dest_id','=',self.env['res.config.settings'].get_reception_type().default_location_dest_id.id)])
            for entree in entrees.move_ids_without_package:
                if date.today().strftime('%Y-%m-%d')== entree.date_expected.strftime('%Y-%m-%d'):
                    totalEntree+=entree.product_uom_qty
            p.total_entree_jour=totalEntree

    def _compute_total_sortie(self):
        for p in self:
            totalsortie = 0
            sorties = self.env['stock.picking'].search([("state", "!=", "cancel"),("product_template_livraison_id", "=", p.id),("origin", "not ilike", "Retour"),('location_id','=',self.env['res.config.settings'].get_livraison_type().default_location_src_id.id)])
            for sortie in sorties.move_ids_without_package:
                totalsortie+=sortie.product_uom_qty
            p.total_sortie=totalsortie

    def _compute_total_sortie_dynamique(self):
        depot=self.env['res.config.settings'].get_livraison_type().default_location_src_id.id
        for p in self:
            totalsortie = 0
            for sortie in self.livraison_line_ids.filtered(lambda t: t.product_id.id == p.product_id.id and "Retour" not in t.picking_id.origin and t.location_id.id==depot):
                totalsortie+=sortie.product_uom_qty
            p.total_sortie_dynamique =totalsortie

    def _compute_total_sortie_jour(self):
        for p in self:
            totalsortie = 0
            sorties = self.env['stock.picking'].search([("state", "!=", "cancel"),("product_template_livraison_id", "=", p.id),("origin", "not ilike", "Retour"),('location_id','=',self.env['res.config.settings'].get_livraison_type().default_location_src_id.id)])
            for sortie in sorties.move_ids_without_package:
                if date.today().strftime('%Y-%m-%d')== sortie.date_expected.strftime('%Y-%m-%d'):
                    totalsortie+=sortie.product_uom_qty
            p.total_sortie_jour=totalsortie

    def _compute_total_retour(self):
        for p in self:
            totalretour = 0
            retours = self.env['stock.picking'].search([("state", "!=", "cancel"),("product_template_livraison_id", "=", p.id),("origin", "ilike", "Retour"),('location_id','=',self.env['res.config.settings'].get_livraison_type().default_location_src_id.id)])
            for retour in retours.move_ids_without_package:
                totalretour+=retour.product_uom_qty
            p.total_retour=totalretour

    def _compute_total_retour_correction(self):
        for p in self:
            p.total_retour_correction = p.total_entree_correction - p.total_sortie_correction

    def _compute_total_entree_correction(self):
        for p in self:
            totalretourcorrection = 0
            retours = self.env['stock.picking'].search([("state", "!=", "cancel"),("product_template_reception_id", "=", p.id), ('location_dest_id','=',self.env['res.config.settings'].get_reception_reparation_type().default_location_dest_id.id)])
            for retour in retours.move_ids_without_package:
                totalretourcorrection+=retour.product_uom_qty
            p.total_entree_correction=totalretourcorrection

    def _compute_total_sortie_correction(self):
        for p in self:
            totalretourcorrection = 0
            retours = self.env['stock.picking'].search([("state", "!=", "cancel"),("product_template_livraison_id", "=", p.id), ('location_id','=',self.env['res.config.settings'].get_reception_reparation_type().default_location_dest_id.id)])
            for retour in retours.move_ids_without_package:
                totalretourcorrection+=retour.product_uom_qty
            p.total_sortie_correction=totalretourcorrection

    def _compute_total_facture(self):
        for p in self:
            totalfacturee = 0
            facturees = self.env['account.move.line'].search([("parent_state", "=", "posted"),("quantity", ">", 0), ("journal_id", "=", 1),("product_id", "=", p.product_id.id)])
            for facturee in facturees:
                totalfacturee+=facturee.quantity
            p.total_facturee =totalfacturee

    @api.depends('price')
    @api.onchange('price')
    def _compute_total_souffrance(self):
        for p in self:
            p.total_en_souffrance = p.total_sortie-p.total_facturee

    @api.depends('price','total_en_souffrance')
    @api.onchange('price','total_en_souffrance')
    def compute_montant_souffrance(self):
        for p in self:
            p.montant_en_souffrance = p.total_en_souffrance*p.price

    @api.depends('price','total_en_souffrance')
    @api.onchange('price','total_en_souffrance')
    def compute_montant_souffrance_dh(self):
        for p in self:
            p.montant_en_souffrance_mad = p.montant_en_souffrance * (1/p.devise.rate)


    def action_creer_reception(self):
        reception = self.env['cps.reception.helper'].create({
            'partner_id': self.client_id.id,
            'product_id': self.product_id.id,
            'is_correction' : False,
            'qte': 0,
        })
        return reception

    def action_creer_reception_correction(self):
        reception = self.env['cps.reception.helper'].create({
            'partner_id': self.client_id.id,
            'product_id': self.product_id.id,
            'is_correction' : True,
            'qte': 0,
        })
        return reception

    def action_creer_livraison(self):
        livraison = self.env['cps.livraison.helper'].create({
            'partner_id': self.client_id.id,
            'product_id': self.product_id.id,
            'qte': 0,
        })
        return livraison

    def create_product(self, nom, type_article, price):
        template = self.env['product.product'].create({
            'name': nom,
            'type': 'product',
            'sale_ok': True,
            'purchase_ok':False,
            'invoice_policy': 'delivery',
            'categ_id': type_article.id,
            'list_price': price,
        })
        return template



    def create_route(self, template):
        if len(template.traitement_ids) > 0:
            route = self.env['mrp.routing'].create({
                'name': template.name,
                'template_id': template.id
            })
            for traitement in template.traitement_ids.sorted(key=lambda p: p.sequence):
                self.env['mrp.routing.workcenter'].create({
                    'name': traitement.traitement_id.name,
                    'workcenter_id': traitement.traitement_id.section_id.id,
                    'routing_id': route.id,
                    'time_mode_batch': 2,
                    'time_mode': 'auto',
                    'time_cycle_manual': 0,
                    'batch': 'yes',
                    'worksheet_type': 'google_slide',
                    'worksheet_google_slide': traitement.gslide,
                    'batch_size': 1,
                })
            return route

    def create_flux(self, template):
        cps_flux = self.env['cps.flux'].create({
            'name': template.name,
        })
        return cps_flux


    def action_creer_of(self):
        reception = self.env['cps.of.helper'].create({
            'product_id': self.product_id.id,
            'qte': 0,
        })
        return reception

    def create_route_with_time(self, template):
        traitements = self.env['cps.product.traitement.liste'].search([('id', 'in', template.traitement_ids.ids)])
        for traitement in traitements:
            tempsTotal = 0
            for ligne_procede in traitement.fiche_procede_id.procede_line_ids:
                tempsTotal += ligne_procede.temps
            routing_line = self.env['mrp.routing.workcenter'].search([('name', '=', traitement.traitement_id.name),
                                                                      ('workcenter_id', '=',
                                                                       traitement.traitement_id.section_id.id)],
                                                                     order='id desc', limit=1)
            if traitement.fiche_procede_id.qte_machine>0:
                routing_line.time_cycle_manual = tempsTotal / traitement.fiche_procede_id.qte_machine

    def update_route_with_time(self):
        for fiche_procede in self.fiche_procede_ids:
            tempsTotal = 0
            for ligne_procede in fiche_procede.procede_line_ids:
                tempsTotal += ligne_procede.temps
            routing_line = self.env['mrp.routing.workcenter'].search([('name', '=', fiche_procede.traitement_id.name),
                                                                          ('workcenter_id', '=',
                                                                           fiche_procede.traitement_id.section_id.id)],
                                                                         order='id desc', limit=1)
            if fiche_procede.qte_machine>0:
                routing_line.time_cycle_manual = tempsTotal / fiche_procede.qte_machine

    @api.model
    def create(self, values):
        product_template = super(CpsProductTemplate, self).create(values)
        if 'type_article_id' in values:
            type_article = self.env['product.category'].search([('id', '=', values['type_article_id'])])
        product_odoo = self.create_product(product_template.name, type_article, values['price'])
        product_template.product_id=product_odoo.id
        cps_flux = self.create_flux(product_template)
        product_template.flux_id = cps_flux.id
        return product_template

    def write(self, values):
        product_template = super(CpsProductTemplate, self).write(values)
        if 'active' in values:
            if values['active']==False:
                pp = self.env['product.product'].search([("id", "=", self.product_id.id)])
                pp.active = values['active']
        if 'type_article_id' in values:
            self.product_id.categ_id = values['type_article_id']
            # raise UserError(_("Le type d'article ne peut etre modifié !"))
        if 'price' not in values:
            values['price']=self.price
        if len(self.product_id)>0:
            self.product_id.list_price= values['price']
            if 'name' in values:
                self.product_id.name = values['name']
            if 'traitement_ids' in values:
                self.create_route(self)
                procedes =[]
                for procede in self.fiche_procede_ids:
                    traitement = self.env['cps.product.traitement.liste'].search([('traitement_id', '=', procede.traitement_id.id), ('template_id', '=', self.id)])
                    if len(traitement)==0:
                        procedes.append(procede.id)
                liste_procede = self.env['fiche.procede'].search([('id', 'in', procedes)])
                liste_procede.template_id=[]
            if 'fiche_procede_ids' in values:
                self.update_route_with_time()
                bom = self.create_bom()
            if 'price' in values:
                sos = self.env['sale.order.line'].search([('product_id', '=', self.product_id.id)])
                sos.price_unit = values['price']
                pp = self.env['product.product'].search([("id", "=", self.product_id.id)])
                pp.lst_price = values['price']


        return product_template

    def action_generer_fiche_procede(self):
        #### creation de la nomenclature
        if self.poids==0:
            raise UserError(_("Le poids n'est pas renseigné !"))
        route = self.create_route(self)
        for traitement_id in self.traitement_ids:
            if traitement_id.fiche_procede_id.id is False:
                raise UserError(_("Merci de vérifier que toutes les informations du traitement sont renseignés !"))
            if traitement_id.traitement_id.id is False:
                raise UserError(_("Merci de vérifier que toutes les informations du traitement sont renseignés !"))
        fiches_procedes_to_return=[]
        for traitement_id in self.traitement_ids:
            fiche_procede = traitement_id.fiche_procede_id
            fiche_procedes = self.env['fiche.procede'].search([('template_id', '=', self.id),('traitement_id', '=', traitement_id.traitement_id.id)])
            if len(fiche_procedes)==0:
                default={}
                default = dict(default or {})
                default.update({
                    'template_id': self.id,
                    'version': len(fiche_procedes)+1
                })
                new_fichde_procede = fiche_procede.copy(default)
                new_fichde_procede.poids_article = self.poids
                new_fichde_procede.compute_poids()
                new_fichde_procede.compute_procede_lines()
                fiches_procedes_to_return.append(new_fichde_procede.id)
                if len(fiche_procede.procede_line_ids) > 0:
                    for fiche_procede_line in fiche_procede.procede_line_ids:
                        default = None
                        default = dict(default or {})
                        default.update({'procede_id': new_fichde_procede.id, })
                        fiche_procede_line.copy(default)
        self.create_bom()
        self.create_route_with_time(self)
        if len(fiches_procedes_to_return)>0:
            return fiches_procedes_to_return
        else:
            return False

    def create_bom(self):
        if len(self.product_id)>0:
            route = self.env['mrp.routing'].search([('template_id', '=', self.id)], order='create_date desc', limit=1)
            bom_id = self.env['mrp.bom'].create({
                'product_tmpl_id': self.product_id.product_tmpl_id.id,
                'product_qty': 1,
                'type': 'normal',
                'product_id': self.product_id.id,
                'routing_id': route.id,
                'template_id':self.id
            })
            # for fiche_procede in self.fiche_procede_ids:
            #     fiche_procede.generate_bom_line(mrp_bom.id, fiche_procede.traitement_id.section_id.id, fiche_procede)
            valJouleToFueloilequivalent = 41000000
            valKwHVapeurSecadora = 187.5
            tempsCentrifuge = 40
            tempsSechage = 40
            valKWHSecadora = 19
            valKWHCentrifuge = 16
            valKWHMachine = 16
            for fiche_procede in self.fiche_procede_ids:
                workcenter_id = self.env['mrp.routing.workcenter'].search([('name', '=', fiche_procede.traitement_id.name),
                                                                          ('workcenter_id', '=',
                                                                           fiche_procede.traitement_id.section_id.id)],
                                                                         order='id desc', limit=1).id
                quimicos = []
                total_eau = 0
                total_kcal = 0
                total_temps = 0
                nb_lines = 0
                line_value = ({})
                for procedeline in fiche_procede.procede_line_ids:
                    if len(procedeline.quimicos) > 0:
                        trouve = False
                        for quimico in quimicos:
                            if quimico['product_id'] == procedeline.quimicos.id:
                                quimico['product_qty'] += procedeline.dosification
                                trouve = True
                        if trouve == False:
                            line_value = ({
                                'product_id': procedeline.quimicos.id,
                                'product_qty': procedeline.dosification,
                            })
                            quimicos.append(line_value)
                    total_eau += procedeline.eau / 1000
                    total_temps += procedeline.temps
                    if procedeline.temperature>20:
                        total_kcal+=(procedeline.temperature-20)
                        nb_lines+=1
                if nb_lines>0:
                    fuel_lavage_teinture = ((total_kcal/nb_lines) * total_eau * 1000 / valJouleToFueloilequivalent)
                fuel_sechage = ((valKwHVapeurSecadora * (tempsSechage / 60)) / 11.2) * 1.3
                electricite_lavage_teinture = total_temps / 60 * valKWHMachine
                electricite_centrifuge = tempsCentrifuge / 60 * valKWHCentrifuge
                electricite_sechage = tempsSechage / 60 * valKWHSecadora

                for quimico in quimicos:
                    mrp_bom_line = self.env['mrp.bom.line'].create({
                        'bom_id': bom_id.id,
                        'procede_id': fiche_procede.id,
                        'product_id': quimico['product_id'],
                        'product_qty': quimico['product_qty'] / fiche_procede.qte_machine,
                        'operation_id': workcenter_id
                    })

                if fiche_procede.qte_machine > 0 and total_eau > 0:
                    product_eau = self.env['product.product'].search([('default_code', '=', 'EAU')])
                    mrp_bom_line = self.env['mrp.bom.line'].create({
                        'bom_id': bom_id.id,
                        'procede_id': fiche_procede.id,
                        'product_id': product_eau.id,
                        'product_qty': total_eau / fiche_procede.qte_machine,
                        'operation_id': workcenter_id
                    })
                    product_fuel = self.env['product.product'].search([('default_code', '=', 'FUEL')])
                    mrp_bom_line = self.env['mrp.bom.line'].create({
                        'bom_id': bom_id.id,
                        'procede_id': fiche_procede.id,
                        'product_id': product_fuel.id,
                        'product_qty': (fuel_lavage_teinture + fuel_sechage) / fiche_procede.qte_machine,
                        'operation_id': workcenter_id
                    })
                    product_electricite = self.env['product.product'].search([('default_code', '=', 'ELEC')])
                    mrp_bom_line = self.env['mrp.bom.line'].create({
                        'bom_id': bom_id.id,
                        'procede_id': fiche_procede.id,
                        'product_id': product_electricite.id,
                        'product_qty': (electricite_lavage_teinture + electricite_centrifuge + electricite_sechage) / fiche_procede.qte_machine,
                        'operation_id': workcenter_id
                    })
            produit_charges_fixes = self.env['product.product']
            if self.type_de_traitement == 'delavage':
                produit_charges_fixes = self.env['product.product'].search([('default_code', '=', 'FIXES DEL')])
            if self.type_de_traitement == 'teinture':
                produit_charges_fixes = self.env['product.product'].search([('default_code', '=', 'FIXES TEIN')])
            if self.type_de_traitement == 'ts':
                produit_charges_fixes = self.env['product.product'].search([('default_code', '=', 'FIXES TS')])

            if len(produit_charges_fixes) > 0:
                mrp_bom_line = self.env['mrp.bom.line'].create({
                    'bom_id': bom_id.id,
                    # 'procede_id': fiche_procede.id,
                    'product_id': produit_charges_fixes.id,
                    'product_qty': 1,
                })

    # def generate_bom_line(self, bom_id, workcenter_id, fiche_procede):

    # def create_bom_line(self, bom, traitement_id, ficheprocede):
    #     print('traitement_id-------------------', traitement_id.name)
    #     print('fiche procede-------------------', ficheprocede.name)
    #     routing_line = self.env['mrp.routing.workcenter'].search([('name', '=', traitement_id.name),('workcenter_id', '=', traitement_id.section_id.id)], order='id desc', limit=1)
    #     ficheprocede.generate_bom_line(bom.id, routing_line.id, ficheprocede)



    # @api.onchange('poids')
    # def compute_quantite_machine(self):
    #     for p in self.fiche_procede_ids:
    #         p._compute_qte_machine()
    #     for p in self.traitement_ids:
    #         p.poids_article = self.poids