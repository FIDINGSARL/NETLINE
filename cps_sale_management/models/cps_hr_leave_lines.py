# # -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import date, datetime, timedelta



class CpsHrLeaveLine(models.Model):

    _name = 'cps.hr.leave.line'

    leave_id = fields.Many2one('cps.hr.leave', 'Leave id')
    employee_id = fields.Many2one('hr.employee', string="Employee")
    matricule= fields.Char(related='employee_id.matricule')
    horaire_id = fields.Many2one('cps.hr.horaire', 'Horaire')
    leave_type = fields.Many2one('hr.leave.type', 'Motif')
