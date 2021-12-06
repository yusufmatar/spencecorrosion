# -*- coding: utf-8 -*-
{
    'name': "Spence Corrosion: FSM Products",

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
    'depends': ['industry_fsm_sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/task_view.xml'
    ],
    # only loaded in demonstration mode
    'demo': [],
    'application': False,
}
