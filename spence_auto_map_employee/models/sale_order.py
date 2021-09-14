# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        res = super().action_confirm()
        for sale in self:
            if sale.project_ids:
                sale.project_id = sale.project_ids[0]
            if any(sale.order_line.mapped(lambda l: l.product_id.product_type_lem == 'labour')):
                sale.project_id.pricing_type = 'employee_rate'
                EmployeeMap = sale.env['project.sale.line.employee.map']
                for line in sale.order_line.filtered(lambda l: l.product_id.product_type_lem == 'labour'):
                    EmployeeMap.create({
                        'project_id': sale.project_id.id,
                        'sale_line_id': line.id,
                        'employee_id': line.product_id.labourer_title_id.id,
                    })
        return res