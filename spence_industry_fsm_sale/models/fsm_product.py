# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class FSMProduct(models.Model):
    _name = 'fsm.product.task'
    _description = 'FSM Product'

    product_id = fields.Many2one(string="Product", comodel_name="product.product", required=True)
    task_id = fields.Many2one(string="Task", comodel_name="project.task", required=True)
    qty = fields.Float(string="Quantity", default=0, digits='Product Unit of Measure')

    @api.onchange('qty')
    def set_fsm_qty(self):
        for record in self.filtered(lambda r: r.product_id and r.task_id):
            record.product_id.with_context(fsm_task_id = record._context.get('default_task_id', record.task_id.id)).set_fsm_quantity(record.qty)


class ProjectTask(models.Model):
    _inherit = 'project.task'

    fsm_product_ids = fields.One2many(string="Materials", comodel_name="fsm.product.task", inverse_name="task_id")
    