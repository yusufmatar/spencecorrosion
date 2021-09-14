# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class Timesheet(models.Model):
    _inherit = 'account.analytic.line'

    employee_id = fields.Many2one(string='Job Title', domain=[('employee_type','=','job_title')])
    employee_partner_id = fields.Many2one(string='Employee', comodel_name='hr.employee', domain=[('employee_type','=','employee')])