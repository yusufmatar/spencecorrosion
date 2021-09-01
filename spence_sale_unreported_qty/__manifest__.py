# -*- coding: utf-8 -*-
{
    'name': "Spence Corrosion: Unreported Lines",

    'summary': """Add a new Unreported Qty to sale order line""",

    'description': """
Spence Corrosion: Daily Worksheets
==================================
We add a new field on sale order lines that resets to zero whenever
a report is generated. Same thing for timesheets.

Task ID: 2603796
    """,

    'author': 'Odoo Inc',
    'website': 'https://www.odoo.com/',

    'category': 'Custom Development',
    'version': '1.0',
    'license': 'OPL-1',

    # any module necessary for this one to work correctly
    'depends': ['spence_lem_reports'],

    # always loaded
    'data': [
        'views/sale.xml',
        'reports/lem.xml'
    ],
    'application': False,
}
