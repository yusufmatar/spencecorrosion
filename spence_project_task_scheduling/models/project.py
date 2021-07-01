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
        modified_tasks = (self._origin | self.project_id.tasks.filtered(lambda t: t.sequence >= min(self.mapped("sequence")))).sorted("sequence")
        unmodified_tasks = self.project_id.tasks - modified_tasks
        for index, task in enumerate(modified_tasks):
            # We only update the start date if it is a task or the chage was triggered by drag reordering.
            if index > 0:
                task.date_start = modified_tasks[index - 1].date_end + timedelta(days=1)
            elif unmodified_tasks and len(self) > 1:
                task.date_start = unmodified_tasks[-1].date_end + timedelta(days=1)
            task.date_end = task.date_start + timedelta(days=task.duration)
