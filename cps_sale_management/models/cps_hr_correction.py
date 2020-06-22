# # -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import date, datetime, timedelta
import pytz
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DF

class CpsHrCorrection(models.Model):

    _name = 'cps.hr.correction'

    date_correction = fields.Date('Journée pointage')
    societe_id = fields.Many2one('cps.hr.societe','Société')
    equipe = fields.Selection([('A', 'A'), ('B', 'B'), ('FM', 'FM'), ('FA', 'FA')], string='Equipe salarié')
    department_id = fields.Many2one('hr.department','Département')

    is_absents = fields.Boolean('Est absent')
    horaire_id = fields.Many2one('cps.hr.horaire', 'Horaire')

    attendance_ids = fields.One2many('hr.attendance', 'correction_id', string='Pointages')

    def action_filter_attendances(self):
        attendances = self.env['hr.attendance'].search([("correction_id", "=", False)])
        # print ('employees------------------------', self.attendance_ids.employee_id)
        ids=[]
        for attendance in attendances.filtered(lambda a: a.check_in.strftime('%Y-%m-%d') == self.date_correction.strftime('%Y-%m-%d')):
            # print ('attendances------------------------', attendance.check_in.strftime('%Y-%m-%d'))
            self.attendance_ids += attendance
        employees = self.env['hr.employee'].search([])
        # print ('employees---------------------------', employees)
        for employee in employees:
            # print ('employees------------------------', employee)
            if employee not in self.attendance_ids.employee_id:
                self.env['hr.attendance'].create({'employee_id' : employee.id,
                                                  'check_in' : datetime.now(),
                                                  'check_out' : datetime.now(),
                                                  'correction_id' : self.id
                                                  })
    def action_appliquer_horaire(self):
        for attendance in self.attendance_ids:
            if attendance.worked_hours>0:
                attendance.horaire_id=self.horaire_id.id
                check_in_modified = None
                check_out_modified = None
                attendance.checkin_anomalie=""
                attendance.checkout_anomalie=""
                if attendance.checkin_corriged:
                    attendance.write({'check_in' : attendance.checkin_corriged, 'check_out' : attendance.checkout_corriged})
                if attendance.check_in:
                    check_in = datetime.strptime(attendance.check_in.strftime('%H:%M:%S'), '%H:%M:%S')# + timedelta(hours=1)
                    check_in_horaire = datetime.strptime(attendance.horaire_id.horaire_debut.strftime('%H:%M:%S'),'%H:%M:%S')# + timedelta(hours=1)
                    diff_in = (check_in-check_in_horaire).total_seconds()/60
                    if not attendance.checkin_corriged:
                        attendance.checkin_corriged = attendance.check_in
                    check_in_modified = attendance.check_in
                    if diff_in >= 60 or diff_in < -30:
                        attendance.checkin_anomalie= "abnormal_checkin"
                    if diff_in > 10 and diff_in<60:
                        attendance.checkin_anomalie= "late"
                    if diff_in < 0 and diff_in>=-30:
                        if attendance.check_in!=attendance.horaire_id.horaire_debut:
                            check_in_modified= datetime.strptime(self.date_correction.strftime('%Y-%m-%d') + " " + attendance.horaire_id.horaire_debut.strftime('%H:%M:%S'), '%Y-%m-%d %H:%M:%S')
                        attendance.checkin_anomalie= "chekin_before_time"
                if attendance.check_out:
                    horaire_j_plus_1 = True
                    if datetime.strptime(attendance.horaire_id.horaire_fin.strftime('%Y-%m-%d'),'%Y-%m-%d') == datetime.strptime(attendance.horaire_id.horaire_debut.strftime('%Y-%m-%d'), '%Y-%m-%d'):
                        horaire_j_plus_1 =False
                    if not horaire_j_plus_1:
                        check_out_horaire = datetime.strptime(self.date_correction.strftime('%Y-%m-%d') + " " + attendance.horaire_id.horaire_fin.strftime('%H:%M:%S'),'%Y-%m-%d %H:%M:%S')# + timedelta(hours=1)
                    else:
                        day_out_horaire = datetime.strptime(self.date_correction.strftime('%Y-%m-%d'),'%Y-%m-%d') + timedelta(days=1)
                        check_out_horaire = datetime.strptime(day_out_horaire.strftime('%Y-%m-%d') + " " + attendance.horaire_id.horaire_fin.strftime('%H:%M:%S'),'%Y-%m-%d %H:%M:%S')# + timedelta(hours=1)
                    check_out = datetime.strptime(attendance.check_out.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S') #+ timedelta(hours=1)
                    diff_out = (check_out-check_out_horaire).total_seconds()/60
                    if not attendance.checkout_corriged:
                        attendance.checkout_corriged = attendance.check_out
                    check_out_modified = attendance.check_out
                    if diff_out<0:
                        attendance.checkout_anomalie= "chekout_before_time"
                    if diff_out>0 and diff_out<=40:
                        attendance.checkout_anomalie= "chekout_after_time"
                        if not horaire_j_plus_1:
                            check_out_modified= datetime.strptime(attendance.check_out.strftime('%Y-%m-%d') + " " + attendance.horaire_id.horaire_fin.strftime('%H:%M:%S'), '%Y-%m-%d %H:%M:%S')
                        else:
                            day_out = datetime.strptime(attendance.check_in.strftime('%Y-%m-%d'),'%Y-%m-%d') + timedelta(days=1)
                            check_out_modified = datetime.strptime(day_out.strftime('%Y-%m-%d') + " " + attendance.horaire_id.horaire_fin.strftime('%H:%M:%S'),'%Y-%m-%d %H:%M:%S')
                    if diff_out>40:
                        attendance.checkout_anomalie= "abnormal_checkout"
                if check_in_modified and check_out_modified:
                    attendance.write({'check_in' : check_in_modified, 'check_out' : check_out_modified})
            else:
                # print('absence----------------!!!!')
                attendance.checkin_anomalie = "absence"
                attendance.checkout_anomalie = "absence"

    def write(self, vals):
        attendance = super(CpsHrCorrection, self).write(vals)
        # self.action_appliquer_horaire()
        return attendance
