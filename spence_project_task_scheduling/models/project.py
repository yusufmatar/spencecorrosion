# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

from datetime import timedelta

class Task(models.Model):
    _inherit = "project.task"
    _order = "sequence, id asc"

    date_start = fields.Date("Start Date", readonly=False, default=fields.Date.context_today, store=True, compute="_compute_date_start")
    date_end = fields.Date("End Date", compute="_compute_end_date")
    duration = fields.Integer("Duration in Days", default=1)

    predecessor = fields.Many2one('project.task', string="Predecessor", compute="_compute_siblings")
    successor = fields.Many2one('project.task', string="Successor", compute="_compute_siblings")

    @api.depends('predecessor.date_start','predecessor.duration')
    def _compute_date_start(self):
        for task in self:
            if(task.predecessor):
                task.date_start = task.predecessor.date_start + timedelta(days=task.predecessor.duration)

    @api.depends("date_start", "duration")
    def _compute_end_date(self):
        for task in self:
            task.date_end = task.date_start + timedelta(days=task.duration - 1)
    
    @api.depends("sequence")
    def _compute_siblings(self):
        for task in self:
            later_tasks = task.project_id.tasks.filtered(lambda t: t.sequence > task.sequence)
            earlier_tasks = task.project_id.tasks.filtered(lambda t: t.sequence < task.sequence)
            if later_tasks:
                task.successor = later_tasks[0]
            else:
                task.successor = None
            if earlier_tasks:
                task.predecessor = earlier_tasks[-1]
            else:
                task.predecessor = None

    # I'm not sure why but even though we have editable = 'bottom' on the list view, it doesn't
    # properly compute the sequence number.
    @api.model
    def create(self, vals):
        rec = super(Task, self).create(vals)
        rec.sequence = max(rec.project_id.tasks.mapped('sequence'))+1
        return rec