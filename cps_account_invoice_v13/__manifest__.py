# -*- coding: utf-8 -*-
{
    'name': "cps_account_invoice_v13",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/10.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    #'depends': ['base','account_accountant', 'sale_management','account','stock'],
    'depends': ['base', 'stock',
                'purchase',   'sale_management', 'account','account_accountant'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/account_invoice_sale.xml',
        'views/cps_account_payment_view.xml',
        'views/cps_menu.xml',
        'reports/paper_format.xml',
        'reports/facture_report.xml',
        'reports/avoir_report.xml',
        'reports/cdm_cheque_report.xml',
        'reports/cdm_cheque.xml',
        'reports/bmci_cheque_report.xml',
        'reports/bmci_cheque.xml',
        'reports/virement_report.xml',
        'reports/transfert_interne_bmci.xml',
        'reports/transfert_interne_tijari.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}