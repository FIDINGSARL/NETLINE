# -*- coding: utf-8 -*-
{
    'name': "netline",
    'application': True,
    'summary': """
        Gestion de laverie industrielle""",

    'description': """
        Gestion compléte de laverie industrielle :
           - Gestion Lavage.
           - Gestion Pressing.
    """,

    'author': "NETBEAM IT",
    'website': "http://www.netbeam.ma",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Gestion blanchisserie industrielle',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'crm', 'project', 'stock', 'point_of_sale', 'hr_timesheet', 'hr_holidays', 'website', 'purchase', 'purchase_requisition', 'hr', 'hr_attendance', 'hr_recruitment','hr_expense', 'board','survey', 'maintenance', 'fleet', 'product', 'sale', 'account', 'sale_stock', 'account_accountant'],

    # always loaded
    'data': [
        'views/groups.xml',
        'security/ir.model.access.csv',
        # 'views/netline_forfait.xml',
        'views/product_generic_laundry.xml',
        'views/product_generic_pressing.xml',
        'views/product_generic_vt.xml',
        'views/product_criteria.xml',
        'views/clients.xml',
        'views/client_product_laundry.xml',
        'views/client_product_pressing.xml',
        'views/client_product_vt.xml',
        # 'views/client_product_vente.xml',
        'views/netline_reception.xml',
        'views/netline_livraison.xml',
        'reports/paper_format.xml',
        'reports/reception_report.xml',
        'reports/livraison_header_report.xml',
        'reports/livraison_report.xml',
        'reports/livraison_vt_report.xml',
        'reports/livraison_pressing_report.xml',
        # 'reports/livraison_textil_report.xml',
        # 'reports/livraison_echantillon_report.xml',
        # 'reports/retour_report.xml',
        # 'reports/retour_textil_report.xml',
        # 'reports/retour_vt_report.xml',
        # 'reports/retour_echantillon_report.xml',
        # 'reports/retour_pressing_report.xml',
        # 'reports/manque_general_report.xml',
        # 'reports/livraison_pressing_report.xml',
        # 'reports/manque_report.xml',
        # 'reports/facture_report.xml',
        # 'reports/facture_journal_report.xml',
        # 'reports/facture_journal_bl_report.xml',
        # 'reports/facture_journal_bl_final_report.xml',
        # 'reports/facture_journal_bl_textil_final_report.xml',
        # 'reports/echantillon_fiche.xml',
        # 'reports/echantillon_fiche_reception.xml',
        # 'reports/commande_report.xml',
        # 'reports/facture_purchase_report.xml',
        # 'reports/rh_resume.xml',
        # 'reports/transfert_sortie_report.xml',
        # 'security/ir.model.access.csv',
        # 'data/crons.xml'
        'views/netline_menu.xml',
    ],
}
