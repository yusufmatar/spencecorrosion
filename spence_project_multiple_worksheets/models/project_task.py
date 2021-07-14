# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from ast import literal_eval
class Task(models.Model):
    _inherit = 'project.task'

    worksheet_ids = fields.One2many(comodel_name="project.task.worksheet.meta", inverse_name="task_id", string="Worksheets")
        
    def action_fsm_worksheet(self):
        action = self.worksheet_template_id.action_id.sudo().read()[0]
        context = literal_eval(action.get('context', '{}'))
        WorksheetMeta = self.env['project.task.worksheet.meta']
        worksheet = self._context.get('worksheet')
        if not worksheet:
            worksheet = WorksheetMeta.create({
                'task_id': self.id
            })
        action.update({
            'res_id': worksheet._get_worksheet().id or False,
            'views': [(False, 'form')],
            'context': {
                **context,
                'edit': True,
                'default_x_task_id': self.id,
                'default_x_worksheet_id': worksheet.id,
                'form_view_initial_mode': 'edit',
            },
        })
        return action