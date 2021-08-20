# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        res = super().action_confirm()
        EmployeeMap = self.env['project.sale.line.employee.map']
        for line in self.order_line.filtered(lambda l: l.product_id.is_labour and l.project_id):
            line.project_id.pricing_type = 'employee_rate'
            EmployeeMap.create({
                'project_id': line.project_id.id,
                'sale_line_id': line.id,
                'employee_id': line.product_id.labourer_title_id.id,
            })
        return res