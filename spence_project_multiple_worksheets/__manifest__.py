# -*- coding: utf-8 -*-
{
    'name': "Spence Corrosion: Multiple Worksheets",

    'summary': """Multiple worksheets per task""",

    'description': """
Spence Corrosion: Multiple Worksheets
=====================================
Allows for the creation/signing/sending of multiple
worksheet reports per task.

Task ID: 2585433
        """,

    'author': 'Odoo Inc',
    'website': 'https://www.odoo.com/',

    'category': 'Custom Development',
    'version': '1.0',
    'license': 'OEEL-1',

    # any module necessary for this one to work correctly
    'depends': ['industry_fsm_report','sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'report/worksheet_custom_reports.xml',
        'views/worksheet_meta_view.xml',
        'views/project_task_views.xml',
        'views/project_portal_templates.xml',
        'views/sale_order.xml'
    ],
    # only loaded in demonstration mode
    'demo': [],
    'application': False,
}
