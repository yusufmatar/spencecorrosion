# -*- coding: utf-8 -*-
{
    'name': "Spence Corrosion: LEM Reports",

    'summary': """""",

    'description': """
        []
        """,

    'author': 'Odoo Inc',
    'website': 'https://www.odoo.com/',

    'category': 'Custom Development',
    'version': '1.0',
    'license': 'OEEL-1',

    # any module necessary for this one to work correctly
    'depends': ['sale_crm','sale_project','industry_fsm_report'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/crm_lead.xml',
        'views/worksheet_lem.xml',
        'views/project_task.xml',
        'views/sale_order.xml',
        'views/product_template.xml',
        'views/portal.xml',
        'reports/lem_report_components.xml',
        'reports/lem.xml',
        'reports/costed_lem.xml',
        'reports/report_actions.xml',
        'reports/report_templates.xml'
    ],
    'application': False,
}
