# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class Task(models.Model):
    _inherit = 'project.task'
    
    lem_ids = fields.Many2many(comodel_name='worksheet.lem', string='LEM Sheets')
    has_draft_lems = fields.Boolean(string="Has Unconfirmed LEMs", compute="_compute_has_draft_lems")

    def _compute_has_draft_lems(self):
        for task in self:
            task.has_draft_lems = any(task.lem_ids.mapped(lambda l: l.state == 'draft'))

    def validate_lems(self):
        self.ensure_one()
        for lem in self.lem_ids.filtered(lambda lem: lem.state == 'draft'):
            lem.action_confirm()
