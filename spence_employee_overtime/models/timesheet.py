# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from operator import inv
from odoo import api, fields, models


class Timesheet(models.Model):
    _inherit = 'account.analytic.line'

    def _domain_employee_id(self):
        if not self.user_has_groups('hr_timesheet.group_hr_timesheet_approver'):
            return [('user_id', '=', self.env.user.id),('employee_type','=','employee')]
        return [('employee_type','=','employee')]

    employee_id = fields.Many2one(string='Job Title', domain=[('employee_type','=','job_title')])
    employee_partner_id = fields.Many2one(string='Employee', comodel_name='hr.employee', domain=_domain_employee_id)
    overtime_allowed = fields.Boolean(string="Overtime Entry Allowed", compute="_compute_allow_overtime_entry")
    unit_amount_overtime = fields.Float(string='Overtime (Hours)', default=0.0)
    overtime_line_id = fields.Many2one(string='Overtime Line', comodel_name='account.analytic.line', readonly=True)
    normal_time_id = fields.One2many(string='Regular Time', comodel_name='account.analytic.line', inverse_name='overtime_line_id')

    @api.onchange('employee_id')
    def _compute_allow_overtime_entry(self):
        for line in self:
            line.overtime_allowed = bool(line.employee_id.overtime_title_id) and not bool(line.overtime_line_id)

    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('unit_amount_overtime',False) and vals.get('employee_id', False):    
                job_title = self.env['hr.employee'].browse(vals['employee_id'])
                overtime_line = self.create(dict(vals, **{
                    'unit_amount': vals['unit_amount_overtime'],
                    'employee_id': job_title.overtime_title_id.id,
                    'unit_amount_overtime': 0
                }))
                vals.update({
                    'overtime_line_id': overtime_line.id,
                    'unit_amount_overtime': 0
                })
        return super().create(vals_list)

    def write(self, values):
        if  values.get('unit_amount_overtime',False) and self.overtime_line_id:
            self.overtime_line_id.write({
                'unit_amount': values['unit_amount_overtime']
            })
            values['unit_amount_overtime'] = 0
        return super().write(values)