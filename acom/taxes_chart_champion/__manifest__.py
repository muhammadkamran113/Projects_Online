# -*- coding: utf-8 -*-
{
    'name': "taxes_chart_champion",

    'summary': """taxes_chart_champion""",

    'description': """
        taxes_chart_champion
    """,

    'author': "Ehtisham Faisal",
    'website': "http://www.oxenlab.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','account_parent'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
    ],
    # only loaded in demonstration mode
}