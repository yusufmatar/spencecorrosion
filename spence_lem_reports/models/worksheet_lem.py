# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import datetime

from odoo.exceptions import UserError, ValidationError

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
    partner_id = fields.Many2one(related='task_id.partner_id')
    sale_order_id = fields.Many2one(related='task_id.sale_order_id', store=True)
    
    # LEM Fields
    date_performed = fields.Date(string='Date Performed', required=True, default=fields.Date.context_today)
    shift_type = fields.Selection(string='Shift Type', required=True, default='day', selection=[('day','Day'),('night','Night')])
    # Note: LOA and Accommodations are actually Integers but the client 
    # wants the user to have to explictly type in 0 if that is the case.
    loa = fields.Char(string='LOA', required=True)
    accommodations = fields.Char(string='Accommodations', required=True)
    note = fields.Text(string='Comments')

    # Employee Signature
    employee_signature = fields.Binary('Employee Signature', required=True, copy=False, attachment=True)
    employee_id = fields.Many2one(string='Employee', comodel_name='res.partner', copy=False, readonly=True)
    employee_signature_date = fields.Date(string='Date Signed by Employee', copy=False, readonly=True)

    # Customer Signature
    customer_signature = fields.Binary('Customer Signature', help='Signature received through the portal.', copy=False, attachment=True, readonly=True)
    customer_signature_name = fields.Char('Customer Name', help='Name of the person who signed the task.', copy=False, readonly=True)
    customer_signature_date = fields.Date(string='Date Signed by Customer', copy=False, readonly=True)

    # Reports
    report_attachment_id = fields.Many2one(string='Report Attachment', comodel_name='ir.attachment', help='Final PDF Report', copy=False, readonly=True)
    report_attachment = fields.Binary('Report', related='report_attachment_id.datas')


    # Buttons
    def action_confirm(self):
        for lem in self:
            if not lem.employee_signature:
                raise UserError('You must first sign the worksheet!')
            lem.state = 'completed'
            lem.employee_signature_date = datetime.today()
            lem.employee_id = lem.env.user.partner_id
            # Increment accomodation and loa line items
            try:
                loa_lines = lem.sale_order_id.order_line.filtered(lambda l: l.product_id.product_type_lem == 'loa')
                if loa_lines:
                    loa_lines[0].qty_delivered += int(lem.loa)
                accommodation_lines = lem.sale_order_id.order_line.filtered(lambda l: l.product_id.product_type_lem == 'accommodations')
                if accommodation_lines:
                    accommodation_lines[0].qty_delivered += int(lem.accommodations)
            except:
                raise ValidationError('LoA and Accommodations must be numbers!')
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
        # If LEM already has an attachment, include it in the email template. 
        # Else, generate a new one. We don't just always generate a new report
        # because it depends on the current state of the sale order, which might
        # be changed between the generation of the original report and the time
        # the email template is used.
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
        return f"LEM{' - ' + self.sale_order_id.name if self.sale_order_id else ''} - {self.name} - {self.date_performed.strftime('%d-%m-%Y')} - {self.id}"
    
    def _message_post_after_hook(self, message, *args, **kwargs):
        if self.env.context.get('lem_mark_as_sent') and self.state != 'signed':
            self.write({'state': 'sent'})