# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

from datetime import timedelta


class Task(models.Model):
    _inherit = "project.task"
    _order = "sequence, priority desc, id desc"

    date_start = fields.Date("Start Date", readonly=False, compute="_compute_dates", default=fields.Date.context_today, store=True)
    date_end = fields.Date("End Date", readonly=True, compute="_compute_dates", store=True)
    duration = fields.Integer("Duration in Days", default=1)

    @api.depends("date_start", "duration", "sequence")
    def _compute_dates(self):
        # We need to add all tasks after any that change since changes will propagate down the list.
        print()
        self = (self._origin | self.project_id.task_ids.filtered(lambda t: t.sequence >= min(self.mapped("sequence")))).sorted("sequence")
        unmodified_tasks = self.project_id.task_ids - self
        # self = self.self.project_id.task_ids
        for index, task in enumerate(self):
            # task.date_start = task.date_start or fields.Date.context_today(task)
            if index > 0:
                task.date_start = self[index - 1].date_end + timedelta(days=1)
            elif unmodified_tasks:
                task.date_start = unmodified_tasks[-1].date_end + timedelta(days=1)
            task.date_end = task.date_start + timedelta(days=task.duration)
