# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_labour = fields.Boolean(string="Is Labour", default=False)
    labourer_title_id = fields.Many2one(string="Job Title", comodel_name="hr.employee", domain=[("employee_type","=","job_title")])