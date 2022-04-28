# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_type_lem = fields.Selection(string="Type", 
                    selection=[('equipment','Equipment'),('material','Material'),('accommodations','Accommodation'),
                               ('loa','LoA'),('labour','Labour')])
    labourer_title_id = fields.Many2one(string="Job Title", comodel_name="hr.employee", domain=[("employee_type","=","job_title")])