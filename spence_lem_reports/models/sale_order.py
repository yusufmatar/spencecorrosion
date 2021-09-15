# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    asset_id = fields.Char(related='opportunity_id.asset_id')
    po_number = fields.Char(related='opportunity_id.po_number')
    location = fields.Char(related='opportunity_id.location')
    
    lem_ids = fields.One2many(comodel_name='worksheet.lem', inverse_name='sale_order_id', string='LEMs associated to this sale')
    lem_count = fields.Integer(string='LEM', compute='_compute_lem_ids')

    use_costed_report = fields.Boolean("Use Costed LEM", default=False)

    @api.depends('lem_ids')
    def _compute_lem_ids(self):
        for order in self:
            order.lem_count = len(order.lem_ids)

    def button_lems(self):
        context = dict(self.env.context)
        context['from_sale_order'] = True
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'worksheet.lem',
            'name': 'LEM Sheets',
            'context': context,
            'domain': [('id', 'in', self.lem_ids.mapped('id'))],
        }