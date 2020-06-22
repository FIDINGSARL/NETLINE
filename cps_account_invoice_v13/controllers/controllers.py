# -*- coding: utf-8 -*-
from odoo import http

# class CpsAccountInvoiceV13(http.Controller):
#     @http.route('/cps_account_invoice_v13/cps_account_invoice_v13/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cps_account_invoice_v13/cps_account_invoice_v13/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cps_account_invoice_v13.listing', {
#             'root': '/cps_account_invoice_v13/cps_account_invoice_v13',
#             'objects': http.request.env['cps_account_invoice_v13.cps_account_invoice_v13'].search([]),
#         })

#     @http.route('/cps_account_invoice_v13/cps_account_invoice_v13/objects/<model("cps_account_invoice_v13.cps_account_invoice_v13"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cps_account_invoice_v13.object', {
#             'object': obj
#         })