# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class Opportunity(models.Model):
    _inherit = 'crm.lead'

    asset_id = fields.Char('Asset ID')
    po_number = fields.Char('PO Number')
    location = fields.Char('Customer Location')