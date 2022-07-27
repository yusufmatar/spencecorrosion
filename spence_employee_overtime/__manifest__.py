# -*- coding: utf-8 -*-
{
    'name': "Spence Corrosion: Overtime Lines",

    'summary': """Handle overtime""",

    'description': """
Spence Corrosion: Overtime Lines
================================

Allow users to record two durations, regular and overtime.
    """,

    'author': 'Odoo Inc',
    'website': 'https://www.odoo.com/',

    'category': 'Custom Development',
    'version': '1.0',
    'license': 'OPL-1',

    'depends': ['hr_timesheet','sale_timesheet'],
    'data': [
        'views/hr_employee_views.xml',
        'views/task_views.xml'
    ],
    'application': False,
}
