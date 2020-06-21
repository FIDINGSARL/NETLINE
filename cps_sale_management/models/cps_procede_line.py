# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import date
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, AccessError

class FicheProcedeLine(models.Model):
    _name = 'fiche.procede.line'
    _order = 'sequence, id'
    _description = 'Liste des lignes des fiches procédés'

    procede_id = fields.Many2one('fiche.procede', 'Fiche procédé', store=True)
    sequence = fields.Integer(string='Sequence', default=1)
    #phase_id= fields.Many2one('fiche.procede.line.phase', 'Phase')
    traitement = fields.Char(related='procede_id.traitement_id.name', string='Traitement')
    section = fields.Char(related='procede_id.section', string='Section')
    etape_id= fields.Many2one('fiche.procede.line.etape', 'Etape')
    #operation_id = fields.Many2one('fiche.procede.line.operation', 'Opération')
    temps = fields.Integer('Durée')
    rb = fields.Float(string='R.B.')
    eau = fields.Integer(string='Qté eau (l)',store=True)
    temperature = fields.Integer('Température')
    kcal = fields.Integer(string='kcal')
    rotationDroite = fields.Integer('Rotation droite')
    rotationGauche = fields.Integer('Rotation gauche')
    vitesse = fields.Integer('Vitesse')
   # valeur  = fields.Char('Valeur')
    quimicos = fields.Many2one('product.product', string="Nom produit", domain="[('categ_id', 'child_of', 3344)]")
    # quimicos = fields.Many2one('product.product', string="Nom produit", domain="[('categ_id', 'child_of', 3)]")
    utilisation = fields.Char(related='quimicos.categ_id.name', string='Fonction')
    unite_mesure = fields.Char(related='quimicos.uom_id.name', string='Unité', store=True)
    gltr = fields.Float(string='g/l',digits='Recette precision')
    gkg = fields.Float(string='%kg',digits='Dosification')
    dosification = fields.Float(string='Dosification',digits='Dosification', store=True)
    mode_calcul = fields.Char('Mode calcul')
    # @api.onchange('quimicos')
    # def change_type_article(self):
    #     cat = self.env['res.config.settings'].get_cat_mere_pc()
    #     cats = self.env['product.category'].search([("id", "child_of", cat.id)])
    #     pcs = self.env['product.product'].search([('categ_id', 'in', cats.ids)])
    #     ids = []
    #     for pc in pcs:
    #         ids.append(pc.id)
    #     return {'domain': {'quimicos': [('id', 'in', ids)]}}
    #
    #
    # @api.depends("eau")
    # @api.onchange("eau")
    # def compute_ligne_procede_eau(self) :
    #     for p in self:
    #         if p.traitement is not False:
    #             if p.poids_machine_ligne > 0 :
    #                 p.rb = p.eau / p.poids_machine_ligne
    #
    # @api.depends("temperature", "poids_machine_ligne")
    # @api.onchange("temperature", "poids_machine_ligne")
    # def compute_ligne_procede(self):
    #     for p in self:
    #         if p.temperature> 25:
    #            p.kcal=(p.temperature-25)*p.rb * p.poids_machine_ligne*0.45448
    #         else:
    #             p.kcal=0
    #
    # @api.onchange("rb")
    # def compute_line_rb(self):
    #     self.eau = self.rb * self.poids_machine_ligne
    #     # Recuperer l'id de la fiche procede a partir du contexte
    #     procede_id = self._context.get('params').get('id')
    #     print ('context-----------------------------------------', self._context)
    #     # Recuperer l'eau de la derniere ligne qui précéde la ligne en cours et qui contient l'eau enregistrée
    #     next_lines = self.env['fiche.procede.line'].search([("procede_id", "=", procede_id), ("sequence", ">=", self.sequence)], order='sequence')
    #     print ('next lines-----------------------------------------', next_lines)
    #
    # @api.depends("gltr")
    # @api.onchange("gltr")
    # def compute_ligne_procede_grltr(self):
    #     for p in self:
    #         if p.traitement is not False:
    #             if p.gltr > 0 :
    #                 p.gkg = 0
    #                 if p.eau>0:
    #                     eau = p.rb * p.poids_machine_ligne/1000
    #                 else:
    #                     #Recuperer l'id de la fiche procede a partir du contexte
    #                     procede_id = self._context.get('params').get('id')
    #                     print ('context-----------------------------------------', self._context)
    #                     #Recuperer l'eau de la derniere ligne qui précéde la ligne en cours et qui contient l'eau enregistrée
    #                     last_line = self.env['fiche.procede.line'].search([("procede_id", "=", procede_id),("eau", ">", 0),("sequence", "<=", self.sequence)], order='sequence desc', limit=1)
    #                     eau = last_line.eau/1000
    #                     #Parcourir le contexte pour recuprer l'eau de la derniere ligne qui précéde la ligne en cours et qui est non enregistrée
    #                     for new_line in self._context.get('values'):
    #                         #S'il y'a des modifications ou création de lignes
    #                         if new_line[2] is not False:
    #                             #Si la ligne contient de l'eau
    #                             if 'eau' in new_line[2]:
    #                                 if new_line[2].get('eau')>0:
    #                                     #Si la ligne vient d'etre créée
    #                                     if "virtual" in str(new_line[1]):
    #                                         #Verifier si la ligne précéde bien la ligne en cours et qu'elle est aprés la ligne enregistré (d'ou on vient de recuperer l'eau a la premiere etape)
    #                                         if new_line[2].get('sequence') >= last_line.sequence and new_line[2].get('sequence') <= self.sequence:
    #                                             eau = new_line[2].get('eau')/1000
    #                                     #Si la ligne vient d'etre modifié
    #                                     else:
    #                                         #Le chercher pour pouvoir recuperer sa sequence
    #                                         modified_line = self.env['fiche.procede.line'].search([("id", "=", new_line[1])])
    #                                         #Verifier si la ligne précéde bien la ligne en cours et qu'elle est aprés la ligne enregistré (d'ou on vient de recuperer l'eau a la premiere etape)
    #                                         if modified_line.sequence>= last_line.sequence and modified_line.sequence <= self.sequence:
    #                                             eau = new_line[2].get('eau')/1000
    #                 print ('eau--------------------------------------', eau)
    #                 p.dosification = p.gltr * eau
    #             else:
    #                 if p.gkg==0:
    #                     p.dosification=0
    #

    #
    # @api.depends("dosification")
    # @api.onchange("dosification")
    # def compute_ligne_procede_dosification(self):
    #     for p in self:
    #         if p.traitement is not False:
    #             if p.dosification>0:
    #                 if p.gkg > 0:
    #                     if p.poids_machine_ligne >0:
    #                         p.gkg = p.dosification / (p.poids_machine_ligne * 10 / 1000)
    #                 if p.gltr > 0:
    #                     if p.rb * p.poids_machine_ligne>0:
    #                         p.gltr = p.dosification / (p.rb * p.poids_machine_ligne/1000)
    #             else:
    #                 p.gltr=0
    #                 p.gkg=0



    @api.depends("gkg")
    @api.onchange("gkg")
    def compute_ligne_procede_grkg(self):
        self.gltr=0
        self.dosification = 0
        self.mode_calcul="gkg"
        self.procede_id.compute_procede_lines()

    @api.depends("gltr")
    @api.onchange("gltr")
    def compute_ligne_procede_grltr(self):
        self.gkg=0
        self.dosification = 0
        self.mode_calcul="gltr"
        self.procede_id.compute_procede_lines()

    @api.depends("dosification")
    @api.onchange("dosification")
    def compute_ligne_procede_dosification(self):
        if self.gkg==0 and self.gltr==0 and self.dosification>0:
            raise UserError(_("Merci de choisir le mode de grammage !"))
        self.mode_calcul="dosification"
        self.procede_id.compute_procede_lines()

    @api.depends("rb")
    @api.onchange("rb")
    def compute_ligne_procede_rb(self):
        self.eau = self.rb * self.procede_id.poids_machine
        self.procede_id.compute_procede_lines()

    @api.depends("eau")
    @api.onchange("eau")
    def compute_ligne_procede_eau(self):
        if self.procede_id.poids_machine> 0:
            self.rb = self.eau / self.procede_id.poids_machine
        self.procede_id.compute_procede_lines()

