# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from datetime import datetime
import binascii
import base64


class CustomerPortal(CustomerPortal):
    @http.route(['/my/lem/<int:lem_id>/',
                 '/my/lem/<int:lem_id>/<string:source>',
                 '/my/lem/<int:lem_id>/report'], type='http', auth="public", website=True)
    def portal_my_lem(self, lem_id, access_token=None, source=False, report_type=None, download=False, message=False, **kw):
        try:
            lem_sudo = self._document_check_access('worksheet.lem', lem_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        if report_type in ('html', 'pdf', 'text'):
            return self._show_report(model=lem_sudo, report_type=report_type, report_ref='spence_lem_reports.spence_lem_sheet_pdf', download=download)
        values = {
            # 'task': lem_sudo, 
            'lem': lem_sudo,
            'message': message, 
            'source': source, 
            'page_name': 'order',
            'sale_order': lem_sudo.sale_order_id
        }
        return request.render("spence_lem_reports.portal_my_lem_spence", values)

    @http.route(['/my/lem/<int:lem_id>/sign/<string:source>'], type='json', auth="public", website=True)
    def portal_lem_sign(self, lem_id, access_token=None, source=False, name=None, signature=None):
        # get from query string if not on json param
        access_token = access_token or request.httprequest.args.get('access_token')
        try:
            lem_sudo = self._document_check_access('worksheet.lem', lem_id, access_token=access_token)
        except (AccessError, MissingError):
            return {'error': _('Invalid LEM.')}
        if not lem_sudo.has_to_be_signed():
            return {'error': _('The worksheet is not in a state requiring customer signature.')}
        if not signature:
            return {'error': _('Signature is missing.')}
        # Write signature related fields
        try:
            lem_sudo.write({
                'customer_signature': signature,
                'customer_signature_name': name,
                'customer_signature_date': datetime.today(),
                'state': 'signed'
            })

        except (TypeError, binascii.Error):
            return {'error': _('Invalid signature data.')}
        # Create costed LEM if needed
        if lem_sudo.sale_order_id.use_costed_report:
            pdf = request.env.ref('spence_lem_reports.spence_costed_lem_sheet_pdf').sudo()._render_qweb_pdf([lem_sudo.id])[0]
            filename = f"Costed LEM{' - ' + lem_sudo.sale_order_id.name if lem_sudo.sale_order_id else ''} - {lem_sudo.name} - {lem_sudo.date_performed.strftime('%d-%m-%Y')} - {lem_sudo.id}"
            lem_sudo.sale_order_id.message_post(body=_('The costed report has been generated'), attachments=[(filename, pdf)])
        # Create normal LEM report
        pdf = request.env.ref('spence_lem_reports.spence_lem_sheet_pdf').sudo()._render_qweb_pdf([lem_sudo.id])[0]
        filename = f"LEM - {lem_sudo.name} - {lem_sudo.date_performed.strftime('%d-%m-%Y')} - {lem_sudo.id}"
        # for task in lem_sudo.task_ids:
        lem_sudo.message_post(body=_('The worksheet has been signed'), attachments=[(filename, pdf)])
        lem_sudo.report_attachment_id = request.env['ir.attachment'].create({
                    'name': filename,
                    'res_id': lem_sudo.id,
                    'res_model': 'worksheet.lem',
                    'datas': base64.encodebytes(pdf),
                    'type': 'binary',
                    'mimetype': 'application/pdf'
                }).id
        query_string = '&message=sign_ok'
        return {
            'force_refresh': True,
            'redirect_url': lem_sudo.get_portal_url(suffix='/%s' % source, query_string=query_string),
        }