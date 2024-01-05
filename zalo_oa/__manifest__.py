# -*- coding: utf-8 -*-
# Lv Quy

{
    'name': 'Odoo Chat Zalo OA',
    'version': '1',
    'license': 'AGPL-3',
    'summary': 'Odoo Zalo OA',
    'description': 'Zalo OA API connection',
    'author': 'Lv Quy',
    'company': 'itricks.me',
    'maintainer': 'itricks.me',
    'website': 'https://itricks.me',
    'depends': ['base', 'base_setup', 'mail','website_blog','contacts'],
    'data': [
        # security
        'security/ir.model.access.csv',
        # data
        'data/cronjob.xml',
        # 'data/mail_channel_data.xml',
        # 'data/user_partner_data.xml',
        # views
        'views/res_config_settings_views.xml',
        'views/zalo_oa.xml',
        'views/chat_zalo.xml',
        'views/res_partner.xml',
    ],
    'js':['static/src/script.js'],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}