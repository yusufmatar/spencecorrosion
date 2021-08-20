# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    employee_type = fields.Selection(string="Type", default='employee',
                                        selection=[('employee','Employee'),('job_title','Job Title')])