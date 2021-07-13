# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    worksheet_ids = fields.Many2many('project.task.worksheet.meta', compute='_compute_worksheet_ids', string='Worksheets associated to this sale')
    worksheet_count = fields.Integer(string='Worksheet', compute='_compute_worksheet_ids')

    @api.depends('order_line.product_id.project_id')
    def _compute_worksheet_ids(self):
        for order in self:
            task_ids = self.env['project.task'].search(['|', ('sale_line_id', 'in', order.order_line.ids), ('sale_order_id', '=', order.id)])
            order.worksheet_ids = task_ids.mapped('worksheet_ids')
            order.worksheet_count = len(order.worksheet_ids)

    def button_task_worksheets(self):
        context = dict(self.env.context)
        context['from_sale_order'] = True
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'list',
            'res_model': 'project.task.worksheet.meta',
            'name': 'Worksheets',
            'context': context,
            'domain': [('id', 'in', self.worksheet_ids.mapped('id'))],
        }