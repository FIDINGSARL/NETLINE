# -*- coding: utf-8 -*-
from odoo.tests import common

import datetime

class TestReception(common.TransactionCase):
    at_install = False
    post_install = True

    def test_01_reception_laundry_add(self):
        #"testing"

        res_partner = {'name': 'test client', "is_company": True, 'invoice_warn': 'no-message'}
        res_partner_row = self.env['res.partner'].create(res_partner)

        product_template = {"purchase_line_warn": "no-message", 'product_variant_ids': [], "name": "test product"}
        product_template_row = self.env["product.template"].create(product_template)

        product_product = {'product_variant_id': [], 'product_tmpl_id': product_template_row.id, "name": "test product",
                           'is_laundry': True}
        product_product_row = self.env["product.product"].create(product_product)

        reception_lines = []
        netline_product = {'name': "test product", 'prix_lavage': 2, 'prix_detachage': 3, 'prix_decatissage': 4,
                           'prix_lavage_sec': 5, 'prix_repassage': 6, 'product_id': product_product_row.id,
                           'client_id':res_partner_row.id}
        netline_product_row = self.env["netline.product"].create(netline_product)

        reception_line_traitement_lavage = {'product_id': netline_product_row.id,'traitement': 'lavage', 'quantity':2}
        reception_line_traitement_detachage = {'product_id': netline_product_row.id,'traitement': 'detachage', 'quantity':2}
        reception_line_traitement_decatissage = {'product_id': netline_product_row.id,'traitement': 'decatissage', 'quantity':2}
        reception_line_traitement_lavage_sec = {'product_id': netline_product_row.id,'traitement': 'lavage_sec', 'quantity':2}
        reception_line_traitement_repassage = {'product_id': netline_product_row.id,'traitement': 'repassage', 'quantity':2}
        reception_lines.append((0, 0, reception_line_traitement_lavage))
        reception_lines.append((0, 0, reception_line_traitement_detachage))
        reception_lines.append((0, 0, reception_line_traitement_decatissage))
        reception_lines.append((0, 0, reception_line_traitement_lavage_sec))
        reception_lines.append((0, 0, reception_line_traitement_repassage))

        #product_template_row
        #product_product_row
        reception = self.env["netline.reception"].create({'client_id': 1, 'date_reception': datetime.datetime.now(),
                                                          "receptionline_ids": reception_lines})

        for reception_line in reception.receptionline_ids:
            if reception_line.traitement == 'lavage':
                self.assertEqual(reception_line.purchase_order_line_ids[0].price_unit, 2)
                self.assertEqual(reception_line.purchase_order_line_ids[0].price_subtotal, 4)
            elif reception_line.traitement == 'detachage':
                self.assertEqual(reception_line.purchase_order_line_ids[0].price_unit, 3)
                self.assertEqual(reception_line.purchase_order_line_ids[0].price_subtotal, 6)
            elif reception_line.traitement == 'decatissage':
                self.assertEqual(reception_line.purchase_order_line_ids[0].price_unit, 4)
                self.assertEqual(reception_line.purchase_order_line_ids[0].price_subtotal, 8)
            elif reception_line.traitement == 'lavage_sec':
                self.assertEqual(reception_line.purchase_order_line_ids[0].price_unit, 5)
                self.assertEqual(reception_line.purchase_order_line_ids[0].price_subtotal, 10)
            elif reception_line.traitement == 'repassage':
                self.assertEqual(reception_line.purchase_order_line_ids[0].price_unit, 6)
                self.assertEqual(reception_line.purchase_order_line_ids[0].price_subtotal, 12)
        #reception.client_id

        #"reception"
        #reception
        self.assertEqual("", "")

    def test_02_create(self):
        #"test_create"
        self.assertEqual("az", "az")