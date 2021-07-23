# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError

"""
    The industry_fsm_report module hardcodes all of the metadata 
    for a sheet directly on the project.task model which is a problem 
    for us since we want to allow for multiple worksheets and reports 
    per task.

    This spins that metadata off into a new model so that we can relate a task 
    to multiple sets of metadata. The worksheets themselves are dynamically
    created by the user (a new model is created) so we cannot create directly
    refer to the sheet itself here since we do not know the model name at
    'compile' time. That's what the _get_worksheet method is for. Lastly, since
    many templates and views still refer to the task, we use delegation inheritance
    for the task_id so that we minimize to need to change too many templates.
"""

class MetaWorksheet(models.Model):
    _name = "project.task.worksheet.meta"
    _description = "Task Worksheet"
    _inherit = ['portal.mixin','mail.thread']
    _inherits = {
        'project.task': 'task_id' 
    }

    task_id = fields.Many2one(comodel_name='project.task', readonly=True)
    worksheet_template_id = fields.Many2one(comodel_name='project.worksheet.template', string="Worksheet Template", related="task_id.worksheet_template_id")
    worksheet_signature = fields.Binary('Signature', help='Signature received through the portal.', copy=False, attachment=True, readonly=True)
    worksheet_signed_by = fields.Char('Signed By', help='Name of the person who signed the task.', copy=False, readonly=True)
    worksheet_color = fields.Integer(related='worksheet_template_id.color')
    date_performed = fields.Date(string="Date Performed", default=fields.Date.context_today)
    date_signed = fields.Date(string="Date Signed", readonly=True)
    fsm_is_sent = fields.Boolean(string="Sent", default=False, readonly=True)
    report_attachment = fields.Binary('Report', help='Final PDF Report', copy=False, attachment=True, readonly=True)

    def _get_worksheet(self):
        self.ensure_one()
        return self.env[self.worksheet_template_id.model_id.model].search([('x_worksheet_id', '=', self.id)])
    
    def button_go_to_worksheet(self):
        self.ensure_one()
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

    def _message_post_after_hook(self, message, *args, **kwargs):
        if self.env.context.get('fsm_mark_as_sent') and not self.fsm_is_sent:
            self.write({'fsm_is_sent': True})

    def _compute_access_url(self):
        super(MetaWorksheet, self)._compute_access_url()
        for worksheet in self:
            worksheet.access_url = '/my/worksheet/%s' % worksheet.id

    def has_to_be_signed(self):
        return self.task_id.allow_worksheets and not self.worksheet_signature

    def _get_report_base_filename(self):
        self.ensure_one()
        return 'Worksheet %s - %s - %d' % (self.name, self.partner_id.name, self.id)