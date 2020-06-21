from odoo import models, fields, api

class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    is_client_principal = fields.Boolean("Est un client principal", default=False)
    is_atelier = fields.Boolean("Est un Atelier", default=False)
    liste_echantillon_client_ids = fields.One2many('cps.product.echantillon', 'client_id')
    liste_echantillon_client_principal_ids = fields.One2many('cps.product.echantillon', 'client_principal_id', string="Atelier")
    numero_ice = fields.Char("Numéro ICE")
    numero_rc = fields.Char("Numéro RC")
    numero_if = fields.Char("Numéro IF")
    numero_cnss = fields.Char("Numéro CNSS")
    numero_tp = fields.Char("Numéro TP")
    payment_journal_id = fields.Many2one('account.journal','Banque paiement',domain="[('type', '=', 'bank')]")

