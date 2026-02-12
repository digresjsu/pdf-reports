# -*- coding: utf-8 -*-
{
    'name': "Digital Resources",

    'summary': """
        Czech localization for QR codes""",

    'description': """
        Adds the option to generate QR codes for payments in the Czech Republic using the QR platba codes.
    """,
    'license': 'LGPL-3',
    'author': "Digital Resources a.s.",
    'website': "https://www.digres.cz",
    'images': ['static/description/icon.png'],
    'installable': True,
    'category': 'Accounting/Localization',
    'version': '0.0.3',

    'depends': ['base','account'],

    'data': [
        'views/res_config_settings_views.xml',
    ],
}