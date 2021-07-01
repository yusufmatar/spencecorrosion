# -*- coding: utf-8 -*-
{
    'name': "Spence Corrosion: Task Scheduling",

    'summary': """Add start date, end date and duration to task list. """,

    'description': """
Spence Corrosion: Task Scheduling
=================================

Turns the project task list view into an agenda of sorts. Tasks are given a start date
and a duration. The end dates for each task are computed based on the end dates of the
previous task in the list.

Task ID: 2555527
        """,

    'author': 'Odoo Inc',
    'website': 'https://www.odoo.com/',

    'category': 'Custom Development',
    'version': '1.0',
    'license': 'OPL-1',

    # any module necessary for this one to work correctly
    'depends': ['project'],

    # always loaded
    'data': [
        "views/project_task.xml"
    ],
    # only loaded in demonstration mode
    'demo': [],
    'application': False,
}
