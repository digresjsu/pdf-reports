# -*- coding: utf-8 -*-
{
    'name': "Digital Resources",

    'summary': """
        Digital resources tools module""",

    'description': """
        Additional features
    """,
    'license': 'LGPL-3',
    'author': "Digital Resources a.s.",
    'website': "https://www.digres.cz",
    'application': True,
    'images': ['static/description/icon.png'],

    'category': 'Uncategorized',
    'version': '0.0.3',

    'depends': ['base', 'accountant', 'contacts', 'sale_management', 'purchase', 'stock', 'base_automation'],

    'data': [
        'security/ir.model.access.csv',
        'views/company_name_history_views.xml',
        'views/record_change_tracker_views.xml',
        'views/account_move_views.xml',
    ]
}