# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class Sale(models.Model):
    _inherit = 'sale.order'

    use_costed_report = fields.Boolean("Use Costed Report", default=False)

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    qty_reported = fields.Float("Reported Quantity", default=0, copy=False, digits='Product Unit of Measure')
    qty_unreported = fields.Float("Unreported Quantity", store=True, copy=False, readonly=False, 
                                    compute="_compute_qty_unreported", inverse="_compute_qty_reported",
                                    digits='Product Unit of Measure', )

    @api.depends('qty_delivered','qty_reported')
    def _compute_qty_unreported(self):
        for line in self:
            line.qty_unreported = line.qty_delivered - line.qty_reported

    def _update_qty_reported(self):
        for line in self:
            line.qty_reported = line.qty_delivered
    
    @api.onchange('qty_unreported')
    def _compute_qty_reported(self):
        for line in self:
            line.qty_reported = line.qty_delivered - line.qty_unreported