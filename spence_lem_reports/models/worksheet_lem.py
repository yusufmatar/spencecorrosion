# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import datetime
from functools import partial
from odoo.tools.misc import formatLang, get_lang

from odoo.exceptions import UserError, ValidationError

class LEM(models.Model):
    _name = 'worksheet.lem'
    _description = 'LEM Sheet'

    _inherit = ['portal.mixin','mail.thread']

    # Model meta fields
    state = fields.Selection(string='State', default='draft',
                                selection=[('draft','Draft'),('completed','Completed'),('sent','Sent'),('signed','Signed')])

    name = fields.Char(string='LEM', compute="_compute_lem_name")
    sale_order_id = fields.Many2one(string="Sale Order", comodel_name='sale.order', required=True, index=True, store=True, readonly=True, states={'draft': [('readonly', False)]})
    currency_id = fields.Many2one(string="Currency", comodel_name="res.currency", related="sale_order_id.currency_id")
    task_id = fields.Many2one(string="Task", comodel_name='project.task', domain="[('sale_order_id', '=', sale_order_id)]", required=True, readonly=True, states={'draft': [('readonly', False)]})
    user_id = fields.Many2one(string="User", comodel_name='res.users', default=lambda self: self.env.user, copy=False, readonly=True, states={'draft': [('readonly', False)]})
    partner_id = fields.Many2one(string="Customer", comodel_name="res.partner", required=True, readonly=True, states={'draft': [('readonly', False)]})

    # LEM Fields
    date_performed = fields.Date(string='Date Performed', required=True, default=fields.Date.context_today, readonly=True, states={'draft': [('readonly', False)]})
    shift_type = fields.Selection(string='Shift Type', required=True, default='day', selection=[('day','Day'),('night','Night')], readonly=True, states={'draft': [('readonly', False)]})
    # Note: LOA and Accommodations are actually Integers but the client 
    # wants the user to have to explictly type in 0 if that is the case.
    loa = fields.Char(string='LOA', required=True, readonly=True, states={'draft': [('readonly', False)]})
    accommodations = fields.Char(string='Accommodations', required=True, readonly=True, states={'draft': [('readonly', False)]})
    note = fields.Text(string='Comments', readonly=True, states={'draft': [('readonly', False)]})

    # Equipment
    product_line_ids = fields.One2many(string="Products", comodel_name="worksheet.lem.product", inverse_name="lem_id", readonly=True, states={'draft': [('readonly', False)]})
    equipment_line_ids = fields.One2many(string="Equipment", comodel_name="worksheet.lem.product", inverse_name="lem_id", domain=[('type', '=', 'equipment')], readonly=True, states={'draft': [('readonly', False)]})
    no_equipment_used = fields.Boolean(string="No Equipment Used", default=False, readonly=True, states={'draft': [('readonly', False)]})
    material_line_ids = fields.One2many(string="Materials", comodel_name="worksheet.lem.product", inverse_name="lem_id", domain=[('type', '=', 'material')], readonly=True, states={'draft': [('readonly', False)]})
    no_material_used = fields.Boolean(string="No Material Used", default=False, readonly=True, states={'draft': [('readonly', False)]})

    # Labour
    labour_line_ids = fields.One2many(string="Labour", comodel_name="worksheet.lem.labour", inverse_name="lem_id", readonly=True, states={'draft': [('readonly', False)]})

    # Employee Signature
    employee_signature = fields.Binary('Employee Signature', required=True, copy=False, attachment=True, readonly=True, states={'draft': [('readonly', False)]})
    employee_id = fields.Many2one(string='Employee', comodel_name='res.partner', copy=False, readonly=True)
    employee_signature_date = fields.Date(string='Date Signed by Employee', copy=False, readonly=True)

    # Customer Signature
    customer_signature = fields.Binary('Customer Signature', help='Signature received through the portal.', copy=False, attachment=True, readonly=True)
    customer_signature_name = fields.Char('Customer Name', help='Name of the person who signed the task.', copy=False, readonly=True)
    customer_signature_date = fields.Date(string='Date Signed by Customer', copy=False, readonly=True)

    # Reports
    report_attachment_id = fields.Many2one(string='Report Attachment', comodel_name='ir.attachment', help='Final PDF Report', copy=False, readonly=True)
    report_attachment = fields.Binary('Report', related='report_attachment_id.datas')

    # Sale Order Related FIelds
    order_lines = fields.Many2many(comodel_name="sale.order.line", string="Order Lines", compute="_compute_order_lines")

    # Pricing for Costed LEM
    amount_untaxed = fields.Monetary(string='Untaxed Amount', readonly=True, compute='_amount_all')
    amount_tax = fields.Monetary(string='Taxes', readonly=True, compute='_amount_all')
    amount_total = fields.Monetary(string='Total', readonly=True, compute='_amount_all')
    
    def _amount_all(self):
        for lem in self:
            amount_untaxed = amount_tax = 0.0
            for line in lem.product_line_ids:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            for line in lem.labour_line_ids:
                amount_untaxed += line.price_subtotal + line.ot_price_subtotal
                amount_tax += line.price_tax + line.ot_price_tax
            lem.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax,
            })

    def _compute_order_lines(self):
        for lem in self:
            lem.order_lines = lem.sale_order_id.order_line.filtered(lambda l: l.display_type == 'line_section' or 
                                                                              l.id in lem.mapped('product_line_ids.order_line.id') or
                                                                              l.id in lem.mapped('labour_line_ids.order_line.id'))

    def _compute_lem_name(self):
        for lem in self:
            lem.name = f"{lem.sale_order_id.name} - {lem.task_id.name}"

    # Automation
    @api.onchange('sale_order_id')
    def _onchange_sale_order_id(self):
        for lem in self:
            lem.partner_id = lem.sale_order_id.partner_id

    # Buttons
    def action_confirm(self):
        for lem in self:
            if not lem.employee_signature:
                raise UserError(_('You must first sign the worksheet!'))
            lem.state = 'completed'
            lem.employee_signature_date = datetime.today()
            lem.employee_id = lem.env.user.partner_id
            # Increment accomodation and loa line items
            try:
                loa_lines = lem.sale_order_id.order_line.filtered(lambda l: l.product_id.product_type_lem == 'loa')
                if loa_lines:
                    loa_lines[0].product_uom_qty += int(lem.loa)
                accommodation_lines = lem.sale_order_id.order_line.filtered(lambda l: l.product_id.product_type_lem == 'accommodations')
                if accommodation_lines:
                    accommodation_lines[0].product_uom_qty += int(lem.accommodations)
            except:
                raise ValidationError(_('LoA and Accommodations must be numbers!'))
            # Check for equipment and materials
            if not lem.no_equipment_used and not lem.equipment_line_ids:
                raise ValidationError(_('You must log your equipment used!'))
            if not lem.no_material_used and not lem.material_line_ids:
                raise ValidationError(_('You must log your material used!'))
            # Update sale order with equipment and material
            if not lem.no_equipment_used:
                for product_line in lem.equipment_line_ids:
                    product = product_line.product_id.with_context(fsm_task_id = lem.task_id.id) 
                    product.set_fsm_quantity(product.sudo().fsm_quantity + product_line.qty)
            if not lem.no_material_used:
                for product_line in lem.material_line_ids:
                    product = product_line.product_id.with_context(fsm_task_id = lem.task_id.id) 
                    product.set_fsm_quantity(product.sudo().fsm_quantity + product_line.qty)
            # Update task with timesheets
            timesheets_to_create = []
            AnalyticLine = self.env['account.analytic.line']
            for line in lem.labour_line_ids:
                if line.regular_hours:
                    timesheets_to_create.append({
                        'date': line.date,
                        'employee_id': line.job_title_id.id,
                        'employee_partner_id': line.employee_id.id,
                        'so_line': AnalyticLine._timesheet_determine_sale_line(lem.task_id, line.job_title_id, lem.task_id.project_id).id,
                        'unit_amount': line.regular_hours,
                        'project_id': lem.task_id.project_id.id,
                        'name': line.note
                    })
                if line.overtime_hours:
                    timesheets_to_create.append({
                        'date': line.date,
                        'employee_id': line.job_title_id.overtime_title_id.id,
                        'employee_partner_id': line.employee_id.id,
                        'so_line': AnalyticLine._timesheet_determine_sale_line(lem.task_id, line.job_title_id.overtime_title_id, lem.task_id.project_id).id,
                        'unit_amount': line.overtime_hours,
                        'project_id': lem.task_id.project_id.id,
                        'name': line.note
                    })
            lem.task_id.write({
                'timesheet_ids': [(0,0,vals) for vals in timesheets_to_create]
            })
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
        return super()._message_post_after_hook(message, *args, **kwargs)

class LEMProduct(models.Model):
    _name = 'worksheet.lem.product'
    _description = 'LEM Equipment/Material Line'

    product_id = fields.Many2one(string="Product", comodel_name="product.product", required=True)
    lem_id = fields.Many2one(string="LEM", comodel_name="worksheet.lem", required=True)
    qty = fields.Float(string="Quantity", default=0, digits='Product Unit of Measure')
    type = fields.Selection(related="product_id.product_type_lem")

    order_line = fields.Many2one(string="Sale Order Line", comodel_name="sale.order.line", compute="_compute_order_line")
    price_unit = fields.Float(string="Price", related="order_line.price_unit")
    discount = fields.Float(related="order_line.discount")
    tax_id = fields.Many2many(comodel_name='account.tax', string='Taxes', related="order_line.tax_id")
    currency_id = fields.Many2one(string="Currency", comodel_name="res.currency", related="order_line.currency_id")
    
    price_tax = fields.Float(compute='_compute_amount', string='Total Tax', readonly=True, store=True)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', readonly=True, store=True)
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', readonly=True, store=True)

    @api.depends('qty', 'discount', 'price_unit', 'tax_id', 'order_line')
    def _compute_amount(self):
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.order_line.order_id.currency_id, line.qty, product=line.product_id, partner=line.order_line.order_id.partner_shipping_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })

    @api.depends('lem_id','product_id')
    def _compute_order_line(self):
        for line in self:
            order_line = line.lem_id.sale_order_id.order_line.filtered(lambda l: l.product_id == line.product_id)
            line.order_line = order_line[0] if order_line else False

class LEMLabour(models.Model):
    _name = 'worksheet.lem.labour'
    _description = 'LEM Labour Line'

    @api.model
    def default_get(self, field_list):
        result = super().default_get(field_list)
        if not self.env.context.get('default_employee_id') and 'employee_id' in field_list and result.get('user_id'):
            employee = self.env['hr.employee'].search([('user_id', '=', result['user_id'])], limit=1)
            result['employee_id'] = employee.id
            if employee.job_title_ids:
                result['job_title_id'] = employee.job_title_ids[0].id
            else:
                result.pop('job_title_id', True)
        return result

    def _domain_employee_id(self):
        if not self.user_has_groups('hr_timesheet.group_hr_timesheet_approver'):
            return [('user_id', '=', self.env.user.id),('employee_type','=','employee')]
        return [('employee_type','=','employee')]

    def _domain_title_id(self):
        if not self.user_has_groups('hr_timesheet.group_hr_timesheet_approver'):
            return [('employee_type','=','job_title'),('overtime_title_id','!=',False),('id','in',self.env.user.employee_id.job_title_ids.ids)]
        return [('employee_type','=','job_title'),('overtime_title_id','!=',False)]

    lem_id = fields.Many2one(string="LEM", comodel_name="worksheet.lem", required=True)
    user_id = fields.Many2one(string="User", comodel_name='res.users', default=lambda self: self.env.user, copy=False, readonly=True)

    regular_hours = fields.Float('Regular Hours', default=0.0)
    overtime_hours = fields.Float('Overtime Hours', default=0.0)

    date = fields.Date('Date', required=True, index=True, default=fields.Date.context_today)

    job_title_id = fields.Many2one(string='Job Title', comodel_name='hr.employee', domain=_domain_title_id)
    employee_id = fields.Many2one(string='Employee', comodel_name='hr.employee', domain=_domain_employee_id)

    note = fields.Text(string="Description")

    order_line = fields.Many2one(string="Order Line", comodel_name="sale.order.line", compute="_compute_order_line", store=True)
    ot_order_line = fields.Many2one(string="OT Order Line", comodel_name="sale.order.line", compute="_compute_order_line", store=True)
    currency_id = fields.Many2one(string="Currency", comodel_name="res.currency", related="order_line.currency_id")

    price_tax = fields.Float(compute='_compute_amount', string='Total Tax', readonly=True)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', readonly=True)
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', readonly=True)
    ot_price_tax = fields.Float(compute='_compute_amount', string='OT Total Tax', readonly=True)
    ot_price_total = fields.Monetary(compute='_compute_amount', string='OT Total', readonly=True)
    ot_price_subtotal = fields.Monetary(compute='_compute_amount', string='OT Subtotal', readonly=True)

    @api.depends('order_line','ot_order_line', 'regular_hours','overtime_hours')
    def _compute_amount(self):
        for line in self:
            price = line.order_line.price_unit * (1 - (line.order_line.discount or 0.0) / 100.0)
            taxes = line.order_line.tax_id.compute_all(price, line.order_line.order_id.currency_id, line.regular_hours, product=line.order_line.product_id, partner=line.order_line.order_id.partner_shipping_id)
            price_ot = line.ot_order_line.price_unit * (1 - (line.ot_order_line.discount or 0.0) / 100.0)
            taxes_ot = line.ot_order_line.tax_id.compute_all(price_ot, line.ot_order_line.order_id.currency_id, line.overtime_hours, product=line.ot_order_line.product_id, partner=line.ot_order_line.order_id.partner_shipping_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
                'ot_price_tax': sum(t.get('amount', 0.0) for t in taxes_ot.get('taxes', [])),
                'ot_price_total': taxes_ot['total_included'],
                'ot_price_subtotal': taxes_ot['total_excluded'],
            })


    def _compute_order_line(self):
        for line in self:
            employee_mapping = line.lem_id.task_id.project_id.sale_line_employee_ids.filtered(lambda l: l.employee_id == line.job_title_id)
            employee_ot_mapping = line.lem_id.task_id.project_id.sale_line_employee_ids.filtered(lambda l: l.employee_id == line.job_title_id.overtime_title_id)
            if employee_mapping.sale_line_id:
                line.order_line = employee_mapping.sale_line_id
            else:
                order_line = self.env['sale.order.line'].create({
                    "order_id": line.lem_id.sale_order_id.id,
                    "product_id": self.env['product.product'].search([('labourer_title_id','=',line.job_title_id.id)],limit=1).id,
                    "product_uom_qty": 0
                })
                line.order_line = order_line
                line.lem_id.task_id.project_id.sale_line_employee_ids.create({
                    'project_id': line.lem_id.task_id.project_id.id,
                    'employee_id': line.job_title_id.id,
                    'sale_line_id': order_line.id
                })
            if employee_ot_mapping:
                line.ot_order_line = employee_ot_mapping.sale_line_id
            else:
                order_line = self.env['sale.order.line'].create({
                    "order_id": line.lem_id.sale_order_id.id,
                    "product_id": self.env['product.product'].search([('labourer_title_id','=',line.job_title_id.overtime_title_id.id)],limit=1).id,
                    "product_uom_qty": 0
                })
                line.ot_order_line = order_line
                line.lem_id.task_id.project_id.sale_line_employee_ids.create({
                    'project_id': line.lem_id.task_id.project_id.id,
                    'employee_id': line.job_title_id.overtime_title_id.id,
                    'sale_line_id': order_line.id
                })
