# -*- coding: utf-8 -*-
from odoo import api, models
from datetime import datetime
import copy

class JournalReports(models.AbstractModel):
    _name = 'report.cps_account_invoice_v13.facture_journal_bl_template'
    _template = 'cps_account_invoice_v13.facture_journal_bl_template'

    @api.model
    def _get_report_values(self, docids, data=None):
        # report_obj = self.env['report.cps_account_invoice_v13.facture_journal_bl_template']
        # report = report_obj._get_report_from_name(self._template)
        print('report gneration-----------------------------', docids[0])

        report = self.env['ir.actions.report']._get_report_from_name(self._template)

        #docids
        facture=self.env["account.invoice.sale"].search([("id", "=", docids[0])])
        print('facture sols----------------------', facture)

        livraisons = []
        lines_textil=[]
        is_laundry = False
        is_pressing = False
        is_vt = False
        is_textil = False
        docargs = {
            'doc_ids': docids,
            'doc_model': report.model,
            'doc': facture,
        }
        for sale_order in facture.sale_order_ids.sorted(key=lambda p: p.date_order):
            livraisons.extend(sale_order.netline_livraison_id)
        #     for livraison in sale_order.netline_livraison_id:
        #         if livraison['is_laundry'] is True:
        #             is_laundry = True
        #         if livraison['is_pressing'] is True:
        #             is_pressing = True
        #         if livraison['is_vt'] is True:
        #             is_vt = True
        print('livraisons----------------------', livraisons)
        articles = []
        # if facture.prestation_type =='Laundry':
        #     articles=self.env["netline.product"].search([("client_id", "=", facture.client_id.id)]).sorted(key=lambda p: p.n_ligne)
        # if facture.prestation_type =='Pressing':
        #     articles = self.env["netline.pressing_product"].search([("client_id", "=", facture.client_id.id)]).sorted(key=lambda p: p.n_ligne)
        # if facture.prestation_type =='Vetement travail':
        #     articles = self.env["netline.vt_product"].search([("client_id", "=", facture.client_id.id)]).sorted(key=lambda p: (p.departement_id.name, p.fonction_id.name, p.id))
        # if is_textil is True:
        #     articles = self.env["netline.textil"].search([("client_id", "=", facture.client_id.id)])

        pages = []
        lines = []

        nb_bon_page = 9
        total_facture=0
        for livraison in livraisons:
            total_facture+=livraison.delivred_quantity
        print('fact lines-------------------------',facture.facturation_lines_ids)
        for article in facture.facturation_lines_ids:
            line = {'article': article.product_description, 'quantities': [], 'total_qty': 0, 'total_facture':total_facture}
            i = 0
            for livraison in livraisons:
                product_quantity = 0
                for livraison_line in livraison.livraison_lines_ids:
                    if livraison_line.reception_line_id.product_id.product_id.id==article.product_id.id or livraison_line.reception_line_id.product_vt_id.product_id.id==article.product_id.id or livraison_line.reception_line_id.product_pressing_id.product_id.id==article.product_id.id:
                        product_quantity += livraison_line.to_deliver_quantity
                line['quantities'].append(product_quantity)
            line['total_qty']=sum(line['quantities'])
            lines.append(line)



        lines2 = []
        quantity_index = 0
        #print len(livraisons), "livraison disponibles"
        while quantity_index < len(livraisons):
            quantity_index += nb_bon_page
            for line in lines:
                new_quantities = line['quantities'][quantity_index-nb_bon_page:quantity_index]
                new_line = {'article': line['article'], 'quantities': new_quantities, 'bons': None, 'total_qty': line['total_qty']}
                lines2.append(new_line)
            bons = livraisons[quantity_index-nb_bon_page:quantity_index]
            lines2.insert(0, {'article': None, 'quantities': [], 'bons': bons, 'total_facture': lines[0]['total_facture']})
            pages.append(lines2)
            lines2 = []

        print('pages------------------------', pages)
        new_pages = []

        for page in pages:
            lines3 = []
            for line in page:
                todelete = True
                if line['article'] is None:
                    todelete = False
                for quantity in line['quantities']:
                    if quantity > 0:
                        todelete = False
                if todelete is False:
                    lines3.append(line)
            page = []
            for l in lines3:
                page.append(l)
            new_pages.append(page)
            docargs = {
                'doc_ids': docids,
                'doc_model': report.model,
                'doc': facture,
                'pages': new_pages,
            }
        print('docargs--------------------------------', docargs)



        #print new_pages[0]
        return docargs
