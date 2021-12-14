# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class HrEmployee(models.Model):
    _inherit = 'hr.employee'


    employee_type = fields.Selection(string="Type", default='employee',
                                        selection=[('employee','Employee'),('job_title','Job Title')])
    overtime_title_id = fields.Many2one(string="Overtime Equivalent", comodel_name="hr.employee", 
                                            domain=[("employee_type","=","job_title"),("overtime_title_id","=",False)])

    job_title_ids = fields.Many2many(string="Job Titles", comodel_name="hr.employee", relation="job_employee_rel", column1="job_title_id", column2="employee_id", domain=[('employee_type','=','job_title'),('overtime_title_id','!=',False)])
    employee_with_title_ids = fields.Many2many(string="Employees with Title", comodel_name="hr.employee", relation="job_employee_rel", column2="job_title_id", column1="employee_id", domain=[('employee_type','=','employee')])