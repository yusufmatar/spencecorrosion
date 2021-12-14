# -*- coding: utf-8 -*-
{
    'name': "Spence Corrosion: FSM Products",

    'summary': """Move product page into a tab on task""",

    'description': """
Spence Corrosion: FSM Products
==============================

Replaces the Products smart button on tasks with a tab page instead.
    """,

    'author': 'Odoo Inc',
    'website': 'https://www.odoo.com/',
    'category': 'Custom Development',
    'version': '1.0',
    'license': 'OPL-1',
    'depends': ['industry_fsm_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/task_view.xml'
    ],
    'application': False,
}
