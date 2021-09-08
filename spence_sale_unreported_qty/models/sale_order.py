# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from functools import partial
from odoo.tools.misc import formatLang

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    unreported_amount_untaxed = fields.Monetary(string='Unreported Untaxed Amount', store=True, readonly=True, compute='_amount_all_unreported')
    unreported_amount_tax = fields.Monetary(string='Unreported Taxes', store=True, readonly=True, compute='_amount_all_unreported')
    unreported_amount_total = fields.Monetary(string='Unreported Total', store=True, readonly=True, compute='_amount_all_unreported')
    unreported_amount_by_group = fields.Binary(string="Unreported Tax amount by group", compute='_unreported_amount_by_group', help="type: [(name, amount, base, formated amount, formated base)]")

    def _unreported_amount_by_group(self):
        for order in self:
            currency = order.currency_id or order.company_id.currency_id
            fmt = partial(formatLang, self.with_context(lang=order.partner_id.lang).env, currency_obj=currency)
            res = {}
            for line in order.order_line:
                price_reduce = line.price_unit * (1.0 - line.discount / 100.0)
                taxes = line.tax_id.compute_all(price_reduce, quantity=line.qty_unreported, product=line.product_id, partner=order.partner_shipping_id)['taxes']
                for tax in line.tax_id:
                    group = tax.tax_group_id
                    res.setdefault(group, {'amount': 0.0, 'base': 0.0})
                    for t in taxes:
                        if t['id'] == tax.id or t['id'] in tax.children_tax_ids.ids:
                            res[group]['amount'] += t['amount']
                            res[group]['base'] += t['base']
            res = sorted(res.items(), key=lambda l: l[0].sequence)
            order.unreported_amount_by_group = [(
                l[0].name, l[1]['amount'], l[1]['base'],
                fmt(l[1]['amount']), fmt(l[1]['base']),
                len(res),
            ) for l in res]

    @api.depends('order_line.price_total')
    def _amount_all_unreported(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.unreported_price_subtotal
                amount_tax += line.unreported_price_tax
            order.update({
                'unreported_amount_untaxed': amount_untaxed,
                'unreported_amount_tax': amount_tax,
                'unreported_amount_total': amount_untaxed + amount_tax,
            })
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    qty_reported = fields.Float("Reported Quantity", default=0, copy=False, digits='Product Unit of Measure')
    qty_unreported = fields.Float("Unreported Quantity", store=True, copy=False, readonly=False, 
                                    compute="_compute_qty_unreported", inverse="_compute_qty_reported",
                                    digits='Product Unit of Measure', )
    unreported_price_subtotal = fields.Monetary(compute='_compute_amount_unreported', string='Unreported Subtotal', readonly=True, store=True)
    unreported_price_tax = fields.Float(compute='_compute_amount_unreported', string='Unreported Total Tax', readonly=True, store=True)
    unreported_price_total = fields.Monetary(compute='_compute_amount_unreported', string='Unreported Total', readonly=True, store=True)
   
    @api.depends('qty_unreported', 'discount', 'price_unit', 'tax_id')
    def _compute_amount_unreported(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.qty_unreported, product=line.product_id, partner=line.order_id.partner_shipping_id)
            line.update({
                'unreported_price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'unreported_price_total': taxes['total_included'],
                'unreported_price_subtotal': taxes['total_excluded'],
            })

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