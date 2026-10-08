# -- coding: utf-8 --
{

    'name': 'Material Requisition and Approval',
    'version': '18.0.1.0',
    'summary': '',
    'description': "This module helps the user to access the Material requisition is a streamlined process for requesting and acquiring stock items from a designated store. Users submit requests, which are checked for availability by inventory managers. Approved requests move through an approval process before items are dispatched to departments. If items are unavailable, a procurement process is initiated. Throughout, actions are tracked, and status updates are provided to users in real-time.",
    'author': '',
    'category': '',
    'depends': ['base', 'purchase', 'stock', 'hr'],
    'license': 'OPL-1',

    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/mail_template.xml',
        'wizards/store_remark_wizard.xml',
        'wizards/approval_wizard.xml',
        'wizards/rfq_po_wizard_view.xml',
        'views/material_requisition_view.xml',
        'views/approval_rule.xml',
        'views/purchase_view.xml',
        'views/menu.xml',
        'report/report_material_requisition.xml',
        'report/material_requisition_template.xml',
    ],

    'installable': True,
    'application': True,
    'auto_install': False,

}
