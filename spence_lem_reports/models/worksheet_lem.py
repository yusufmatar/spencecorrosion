# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import datetime

from odoo.exceptions import UserError

class LEM(models.Model):
    _name = 'worksheet.lem'
    _description = 'LEM Sheet'

    _inherit = ['portal.mixin','mail.thread']

    # Model meta fields
    state = fields.Selection(string='State', default='draft',
                                selection=[('draft','Draft'),('completed','Completed'),('sent','Sent'),('signed','Signed')])

    # Task Related Fields
    task_id = fields.Many2one(comodel_name='project.task', required=True, readonly=True, ondelete='cascade', index=True)
    name = fields.Char(string='Task', related='task_id.name')
    user_id = fields.Many2one(related='task_id.user_id')
    sale_order_id = fields.Many2one(related='task_id.sale_order_id', store=True)
    
    # LEM Fields
    date_performed = fields.Date(string='Date Performed', default=fields.Date.context_today)
    shift_type = fields.Selection(string='Shift Type', required=True, default='day', selection=[('day','Day'),('night','Night')])
    loa = fields.Integer(string='LOA')
    accommodations = fields.Integer(string='Accommodations')
    note = fields.Text(string='Comments')

    # Employee Signature
    employee_signature = fields.Binary('Employee Signature', copy=False, attachment=True)
    employee_id = fields.Many2one(string='Employee', comodel_name='res.partner', copy=False, readonly=True)
    employee_signature_date = fields.Date(string='Date Signed by Employee', copy=False, readonly=True)

    # Customer Signature
    partner_id = fields.Many2one(related='task_id.partner_id')
    customer_signature = fields.Binary('Customer Signature', help='Signature received through the portal.', copy=False, attachment=True, readonly=True)
    customer_signature_name = fields.Char('Customer Name', help='Name of the person who signed the task.', copy=False, readonly=True)
    customer_signature_date = fields.Date(string='Date Signed by Customer', copy=False, readonly=True)

    # Reports
    report_attachment_id = fields.Many2one(string='Report Attachment', comodel_name='ir.attachment', help='Final PDF Report', copy=False, readonly=True)
    report_attachment = fields.Binary('Report', related='report_attachment_id.datas')


    # Buttons
    def button_employee_sign(self):
        self.ensure_one()
        if not self.employee_signature:
            raise UserError('You must first sign the worksheet!')
        self.state = 'completed'
        self.employee_signature_date = datetime.today()
        self.employee_id = self.env.user.partner_id
        return True

    def button_go_to_portal(self):
        self.ensure_one()
        url = self.get_portal_url()
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': url
        }

    def _compute_access_url(self):
        super()._compute_access_url()
        for worksheet in self:
            worksheet.access_url = '/my/lem/%s' % worksheet.id

    def button_send_report(self):
        self.ensure_one()
        if self.report_attachment_id:
            template = self.env.ref('spence_lem_reports.spence_lem_email_template_signed')
            template.attachment_ids = [(6,0, [self.report_attachment_id.id])]
        else:
            template = self.env.ref('spence_lem_reports.spence_lem_email_template_unsigned')
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': {
                'default_model': 'worksheet.lem',
                'default_res_id': self.id,
                'default_use_template': bool(template),
                'default_template_id': template.id,
                'force_email': True,
                'lem_mark_as_sent': True,
            },
        }

    def has_to_be_signed(self):
        return not self.customer_signature

    def _get_report_base_filename(self):
        self.ensure_one()
        return f"LEM{' - ' + self.sale_order_id.name if self.sale_order_id else ''} - {self.name} - {self.date_performed.strftime('%d-%m-%Y')} - {self.id}.pdf"
    
    def _message_post_after_hook(self, message, *args, **kwargs):
        if self.env.context.get('lem_mark_as_sent') and self.state != 'signed':
            self.write({'state': 'sent'})

class Task(models.Model):
    _inherit = 'project.task'

    lem_ids = fields.One2many(comodel_name='worksheet.lem', inverse_name='task_id', string='LEM Sheets')