# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class WorksheetCustomReport(models.AbstractModel):
    _inherit = 'report.industry_fsm_report.worksheet_custom'
    _description = 'Worksheet Custom Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['project.task.worksheet.meta'].browse(docids).sudo()

        worksheet_map = {}
        for sheet in docs:
            if sheet.worksheet_template_id:
                worksheet_map[sheet.id] = sheet._get_worksheet()

        return {
            'doc_ids': docids,
            'doc_model': 'project.task.worksheet.meta',
            'docs': docs,
            'worksheet_map': worksheet_map,
        }
