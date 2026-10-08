# -*- coding: utf-8 -*-
{
    'name': "Asset Rental Purchase ",
    'summary': "Manage rentals from vendors via purchase rental orders",
    'description': """
This module allows users to handle product rentals from vendors, track rented quantities, pricing,
and returns within the purchase workflow.
    """,
    'author': 'Chandni Patel@Xenlogic Technologies Pvt Ltd',
    'website': 'https://www.xenlogictech.com/',
    'category': 'Purchases/Rentals',
    'version': '18.0',
    'depends': ['crm', 'purchase', 'stock', 'account', 'mail',],
    'data': [
        # XML views, actions, menus go here
        'security/ir.model.access.csv',
        'data/rental_data.xml',
        'data/cron_data.xml',
        #Custom
        'views/rental_intervals_view.xml',
        #Inherit
        'views/product_view.xml',
        'views/purchase_view.xml',
        'views/po_rental_view.xml',
        'views/res_partner_view.xml',
        #Menu
        'views/menu_view.xml',
    ],
    'installable': True,
    'application': True,
}