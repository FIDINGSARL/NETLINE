# # -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import date, datetime, timedelta


class CpsHrEmployee(models.Model):

    _inherit = 'hr.employee'

    matricule = fields.Char('Matricule')
    type_employee=fields.Selection([('permanent', 'Permanent'), ('Apprenti', 'Apprenti')], string='Type salarié', default='permanent')
    is_direct = fields.Selection([('direct', 'Direct'), ('indirect', 'Indirect')], string='Direct/Indirect', default='direct')
    is_absents = fields.Boolean('Est absent')
    equipe = fields.Selection([('A', 'A'), ('B', 'B'), ('FM', 'FM'), ('FA', 'FA')], string='Equipe salarié')
    societe = fields.Many2one('cps.hr.societe','Société')

    def _attendance_action_change(self):
        """ Check In/Check Out action
            Check In: create a new attendance record
            Check Out: modify check_out field of appropriate attendance record
        """

        # print('_attendance_action_change--------------------------')
        self.ensure_one()
        action_date = fields.Datetime.now()

        if self.attendance_state != 'checked_in':
            last_attendance = self.env['hr.attendance'].search([('employee_id', '=', self.id), ('check_out', '!=', False)], order='check_out desc', limit=1)
            delta_time_seconds = False
            if last_attendance.check_out is not False:
                delta_time = action_date - last_attendance.check_out
                delta_time_seconds = delta_time.seconds
            if (delta_time_seconds>30 or delta_time_seconds is False) and not self.is_absents:
                vals = {
                    'employee_id': self.id,
                    'check_in': action_date,
                }
                return self.env['hr.attendance'].create(vals)
            else:
                return last_attendance
        attendance = self.env['hr.attendance'].search([('employee_id', '=', self.id), ('check_out', '=', False)], limit=1)

        if attendance:
            delta_time = action_date - attendance.check_in
            if delta_time.seconds>30:
                attendance.check_out = action_date
        else:
            raise exceptions.UserError(_('Cannot perform check out on %(empl_name)s, could not find corresponding check in. '
                'Your attendances have probably been modified manually by human resources.') % {'empl_name': self.sudo().name, })
        return attendance

    def _attendance_action(self, next_action):
        """ Changes the attendance of the employee.
            Returns an action to the check in/out message,
            next_action defines which menu the check in/out message should return to. ("My Attendances" or "Kiosk Mode")
        """
        # print('attendance_action------------------------')
        self.ensure_one()
        employee = self.sudo()
        action_message = self.env.ref('hr_attendance.hr_attendance_action_greeting_message').read()[0]
        action_message['previous_attendance_change_date'] = employee.last_attendance_id and (employee.last_attendance_id.check_out or employee.last_attendance_id.check_in) or False
        action_message['employee_name'] = employee.matricule + "\n" + employee.name
        action_message['matricule'] = employee.matricule
        action_message['barcode'] = employee.barcode
        action_message['next_action'] = next_action
        if self.is_absents:
            action_message['hours_today'] = ""
        else:
            action_message['hours_today'] = employee.hours_today
        # print('employee matricule-------------------------', action_message['matricule'])
        if employee.user_id:
            modified_attendance = employee.with_user(employee.user_id)._attendance_action_change()
        else:
            modified_attendance = employee._attendance_action_change()
        action_message['attendance'] = modified_attendance.read()[0]
        return {'action': action_message}
