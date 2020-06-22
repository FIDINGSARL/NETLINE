from odoo import models, fields, api

class CpsProductPantone(models.Model):
    _name = 'cps.pantone'
    _order = 'name'
    _description = 'Liste des codes pantones'
    _sql_constraints =[('pantone_constraint', 'UNIQUE (code_pantone)', 'Ce code pantone existe déja !')]

    name = fields.Char("name", compute="compute_name", store=True)
    code_pantone = fields.Char("Code pantone")
    page_pantone = fields.Integer('Page pantone')
    couleur_id = fields.Many2one('cps.product.couleur', 'Couleur')
    type_couleur = fields.Selection(string="Type couleur", selection=[('clair', 'Clair'), ('pastel', 'Pastel'), ('moyen', 'Moyen'), ('fonce', 'Foncé'), ('tfonce', 'Trés foncé') ])
    state = fields.Selection([('nok', 'Non validé'), ('ok', 'Validé'), ('annule', 'Annulé')], required=True, default='nok')
    echantillon_ids = fields.One2many('cps.product.echantillon', 'pantone_id', string="Echantillons")

    def set_valide(self):
        self.state="ok"

    def set_annule(self):
        self.state="annule"


    @api.depends( 'code_pantone', 'type_couleur', 'page_pantone')
    def compute_name(self):
        recs = []
        for p in self:
            name = ""
            if p.code_pantone is not False:
                name = name + p.code_pantone + " - "
            if p.page_pantone is not False:
                name = name + "p. " + str(p.page_pantone) + " - "
            if p.couleur_id.name is not False:
                name = name + p.couleur_id.name + " - "
            if p.type_couleur is not False:
               name = name + p.type_couleur + " - "
            if len(name) > 0:
                name = name[:-3]
            p.name = name


    def name_get(self):
        res = []
        #designation_client, designation, type, couleur
        for p in self:
            name = ""
            if p.code_pantone is not False:
                name = name + p.code_pantone + " - "
            if p.couleur_id.name is not False:
                name = name + p.couleur_id.name + " - "
            if p.type_couleur is not False:
                name = name + p.type_couleur + " - "
            if len(name) > 0:
                name = name[:-3]
            res.append((p.id, name))
        return res