# -*- coding: utf-8 -*-
{
    'name': 'Asset Management',
    'version': '18.0',
    'sequence': 1,
    'category': 'Inventory',
    'description':
        """
       Manage company assets and asset masters

    """,
    'depends': ['purchase', 'stock', 'analytic', 'crm', 'fleet', 'account_asset'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/asset_category_demo.xml',
        'data/asset_owner_demo.xml',
        'views/make_view.xml',
        'views/asset_tags_view.xml',
        'views/asset_master_views.xml',
        'views/rating_master_view.xml',
        'views/voltage_master_view.xml',
        'views/phase_master_view.xml',
        'views/asset_view.xml',
        'views/inspection_master_view.xml',
        'views/maintenance_master_view.xml',
        'views/maintenance_order_view.xml',
        'views/inspection_order_view.xml',
        'views/product_view.xml',
        'views/business_unit_view.xml',
        'views/client_view.xml',
        'views/controller_view.xml',
        'views/hz_view.xml',
        'views/owner_view.xml',
        'views/category_view.xml',
        'views/crm_view.xml',
        'views/menu_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}