# -*- coding: utf-8 -*-
{
    'name': "Spence Corrosion: Overtime Lines",

    'summary': """""",

    'description': """
        []
        """,

    'author': 'Odoo Inc',
    'website': 'https://www.odoo.com/',

    'category': 'Custom Development',
    'version': '1.0',
    'license': 'OPL-1',

    # any module necessary for this one to work correctly
    'depends': ['hr_timesheet'],

    # always loaded
    'data': [
        'views/hr_employee_views.xml',
        'views/task_views.xml'
    ],
    # only loaded in demonstration mode
    'demo': [],
    'application': False,
}
