# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError
import datetime

class Netline_product_template(models.Model):
    #netline laundry product
    _name = 'netline.product'
    _order='n_ligne, id'

    designation_client = fields.Char(string="Designation Client")
    prix_lavage = fields.Float(string="Prix lavage")
    prix_lavage_sec = fields.Float(string="Prix lavage a sec")    
    prix_repassage = fields.Float(string="Prix repassage")
    prix_detachage = fields.Float(string="Prix détachage")
    prix_decatissage = fields.Float(string="Prix décatissage")

    type_id = fields.Many2one('netline.product.type', 'Type')
    type_name = fields.Char(related="type_id.name")
    couleur_id = fields.Many2one('netline.product.couleur', 'Couleur' , domain='[("state", "=", "ok")]')
    color_name = fields.Char(related="couleur_id.name")
    matiere_id = fields.Many2one('netline.product.matiere', 'Matière' , domain='[("state", "=", "ok")]')
    composition_id = fields.Many2one('netline.product.composition', 'Composition' , domain='[("state", "=", "ok")]')
    taille_id= fields.Many2one('netline.product.taille', 'Composition')
    marque_id = fields.Many2many('netline.product.marque', 'product_id', string='Marque')
    poids = fields.Float(string="Poids")
    grammage = fields.Float('Grammage')
    longueur= fields.Integer("Longueur")
    largeur= fields.Integer("Largeur")
    n_ligne= fields.Integer("Numéro Ligne")

    product_id = fields.Many2one("product.product", 'Produit',  domain='[("is_laundry", "=", True)]')
    product_name = fields.Char(related="product_id.name")
    name = fields.Char("name", compute="compute_name",store=True)
    # produit_name = fields.Char("name", compute="compute_product_name",store=True)

    def get_price(self, traitement):
        price = self.prix_lavage

        if traitement == 'lavage':
            price = self.prix_lavage
        elif traitement == 'lavage_sec':
            price = self.prix_lavage_sec
        elif traitement == 'repassage':
            price = self.prix_repassage
        elif traitement == 'detachage':
            price = self.prix_detachage
        elif traitement == 'decatissage':
            price = self.prix_decatissage

        if price is 0:
            raise UserError(
                _("Le prix de cet article n'est pas renseigné"))
        return price

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search((args+[('product_name', 'ilike', name)]),
                               limit=limit)
            recs = recs + self.search(([('designation_client', 'ilike', name)] + args),
                                  limit=limit)
        if not recs:
            recs = self.search([('name', operator, name)] + args, limit=limit)
        return recs.name_get()

    client_id = fields.Many2one("res.partner", 'Client')
    reception_id = fields.One2many('netline.reception.line', 'reception_id')
    devise_client = fields.Many2one("res.currency",compute='_compute_partner_currency', string='Devise')
    def _compute_partner_currency(self):
        for devise in self:
            devise.devise_client= devise.client_id.devise.id


    def name_get(self):
        res = []
        #designation_client, designation, type, couleur
        for rec in self:
            name = rec.name
            res.append((rec.id, name))
        return res
        
    # def get_name(self):
    #     name = ""
    #     if self.product_id.name is not False:
    #         name = name + self.product_id.name
    #     if self.designation_client is not False:
    #         name = name + "-" + self.designation_client
    #     if self.type_id.name is not False:
    #         name = name + " - " + self.type_id.name
    #     if self.couleur_id.name is not False:
    #         name = name + " - " + self.couleur_id.name
    #     return name


    @api.depends('designation_client','product_id','type_id','couleur_id')
    def compute_name(self):
        recs = []
        for p in self:
            name = ""
            if p.designation_client is not False:
                name = name + p.designation_client + " - "
            if p.product_id.name is not False:
                name = name + p.product_id.name + " - "
            if p.type_id.name is not False:
                name = name + p.type_id.name + " - "
            if p.couleur_id.name is not False:
                name = name + p.couleur_id.name + " - "
            if len(name) > 0:
                name = name[:-3]
            p.name = name


    # def compute_product_name(self):
    #     recs = []
    #     for p in self:
    #         name = ""
    #         if p.designation_client is not False:
    #             name = name + p.designation_client + " - "
    #         if p.product_id.name is not False:
    #             name = name + p.product_id.name + " - "
    #         if p.type_id.name is not False:
    #             name = name + p.type_id.name + " - "
    #         if p.couleur_id.name is not False:
    #             name = name + p.couleur_id.name + " - "
    #         if len(name) > 0:
    #             name = name[:-3]
    #         p.produit_name = name

class Netline_pressing_product(models.Model):
    _name = 'netline.pressing_product'
    _order='n_ligne, id'

    client_id = fields.Many2one("res.partner", 'Client')
    client_name = fields.Char(related='client_id.name', store=True)
    product_id = fields.Many2one("product.product", 'Produit',  domain='[("is_pressing", "=", True)]' )

    designation_client = fields.Char(string="Designation Client")
    poids = fields.Float(string="Poids")
    sexe=fields.Selection([('homme', 'Messieurs'), ('femme', 'Dames'), ('enfant', 'Enfants')], string='Sexe', default='homme')

    prix_lavage = fields.Float(string="Prix Lavage")
    prix_lavage_sec = fields.Float(string="Prix lavage a sec")    
    prix_repassage = fields.Float(string="Prix Repassage")
    prix_detachage = fields.Float(string="Prix détachage")
    n_ligne= fields.Integer("Numéro Ligne")
    
    reception_id = fields.One2many('netline.reception.line', 'reception_id')
    product_name = fields.Char(related="product_id.name")
    name = fields.Char("name", compute="compute_name",store=True)
    reception_product_selection_ids = fields.Many2many("netline.reception", "pressing_product_selection_ids")
    devise_client = fields.Many2one("res.currency",compute='_compute_partner_currency', string='Devise')

    def _compute_partner_currency(self):
        for devise in self:
            devise.devise_client= devise.client_id.devise.id

    def get_price(self, traitement):
        price = self.prix_lavage

        if traitement == 'lavage':
            price = self.prix_lavage
        elif traitement == 'lavage_sec':
            price = self.prix_lavage_sec
        elif traitement == 'repassage':
            price = self.prix_repassage
        elif traitement == 'detachage':
            price = self.prix_detachage

        if price is 0:
            raise UserError(
                _("Le prix de cet article n'est pas renseigné"))
        return price

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search((args+[('product_name', 'ilike', name)]),
                               limit=limit)
            recs = recs + self.search(([('designation_client', 'ilike', name)] + args),
                                  limit=limit)
        if not recs:
            recs = self.search([('name', operator, name)] + args, limit=limit)
        return recs.name_get()


    def name_get(self):
        res = []
        #designation_client, designation, type, couleur
        for rec in self:
            name = rec.name
            res.append((rec.id, name))
        return res
        

    @api.depends('designation_client','product_id','sexe')
    def compute_name(self):
        recs = []
        for p in self:
            name = ""
            if p.product_id.name is not False:
                name = name + p.product_id.name
            if p.designation_client is not False:
                name = name + " | " + p.designation_client
            if p.sexe is not False:
                name = name + " | " + p.sexe
            p.name = name

    def get_name(self):
        name = ""
        if self.product_id.name is not False:
            name = name + self.product_id.name
        if self.designation_client is not False:
            name = name + " | " + self.designation_client
        if self.sexe is not False:
            name = name + " | " + self.sexe
        return name

class Netline_vt_product(models.Model):
    _name = 'netline.vt_product'
    _order='n_ligne, id'

    client_id = fields.Many2one("res.partner", 'Client')
    client_name = fields.Char(related='client_id.name', store=True)
    product_id = fields.Many2one("product.product", 'Produit',  domain='[("is_vt", "=", True)]' )
    couleur_id = fields.Many2one("netline.product.couleur", 'Couleur')

    designation_client = fields.Char(string="Designation Client")
    poids = fields.Float(string="Poids")

    code_article = fields.Char(string="Code Article")
    ref_unif = fields.Char(string="Ref. Unif.")
    sexe=fields.Selection([('homme', 'Messieurs'), ('femme', 'Dames')], string='Sexe', default='homme')
    departement_id = fields.Many2one('netline.vt_product.departement', 'Departement')
    fonction_id = fields.Many2one('netline.vt_product.fonction', 'Fonction')
    taille_id = fields.Many2one('netline.product.taille', 'Taille')

    prix_lavage = fields.Float(string="Prix Lavage")
    prix_lavage_sec = fields.Float(string="Prix lavage a sec")    
    prix_repassage = fields.Float(string="Prix Repassage")
    prix_detachage = fields.Float(string="Prix détachage")

    porteur_ids = fields.Many2one('netline.porteur', 'product_ids')
    reception_id = fields.One2many('netline.reception.line', 'reception_id')
    product_name = fields.Char(related="product_id.name")
    fonction_name = fields.Char(related="fonction_id.name")
    departement_name = fields.Char(related="departement_id.name")

    name = fields.Char("name", compute="compute_name", store=True)

    n_ligne= fields.Integer("Numéro Ligne")
    devise_client = fields.Many2one("res.currency",compute='_compute_partner_currency', string='Devise')
    def _compute_partner_currency(self):
        for devise in self:
            devise.devise_client= devise.client_id.devise.id


    def get_price(self, traitement):
        price = self.prix_lavage

        if traitement == 'lavage':
            price = self.prix_lavage
        elif traitement == 'lavage_sec':
            price = self.prix_lavage_sec
        elif traitement == 'repassage':
            price = self.prix_repassage
        elif traitement == 'detachage':
            price = self.prix_detachage

        if price is 0:
            raise UserError(
                _("Le prix de cet article n'est pas renseigné"))
        return price

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search((args+[('product_name', 'ilike', name)]),
                               limit=limit)
            recs = recs + self.search(([('designation_client', 'ilike', name)] + args),
                                  limit=limit)
        if not recs:
            recs = self.search([('name', operator, name)] + args, limit=limit)
        return recs.name_get()


    def name_get(self):
        res = []
        #designation_client, designation, type, couleur
        for rec in self:
            name = rec.name
            res.append((rec.id, name))
        return res


    @api.depends('product_id','couleur_id','fonction_id','departement_id')
    def compute_name(self):
        recs = []
        for p in self:
            name = ""
            if p.product_id.name is not False:
                name = name + p.product_id.name
            if p.couleur_id.name is not False:
                name = name + " (" + p.couleur_id.name + " )"
            if p.fonction_id.name is not False:
                name = name + " | " + p.fonction_id.name
            if p.departement_id.name is not False:
                name = name + " | " + p.departement_id.name
            p.name = name

    def get_name(self):
        name = ""
        if self.product_id.name is not False:
            name = name + self.product_id.name
        if self.couleur_id.name is not False:
            name = name + " (" + self.couleur_id.name + " )"
        if self.fonction_id.name is not False:
            name = name + " | " + self.fonction_id.name
        if self.departement_id.name is not False:
            name = name + " | " + self.departement_id.name
        return name

class Netline_liste_prix(models.Model):
    _name = 'netline.liste_prix'
 
    client_id = fields.Many2one("res.partner", 'Client')
    client_name = fields.Char(related='client_id.name', store=True)
    product_id = fields.Many2one("product.product", 'Produit',  domain="['|',('is_laundry', '=', True),('is_vt','=',True)]")
    prix = fields.Float(string="Prix Produit")
     

    def name_get(self):
        res = []
        #designation_client, designation, type, couleur
        for rec in self:
            name = rec.name
            res.append((rec.id, name))
        return res
 
        product = super(Netline_liste_prix, self).create(values);
        return product


class Netline_product_taille(models.Model):
    _name = 'netline.product.taille'
    
    name = fields.Char("Nom", required=True)
    product_id = fields.One2many('netline.product', 'taille_id', string="Taille")

class Netline_product_couleur(models.Model):
    _name = 'netline.product.couleur'
    _order = 'name'
    _sql_constraints =[('product_couleur_constraint', 'UNIQUE (name)', 'Cette couleur existe déja !')]

    name = fields.Char("Nom", required=True)
    product_id = fields.One2many('netline.product', 'couleur_id', string="Couleur")
    state = fields.Selection([('nok', 'Non validé'), ('ok', 'Validé'), ('annule', 'Annulé')], required=True, default='nok')

    def set_valide(self):
        self.state="ok"

    def set_annule(self):
        self.state="annule"

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search((args+[('name', 'ilike', name)]),
                               limit=limit)
        if not recs:
            recs = self.search([('name', operator, name)] + args, limit=limit)
        return recs.name_get()

class Netline_product_matiere(models.Model):
    _name = 'netline.product.matiere'
    _sql_constraints =[('product_matiere_constraint', 'UNIQUE (name)', 'Cette matiere existe déja !')]

    name = fields.Char("Nom", required=True)
    state = fields.Selection([('nok', 'Non validé'), ('ok', 'Validé'), ('annule', 'Annulé')], required=True, default='nok')
    product_id = fields.One2many('netline.product', 'matiere_id', string="Matière")

    def set_valide(self):
        self.state="ok"

    def set_annule(self):
        self.state="annule"

class Netline_product_composition(models.Model):
    _name = 'netline.product.composition'
    _sql_constraints =[('product_composition_constraint', 'UNIQUE (name)', 'Cette composition existe déja !')]

    name = fields.Char("Nom", required=True)
    state = fields.Selection([('nok', 'Non validé'), ('ok', 'Validé'), ('annule', 'Annulé')], required=True, default='nok')
    product_id = fields.One2many('netline.product', 'composition_id', string="Composition")

    def set_valide(self):
        self.state="ok"

    def set_annule(self):
        self.state="annule"

class Netline_product_marque(models.Model):
    _name = 'netline.product.marque'
    _sql_constraints =[('product_marque_constraint', 'UNIQUE (name)', 'Cette marque existe déja !')]

    name = fields.Char("Nom", required=True)
    product_id = fields.One2many('netline.product', 'marque_id', string="Marque")

class Netline_product_type(models.Model):
    _name = 'netline.product.type'
    
    name = fields.Char(string="Nom du type", required=True)
    product_id = fields.One2many('netline.product', "type_id", string="Type")

class Netline_vt_departement(models.Model):
    _name = 'netline.vt_product.departement'
    
    name = fields.Char(string="Departement", required=True)
    product_id = fields.One2many('netline.vt_product', "departement_id", string="depart_id")
    n_line = fields.Integer("Numéro ligne")


class Netline_vt_fonction(models.Model):
    _name = 'netline.vt_product.fonction'

    name = fields.Char(string="Fonction", required=True)
    product_id = fields.One2many('netline.vt_product', "fonction_id", string="fonction_id")


class Netline_porteur(models.Model):
    _name="netline.porteur"

    n_porteur = fields.Char(string="N° Porteur")
    client_id = fields.Many2one('res.partner', "Client")
    nom = fields.Char(string="Nom")
    prenom = fields.Char(string="Prenom")
    product_ids = fields.Many2many('netline.vt_product', 'porteur_ids')
