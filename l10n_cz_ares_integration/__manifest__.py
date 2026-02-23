# -*- coding: utf-8 -*-
{
    'name': "Digital Resources",

    'summary': """
        ARES integration for czech subjects""",

    'description': """
        Fills ARES data for Czech subjects.
    """,
    'license': 'LGPL-3',
    'author': "Digital Resources a.s.",
    'website': "https://www.digres.cz",
    'images': ['static/description/icon.png'],
    'installable': True,
    'version': '0.0.1',

    'depends': ['base'],

    'data': [
        'views/res_partner_views.xml',
        'views/res_config_settings_views.xml',
        'views/l10n_cz_invoice_qr_template.xml',
    ],
}