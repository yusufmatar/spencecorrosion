# -*- coding: utf-8 -*-
{
    'name': "Spence Corrosion: Daily Worksheets",

    'summary': """Only show new stuff from sale order on worksheet reports""",

    'description': """
Spence Corrosion: Daily Worksheets
==================================
Worksheets reports will only display new/updated line items on the worksheet report
compared to when the last report was created, usually daily.

Task ID: 2603796
    """,

    'author': 'Odoo Inc',
    'website': 'https://www.odoo.com/',

    'category': 'Custom Development',
    'version': '1.0',
    'license': 'OPL-1',

    # any module necessary for this one to work correctly
    'depends': ['sale', 'spence_project_multiple_worksheets'],

    # always loaded
    'data': [
        'views/sale.xml'
    ],
    'application': False,
}
