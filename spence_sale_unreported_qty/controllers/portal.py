# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, http
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.exceptions import AccessError, MissingError
from odoo.http import request


class CustomerPortal(CustomerPortal):
    @http.route(['/my/worksheet/<int:worksheet_id>/sign/<string:source>'], type='json', auth="public", website=True)
    def portal_worksheet_sign(self, worksheet_id, access_token=None, source=False, name=None, signature=None):
        response = super(CustomerPortal, self).portal_worksheet_sign(worksheet_id, access_token, source, name, signature)
        if response.get('error', False):
            return response
        try:
            worksheet_sudo = self._document_check_access('project.task.worksheet.meta', worksheet_id, access_token=access_token)
        except (AccessError, MissingError):
            return {'error': _('Invalid Worksheet.')}
        # Create pro-forma pdf if needed
        if worksheet_sudo.task_id.sale_order_id.use_costed_report:
            pdf = request.env.ref('sale.action_report_pro_forma_invoice').sudo()._render_qweb_pdf([worksheet_sudo.task_id.sale_order_id.id])[0]
            worksheet_sudo.task_id.sale_order_id.message_post(body=_('The costed report has been generated'), attachments=[('%s - %d.pdf' % (worksheet_sudo.task_id.sale_order_id.name, worksheet_sudo.id), pdf)])
        # Update sale order lines and timesheet lines
        worksheet_sudo.task_id.sale_order_id.order_line._update_qty_reported()
        worksheet_sudo.task_id.timesheet_ids._mark_timesheets_reported()
        return response
