# -*- coding: utf-8 -*-
#############################################################################
#
#
#############################################################################

{
    'name': "Flash Logins",
    'version': '13.0.22.09.01',
    'summary': """Login User Details & IP Address""",
    'description': """This module records login information of user""",
    'author': "Flash Software",
    'website': "https://www.flasof.com",
    'category': 'Tools',
    'depends': ['base'],
    'license': 'AGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'views/login_user_views.xml'],
    'demo': [],
    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
    'external_dependencies': {
        'python': ['httpagentparser']
    }
}
