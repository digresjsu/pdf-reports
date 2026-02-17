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
    'version': '0.0.5',

    'depends': ['base','account'],

    'data': [
        'views/res_config_settings_views.xml',
        'views/l10n_cz_qr_code_templates.xml',
    ],
}