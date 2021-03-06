# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
from datetime import datetime
import binascii
import base64


class CustomerPortal(CustomerPortal):
    @http.route(['/my/worksheet/<int:worksheet_id>/',
                 '/my/worksheet/<int:worksheet_id>/<string:source>',
                 '/my/worksheet/<int:worksheet_id>/report'], type='http', auth="public", website=True)
    def portal_my_worksheet(self, worksheet_id, access_token=None, source=False, report_type=None, download=False, message=False, **kw):
        try:
            worksheet_sudo = self._document_check_access('project.task.worksheet.meta', worksheet_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        if report_type in ('html', 'pdf', 'text'):
            return self._show_report(model=worksheet_sudo, report_type=report_type, report_ref='spence_project_multiple_worksheets.task_custom_report', download=download)
        worksheet_map = {}
        if worksheet_sudo.worksheet_template_id:
            worksheet = worksheet_sudo._get_worksheet()
            worksheet_map[worksheet_sudo.id] = worksheet
        return request.render("industry_fsm_report.portal_my_worksheet", {'worksheet_map': worksheet_map, 'task': worksheet_sudo.task_id, 'worksheet': worksheet_sudo,'message': message, 'source': source})


    @http.route(['/my/worksheet/<int:worksheet_id>/sign/<string:source>'], type='json', auth="public", website=True)
    def portal_worksheet_sign(self, worksheet_id, access_token=None, source=False, name=None, signature=None):
        # get from query string if not on json param
        access_token = access_token or request.httprequest.args.get('access_token')
        try:
            worksheet_sudo = self._document_check_access('project.task.worksheet.meta', worksheet_id, access_token=access_token)
        except (AccessError, MissingError):
            return {'error': _('Invalid Task.')}

        if not worksheet_sudo.has_to_be_signed():
            return {'error': _('The worksheet is not in a state requiring customer signature.')}
        if not signature:
            return {'error': _('Signature is missing.')}

        try:
            worksheet_sudo.write({
                'worksheet_signature': signature,
                'worksheet_signed_by': name,
                'date_signed': datetime.today()
            })

        except (TypeError, binascii.Error):
            return {'error': _('Invalid signature data.')}

        pdf = request.env.ref('spence_project_multiple_worksheets.task_custom_report').sudo()._render_qweb_pdf([worksheet_sudo.id])[0]
        # filename = f"Worksheet {worksheet_sudo.name}{(' - ' + worksheet_sudo.partner_id.name) if worksheet_sudo.partner_id else ''} - {worksheet_sudo.id}.pdf"
        filename = f"LEM{' - ' + worksheet_sudo.sale_order_id.name if worksheet_sudo.sale_order_id else ''} - {worksheet_sudo.name} - {worksheet_sudo.date_performed.strftime('%d-%m-%Y')} - {worksheet_sudo.id}.pdf"
        worksheet_sudo.task_id.message_post(body=_('The worksheet has been signed'), attachments=[(filename, pdf)])
        worksheet_sudo.report_attachment_id = request.env['ir.attachment'].create({
                    'name': filename,
                    'res_id': worksheet_sudo.id,
                    'res_model': 'project.task.worksheet.meta',
                    'datas': base64.encodebytes(pdf),
                    'type': 'binary',
                    'mimetype': 'application/pdf'
                }).id
        query_string = '&message=sign_ok'
        return {
            'force_refresh': True,
            'redirect_url': worksheet_sudo.get_portal_url(suffix='/%s' % source, query_string=query_string),
        }
