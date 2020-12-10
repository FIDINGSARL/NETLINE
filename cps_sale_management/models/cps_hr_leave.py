# # -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import date, datetime, timedelta



class CpsHrLeave(models.Model):

    _name = 'cps.hr.leave'

    date_absence = fields.Date('Journée pointage')
    leave_lines = fields.One2many('cps.hr.leave.line', 'leave_id', string="Employee")

    def action_filter_attendances(self):
        employees = self.env['hr.employee'].search([])
        colis = []
        for employee in employees:
            trouve=False
            for attendance in employee.attendance_ids.filtered(lambda a: a.check_in.strftime('%Y-%m-%d') == self.date_absence.strftime('%Y-%m-%d')):
                print ('Mat', employee.matricule, '  pointage--------------------', attendance.check_in)
                trouve=True
            if trouve == False:
                colis.append((0, 0, {'leave_id': self.id, 'employee_id': employee.id}))
        self.leave_lines = colis

    def action_valider_absence(self):
        for leave_line in self.leave_lines:
            if len(leave_line.leave_type)>0:
                print('leave id--------------------------------', leave_line.leave_type.name)
                leave = self.env['hr.leave'].create({
                    'holiday_type': 'employee',
                    'employee_id': leave_line.employee_id.id,
                    'request_date_from': self.date_absence,
                    'request_hour_from': str(leave_line.horaire_id.horaire_debut.hour+1),
                    'request_hour_to': str(leave_line.horaire_id.horaire_fin.hour+1),
                    'date_from': str(self.date_absence.strftime('%Y-%m-%d')) + " " + str(leave_line.horaire_id.horaire_debut.strftime('%H:%M:%S')),
                    'date_to': str(self.date_absence.strftime('%Y-%m-%d')) + " " + str(leave_line.horaire_id.horaire_fin.strftime('%H:%M:%S')),
                    'request_unit_hours' : True,
                    'holiday_status_id':leave_line.leave_type.id
                })
                leave.action_approve()
                leave.action_validate()

