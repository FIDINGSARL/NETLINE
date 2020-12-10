# # -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_round
from datetime import date, datetime, timedelta


class CpsHrAttendance(models.Model):

    _inherit = 'hr.attendance'

    matricule = fields.Char(related="employee_id.matricule", string='Matricule')
    horaire_id = fields.Many2one('cps.hr.horaire', 'Horaire')
    # checkin_horaire = fields.Datetime(related="horaire_id.horaire_debut", string='Horaire entrée')
    checkin_corriged = fields.Datetime('Entrée orig.')
    checkin_anomalie = fields.Selection(string='An. Entrée', selection=[('chekin_before_time', 'Entrée avant heure'), ('late', 'Retard'), ('abnormal_checkin', 'Entrée anormale'), ('absence', 'absence')])
    # checkout_horaire = fields.Datetime(related="horaire_id.horaire_fin", string='Horaire sortie')
    checkout_corriged = fields.Datetime('Sortie orig.')
    checkout_anomalie = fields.Selection(string='An. Sortie', selection=[('chekout_before_time', 'Sortie avant heure'), ('chekout_after_time', 'Sortie aprés heure'), ('abnormal_checkout', 'Sortie anormale'), ('absence', 'absence')])
    correction_id = fields.Many2one('cps.hr.correction', 'N° Correction')
    hn = fields.Float('HN')
    h_25 = fields.Float('H25')
    h_50 = fields.Float('H50')
    h_100 = fields.Float('H100')
    is_absent = fields.Boolean('Est absent')

    @api.depends('check_in', 'check_out')
    def _compute_worked_hours(self):
        for attendance in self:
            if attendance.check_out:
                delta = attendance.check_out - attendance.check_in
                attendance.worked_hours = delta.total_seconds() / 3600.0
                print ('attendance.worked_hours-------------------------', attendance.worked_hours%2)
                decimal_value = (attendance.worked_hours%2)
                if decimal_value>1:
                    if decimal_value-1<=0.25:
                        attendance.hn = attendance.worked_hours - (decimal_value-1) + 0
                    elif decimal_value-1<=0.5:
                        attendance.hn = attendance.worked_hours - (decimal_value-1) + 0.25
                    elif decimal_value - 1 <= 0.75:
                        attendance.hn = attendance.worked_hours - (decimal_value - 1) + 0.5
                    elif decimal_value - 1 > 0.75:
                        attendance.hn = attendance.worked_hours - (decimal_value - 1) + 0.75
                if len(self.correction_id) > 0:
                    if len(self.horaire_id) > 0:
                        print('self.horaire_id.duree_pause----------------------------------------', self.horaire_id.duree_pause)
                        if attendance.hn>4:
                            attendance.hn -= self.horaire_id.duree_pause
                attendance.h_25 = 0
                if attendance.hn>10:
                    attendance.h_25 = attendance.hn-10
                    attendance.hn=10
            else:
                attendance.worked_hours = False

    def write(self, values):
        attendance = super(CpsHrAttendance, self).write(values)
        if 'is_absent' in values:
            if values['is_absent']:
                self.employee_id.is_absents=True
        return attendance

    def action_appliquer_horaire(self):

        check_in = datetime.strptime(self.correction_id.date_correction.strftime('%Y-%m-%d') + " " + self.correction_id.horaire_id.horaire_debut.strftime('%H:%M:%S'), '%Y-%m-%d %H:%M:%S')
        check_out = datetime.strptime(self.correction_id.date_correction.strftime('%Y-%m-%d') + " " + self.correction_id.horaire_id.horaire_fin.strftime('%H:%M:%S'), '%Y-%m-%d %H:%M:%S')
        # print ('check_out--------------------------------', check_out)
        if datetime.strptime(self.correction_id.horaire_id.horaire_fin.strftime('%Y-%m-%d'), '%Y-%m-%d') == datetime.strptime(self.correction_id.horaire_id.horaire_debut.strftime('%Y-%m-%d'), '%Y-%m-%d'):
            day_out_horaire = datetime.strptime(self.correction_id.date_correction.strftime('%Y-%m-%d'), '%Y-%m-%d') + timedelta(days=1)
            check_out = datetime.strptime(day_out_horaire.strftime('%Y-%m-%d') + " " + self.correction_id.horaire_id.horaire_fin.strftime('%H:%M:%S'), '%Y-%m-%d %H:%M:%S')
        self.write({'check_in': check_in, 'check_out': check_out})
        # self.correction_id.action_appliquer_horaire()
