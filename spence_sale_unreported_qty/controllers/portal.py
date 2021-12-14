# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, http
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.exceptions import AccessError, MissingError
from odoo.http import request


class CustomerPortal(CustomerPortal):
    @http.route(['/my/lem/<int:lem_id>/sign/<string:source>'], type='json', auth="public", website=True)
    def portal_lem_sign(self, lem_id, access_token=None, source=False, name=None, signature=None):
        response = super(CustomerPortal, self).portal_lem_sign(lem_id, access_token, source, name, signature)
        if response.get('error', False):
            return response
        try:
            lem_sudo = self._document_check_access('worksheet.lem', lem_id, access_token=access_token)
        except (AccessError, MissingError):
            return {'error': _('Invalid LEM Sheet.')}
        # Update sale order lines and timesheet lines
        lem_sudo.sale_order_id.order_line._update_qty_reported()
        lem_sudo.task_ids.timesheet_ids._mark_timesheets_reported()
        return response
