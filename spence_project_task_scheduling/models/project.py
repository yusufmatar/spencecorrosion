# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

from datetime import timedelta

class Task(models.Model):
    _inherit = "project.task"
    _order = "sequence, priority desc, id desc"

    date_start = fields.Date("Start Date", readonly=False, compute="_compute_date_start", default=fields.Date.context_today, store=True)
    date_end = fields.Date("End Date", compute="_compute_date_end")
    duration = fields.Integer("Duration in Days", default=1)

    # Because date_start depends on 'itself' (in reality it depends on the the start date of its 
    # older sibling) we need to manually trigger the compute method on change to effect change
    # on the younger sibling tasks.
    @api.onchange('date_start')
    def _on_change(self):
        self._compute_date_start()


    @api.depends('date_start','sequence','duration')
    def _compute_date_start(self):
        # We split the total task list in two. Those that come after the first edited row and 
        # those that come before.
        modified_tasks = self.project_id.tasks.filtered(lambda t: t.sequence >= min(self.mapped("sequence")))
        unmodified_tasks = self.project_id.tasks - modified_tasks
        for index, task in enumerate(modified_tasks):
            # We only recompute the start date if was a secondary change or as a result of dragging the sequence handle.
            # Otherwise, it was manually entered by the user and we don't touch it.
            if index > 0:
                task.date_start = modified_tasks[index - 1].date_start + timedelta(days=1+modified_tasks[index - 1].duration)
            elif unmodified_tasks and len(self) > 1:
                task.date_start = unmodified_tasks[-1].date_start +  timedelta(days=1+unmodified_tasks[-1].duration)   

    @api.depends("date_start", "duration")
    def _compute_date_end(self):
        for task in self:
            task.date_end = task.date_start + timedelta(days=task.duration)