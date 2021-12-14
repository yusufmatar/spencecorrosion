# -*- coding: utf-8 -*-
{
    'name': "Spence Corrosion: Map Employees to Sale Order Lines",
    'summary': """Map Employees to Sale Order Lines on the Project""",
    'description': """
Spence Corrosion: Map Employees to Sale Order Lines
===================================================
When sale orders are created with the project intended
to be invoiced at an employee rate, this module will
automatically create the mapping from the employee to
the particular sale order line for that service.

Task ID: 2586808
    """,
    'author': 'Odoo Inc',
    'website': 'https://www.odoo.com/',
    'category': 'Custom Development',
    'version': '1.0',
    'license': 'OPL-1',
    'depends': ['sale_timesheet'],
    'data': [
        'views/product_template.xml',
        'reports/lem.xml'
    ],
    'application': False,
}
