# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from ast import literal_eval
from datetime import datetime

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

class MetaWorksheet(models.Model):
    _name = "project.task.worksheet.meta"
    _description = "Task Worksheet"
    _inherit = ['portal.mixin']
    _inherits = {
        'project.task': 'task_id' 
    }

    task_id = fields.Many2one(comodel_name='project.task')
    worksheet_template_id = fields.Many2one(comodel_name='project.worksheet.template', string="Worksheet Template", related="task_id.worksheet_template_id")
    signature = fields.Binary('Signature', help='Signature received through the portal.', copy=False, attachment=True)
    signed_by = fields.Char('Signed By', help='Name of the person who signed the task.', copy=False)
    color = fields.Integer(related='worksheet_template_id.color')
    date_performed = fields.Date(string="Date Performed", default=fields.Date.context_today)
    date_signed = fields.Date(string="Date Signed")


    def _get_worksheet(self):
        self.ensure_one()
        return self.env[self.worksheet_template_id.model_id.model].search([('x_worksheet_id', '=', self.id)])
    
    def button_go_to_worksheet(self):
        return self.task_id.with_context(worksheet=self).action_fsm_worksheet()

    def button_go_to_portal(self):
        self.ensure_one()
        if not self.worksheet_template_id:
            raise UserError(_("To send the report, you need to select a worksheet template."))

        source = 'fsm' if self.env.context.get('fsm_mode', False) else 'project'
        url = self.get_portal_url(suffix='/%s' % source)
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': url
        }

    def button_send_report(self):
        self.ensure_one()
        if not self.worksheet_template_id:
            raise UserError(_("To send the report, you need to select a worksheet template."))

        template_id = self.env.ref('spence_project_multiple_worksheets.mail_template_data_send_report').id
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': {
                'default_model': 'project.task.worksheet.meta',
                'default_res_id': self.id,
                'default_use_template': bool(template_id),
                'default_template_id': template_id,
                'force_email': True,
                'fsm_mark_as_sent': True,
            },
        }

    def _compute_access_url(self):
        super(MetaWorksheet, self)._compute_access_url()
        for worksheet in self:
            worksheet.access_url = '/my/worksheet/%s' % worksheet.id

    def has_to_be_signed(self):
        return self.task_id.allow_worksheets and not self.signature