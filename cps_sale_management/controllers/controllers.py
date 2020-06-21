# -*- coding: utf-8 -*-
from odoo import http

# class CpsAccountInvoiceV13(http.Controller):
#     @http.route('/cps_sale_management/cps_sale_management/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cps_sale_management/cps_sale_management/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cps_sale_management.listing', {
#             'root': '/cps_sale_management/cps_sale_management',
#             'objects': http.request.env['cps_sale_management.cps_sale_management'].search([]),
#         })

#     @http.route('/cps_sale_management/cps_sale_management/objects/<model("cps_sale_management.cps_sale_management"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cps_sale_management.object', {
#             'object': obj
#         })