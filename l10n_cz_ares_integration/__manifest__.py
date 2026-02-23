# -*- coding: utf-8 -*-
{
    'name': "DIG ARES Integration",

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

    'depends': ['base', 'contacts'],

    'data': [
        'views/res_partner_views.xml',
    ],
}