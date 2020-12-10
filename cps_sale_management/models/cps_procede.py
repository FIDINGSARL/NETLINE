# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import UserError, AccessError

# modules consomation energie

class FicheProcede(models.Model):
    _name = "fiche.procede"
    _order = 'traitement_sequence,version'
    _description = 'Liste des fiches procédés'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("name", compute="compute_name", store=True)
    poids_article = fields.Float(related='template_id.poids', string='Poids article')
    pantone_id = fields.Many2one('cps.pantone', 'Pantone')
    pantone_code = fields.Char(related='pantone_id.code_pantone', string='Code pantone')
    pantone_name = fields.Char(related='pantone_id.name', string = 'Désign. pantone')
    # pantone_categ = fields.Selection(related='pantone_id.type_couleur', string = 'Catégorie pantone', selection=[('clair', 'Clair'), ('pastel', 'Pastel'), ('moyen', 'Moyen'), ('fonce', 'Foncé'), ('tfonce', 'Trés foncé') ])
    poids_machine = fields.Float(String="Poids machine (kg)", required=True)
    qte_machine = fields.Integer(String="Quantité")
    procede_line_ids = fields.One2many('fiche.procede.line', "procede_id", string="Lignes de la fiche procédé")
    mrp_bom_line_ids = fields.One2many('mrp.bom.line', "procede_id", string="Lignes de nomenclature")
    type_teinture = fields.Selection(string="Type Teinture", selection=[('reactif', 'Réactif'),
                                                                     ('direct', 'Direct'),
                                                                     ('sulfu', 'Sulfurisé'),
                                                                     ('pigment', 'Pigmentaire'),
                                                                     ('autre', 'Autre'),
                                                                     ])

    create_uid = fields.Many2one('res.users', string="Crée par")
    template_id = fields.Many2one('cps.product.template', string="Template")
    echantillon_id = fields.Many2one('cps.product.echantillon', string="Echantillon")
    production_id = fields.Many2one('cps.product.production', string="Production")
    traitement_id = fields.Many2one('cps.product.traitement', 'Traitement', required=True)
    mrp_routing_workcenter_id = fields.Many2one('mrp.routing.workcenter', 'Opération Odoo')

    section = fields.Char(related='traitement_id.section_id.name', string='Section')
    liste_traitement_id = fields.One2many('cps.product.traitement.liste', 'fiche_procede_id', string="Liste de traitements")
    traitement_sequence = fields.Integer()
    version = fields.Integer(String="Version")

    def open_line(self):
        return {
            'name': 'Fiche procédé',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'fiche.procede',
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'target': 'current'
        }

    @api.model
    def create(self, values):
        procede = super(FicheProcede, self).create(values)
        procede.compute_procede_lines()
        if procede.pantone_id is not False :
            procede.echantillon_id.pantone_id = procede.pantone_id.id
        return procede

    def write(self, values):
        procede = super(FicheProcede, self).write(values)
        self.compute_procede_lines()
        # print('values--------------------', values)
        if self.pantone_id is not False :
            self.template_id.pantone_id = self.pantone_id.id
        if self.template_id.id is not False and self.template_id.product_id.id is not False:
            # print ('lines----------------------', len(self.procede_line_ids))
            if len(self.procede_line_ids)>0:
                self.template_id.create_bom()
            # bom = self.template_id.create_bom()
            # for traitement in self.template_id.traitement_ids:
            #     self.template_id.create_bom_line(bom, traitement.traitement_id, self)
            # self.template_id.create_route(self.template_id)
            self.template_id.create_route_with_time(self.template_id)

        return procede

    # def generate_bom_line(self, bom_id, workcenter_id, fiche_procede):
    #     valJouleToFueloilequivalent = 41000000
    #     valKwHVapeurSecadora = 187.5
    #     tempsCentrifuge = 40
    #     tempsSechage = 40
    #     valKWHSecadora = 19
    #     valKWHCentrifuge = 16
    #     valKWHMachine = 16
    #     quimicos =[]
    #     total_eau = 0
    #     total_kcal = 0
    #     total_temps = 0
    #     line_value=({})
    #
    #     print('workcenter id procede----------------------------', workcenter_id)
    #     print('procede----------------------------', fiche_procede)
    #     for procedeline in fiche_procede.procede_line_ids:
    #         if len(procedeline.quimicos)>0:
    #             trouve=False
    #             for quimico in quimicos:
    #                 if quimico['product_id'] == procedeline.quimicos.id:
    #                     quimico['product_qty']+= procedeline.dosification
    #                     trouve=True
    #             if trouve==False:
    #                 line_value = ({
    #                         'product_id': procedeline.quimicos.id,
    #                         'product_qty': procedeline.dosification,
    #                     })
    #                 quimicos.append(line_value)
    #         total_eau+=procedeline.eau/1000
    #         total_kcal+=procedeline.kcal
    #         total_temps+=procedeline.temps
    #
    #     fuel_lavage_teinture = (total_kcal * total_eau * 1000 / valJouleToFueloilequivalent)
    #     fuel_sechage = ((valKwHVapeurSecadora * (tempsSechage / 60)) / 11.2) * 1.3
    #     electricite_lavage_teinture = total_temps / 60 * valKWHMachine
    #     electricite_centrifuge = tempsCentrifuge / 60 * valKWHCentrifuge
    #     electricite_sechage = tempsSechage / 60 * valKWHSecadora
    #
    #     print ('quimicos---------------------------', quimicos)
    #     for quimico in quimicos:
    #         mrp_bom_line = self.env['mrp.bom.line'].create({
    #             'bom_id': bom_id,
    #             'procede_id': self.id,
    #             'product_id': quimico['product_id'],
    #             'product_qty': quimico['product_qty']/self.qte_machine,
    #             'operation_id': workcenter_id
    #         })
    #
    #     if self.qte_machine > 0 and total_eau > 0:
    #         product_eau = self.env['product.product'].search([('default_code', '=', 'EAU')])
    #         mrp_bom_line = self.env['mrp.bom.line'].create({
    #             'bom_id': bom_id,
    #             'procede_id': self.id,
    #             'product_id': product_eau.id,
    #             'product_qty': total_eau / self.qte_machine,
    #             'operation_id': workcenter_id
    #         })
    #         product_fuel = self.env['product.product'].search([('default_code', '=', 'FUEL')])
    #         mrp_bom_line = self.env['mrp.bom.line'].create({
    #             'bom_id': bom_id,
    #             'procede_id': self.id,
    #             'product_id': product_fuel.id,
    #             'product_qty': (fuel_lavage_teinture + fuel_sechage) / self.qte_machine,
    #             'operation_id': workcenter_id
    #         })
    #         product_electricite = self.env['product.product'].search([('default_code', '=', 'ELEC')])
    #         mrp_bom_line = self.env['mrp.bom.line'].create({
    #             'bom_id': bom_id,
    #             'procede_id': self.id,
    #             'product_id': product_electricite.id,
    #             'product_qty': (electricite_lavage_teinture + electricite_centrifuge + electricite_sechage) / self.qte_machine,
    #             'operation_id': workcenter_id
    #         })
    #     produit_charges_fixes = self.env['product.product']
    #     if self.template_id.type_de_traitement=='delavage':
    #         produit_charges_fixes = self.env['product.product'].search([('default_code', '=', 'FIXES DEL')])
    #     if self.template_id.type_de_traitement=='teinture':
    #         produit_charges_fixes  = self.env['product.product'].search([('default_code', '=', 'FIXES TEIN')])
    #     if self.template_id.type_de_traitement=='ts':
    #         produit_charges_fixes  = self.env['product.product'].search([('default_code', '=', 'FIXES TS')])
    #
    #     if len(produit_charges_fixes)>0:
    #         mrp_bom_line = self.env['mrp.bom.line'].create({
    #             'bom_id' : bom_id,
    #             'procede_id': self.id,
    #             'product_id': produit_charges_fixes.id ,
    #             'product_qty': 1,
    #             'operation_id' : workcenter_id
    #         })


    # @api.onchange('procede_line_ids')
    # def compute_line(self):
    #     for p in self.procede_line_ids:
    #         p.poids_machine_ligne = self.poids_machine

    @api.depends("qte_machine")
    @api.onchange('qte_machine')
    def compute_qte(self):
        self.poids_machine = (self.qte_machine * self.poids_article)
        self.compute_procede_lines()
        # for ligne_procede in self.procede_line_ids:
        #     ligne_procede.compute_ligne_procede()
        #     ligne_procede.compute_ligne_procede_eau()
        #     ligne_procede.compute_ligne_procede_grkg()

    @api.depends("poids_machine")
    @api.onchange('poids_machine')
    def compute_poids(self):
        for procede_line in self.procede_line_ids:
            procede_line.compute_ligne_procede_rb()
            procede_line.compute_ligne_procede_dosification()
        if self.poids_article>0:
            self.qte_machine = (self.poids_machine / self.poids_article)

    def _compute_qte_machine(self):
        for p in self:
            if p.poids_article > 0:
                p.qte_machine = (p.poids_machine / p.poids_article)

    def name_get(self):
        res = []
        #designation_client, designation, type, couleur
        for p in self:
            name = ""
            if p.pantone_id.name is not False:
                name = name + p.pantone_id.name + " - "
            if p.traitement_id.name is not False:
                name = name + p.traitement_id.name
            if p.version is not False and p.version>0:
                name = name + " v." + str(p.version)
            if p.template_id.name is not False:
                name = name + " (" + p.template_id.name + ")"
            res.append((p.id, name))
        return res

    @api.depends('pantone_id','traitement_id','template_id', 'version')
    def compute_name(self):
        res = []
        #designation_client, designation, type, couleur
        for p in self:
            name = ""
            if p.pantone_id.name is not False:
                name = name + p.pantone_id.name + " - "
            if p.traitement_id.name is not False:
                name = name + p.traitement_id.name
            if p.version is not False and p.version>0:
                name = name + " v." + str(p.version)
            if p.echantillon_id.name is not False:
                name = name + " (Echan. " + p.echantillon_id.name + ")"
            if p.production_id.name is not False:
                name = name + " (Prod. " + p.production_id.name + ")"
            p.name=name

    def compute_procede_lines(self):
        eauEnCours = 0
        for procede_line in self.procede_line_ids:
            if procede_line.eau>0:
                eauEnCours = procede_line.eau
            # print ('mode calcul--------------------------', procede_line.mode_calcul)
            if procede_line.mode_calcul is not False:
                if procede_line.mode_calcul=="gkg":
                    procede_line.dosification = procede_line.gkg * self.poids_machine * 10 / 1000
                elif procede_line.mode_calcul=="gltr":
                    procede_line.dosification = procede_line.gltr * eauEnCours / 1000
                elif procede_line.mode_calcul == "dosification":
                    if procede_line.gltr > 0:
                        procede_line.gltr =  procede_line.dosification/(eauEnCours/1000)
                    elif procede_line.gkg > 0:
                        procede_line.gkg = procede_line.dosification/(self.poids_machine * 10 / 1000)
            else:
                if procede_line.gltr>0:
                    if eauEnCours>0:
                        procede_line.dosification = procede_line.gltr * eauEnCours/1000
                if procede_line.gkg>0:
                    procede_line.dosification = procede_line.gkg * self.poids_machine * 10 / 1000
            # if procede_line.gltr > 0:
            #     if eauEnCours > 0:
            #         procede_line.gltr = procede_line.dosification / (eauEnCours / 1000)
            # if procede_line.gkg > 0:
            #     if self.poids_machine > 0:
            #         procede_line.gkg = procede_line.dosification / (self.poids_machine * 10 / 1000)
            if procede_line.temperature> 20:
               procede_line.kcal=(procede_line.temperature-20)*4185
            else:
                procede_line.kcal=0