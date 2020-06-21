# -*- coding: utf-8 -*-
{
    'name': "cps_sale_management_v13",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filtr modules in modules listing
    # Check https://github.com/odoo/odoo/blob/10.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale','mrp', 'hr', 'hr_attendance'],

    # always loaded
    'data': [
        'views/cps_groups.xml',
        'views/cps_decimal_precision.xml',
        'security/ir.model.access.csv',
        'demo/demo.xml',
        'reports/paper_format.xml',
        'reports/ticket_emballage.xml',
        'views/cps_product_traitement.xml',
        'views/cps_product_traitement_liste.xml',
        'views/cps_product_echantillon.xml',
        'views/cps_product_production.xml',
        'views/cps_purchase_order_tree.xml',
        'views/res_partner.xml',
        'views/cps_fiche_procede.xml',
        'views/cps_pantone.xml',
        'views/cps_of_helper.xml',
        'views/cps_reception_helper.xml',
        'views/cps_livraison_helper.xml',
        'views/cps_stock_move.xml',
        'views/cps_settings.xml',
        'views/cps_flux.xml',
        'views/cps_stock_picking.xml',
        'views/cps_stock_picking_type.xml',
        'views/cps_colis_emballage.xml',
        'views/cps_colis_emballage_helper.xml',
        'views/cps_hr_employee.xml',
        'views/cps_hr_correction.xml',
        'reports/fiche_route.xml',
        'views/cps_chariot.xml',
        'views/cps_chariot_helper.xml',
        'views/cps_product_production_report.xml',
        'views/cps_menu.xml',
        'reports/livraison_report.xml',
        'reports/fiche_procede_report.xml',
        'reports/situation_general.xml',
        'reports/detail_es_report.xml',
        'views/cps_tasks.xml',


    ],
    # only loaded in demonstration mode
    'demo': [

    ],
    'qweb': [
        "static/src/xml/attendance.xml",
    ],

}