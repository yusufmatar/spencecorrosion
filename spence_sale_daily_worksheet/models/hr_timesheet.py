# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    reported = fields.Boolean("Reported", default=False, readonly=True)

    def _mark_timesheets_reported(self):
        for sheet in self:
            sheet.reported = True