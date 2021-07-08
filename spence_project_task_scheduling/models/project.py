# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

from datetime import timedelta, datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
import pytz

class Task(models.Model):
    _inherit = "project.task"
    _order = "sequence, id asc"

    date_start = fields.Datetime("Start Date", readonly=False, default=fields.Date.context_today, store=True, compute="_compute_date_start")
    date_end = fields.Datetime("End Date", compute="_compute_end_date", store=True)
    duration = fields.Integer("Duration in Days", default=1)
    predecessor = fields.Many2one('project.task', string="Predecessor", compute="_compute_siblings", store=True)

    @api.depends('predecessor.date_start','predecessor.duration')
    def _compute_date_start(self):
        for task in self.filtered(lambda t: t.predecessor):
            task.date_start = task.predecessor.date_start + timedelta(days=task.predecessor.duration)

    @api.depends("date_start", "duration")
    def _compute_end_date(self):
        for task in self:
            task.date_end = task.date_start + timedelta(days=task.duration, seconds=-1)

    @api.depends("sequence","predecessor.sequence")
    def _compute_siblings(self):
        for task in self:
            earlier_tasks = task.project_id.tasks.filtered(lambda t: t.sequence < task.sequence).sorted('sequence') # For some reason it wasn't automatically being sorted so we explcitly sort here
            task.predecessor = earlier_tasks[-1] if earlier_tasks else None

    # I'm not sure why but even though we have editable = 'bottom' on the list view,
    # it doesn't properly compute the sequence number.
    @api.model
    def create(self, vals):
        rec = super(Task, self).create(vals)
        rec.sequence = max(rec.project_id.tasks.mapped('sequence'))+1
        return rec