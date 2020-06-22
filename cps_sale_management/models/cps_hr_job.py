# # -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import date, datetime, timedelta



class CpsHrJob(models.Model):

    _inherit = 'hr.job'
    _description = "HR Job"
    type_poste = fields.Selection([('direct', 'Direct'), ('indirect', 'Indirect')], string='Direct/Indirect', default='direct')
