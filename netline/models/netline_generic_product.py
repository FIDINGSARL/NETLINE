# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions

class Netline_genericlaundry_template(models.Model):
    _name = 'netline.genericproduct'
    product_generic_id = fields.Many2one('product.product', string="Netline Generic Product")
    product_name = fields.Char("Nom Produit")
    product_categ = fields.Many2one('product.category')
    is_generic = fields.Boolean("generic", default=True)

    def name_get(self):
        res = []
        # designation_client, designation, type, couleur
        for rec in self:
            res.append((rec.id, rec.product_name))
        return res

    @api.model
    def create(self, values):
        generic_product = self.env['netline.genericproduct'].search([('product_name', 'ilike', values.get('product_name')),('product_categ', '=', values.get('product_categ'))])
        if len(generic_product) == 0 :
            pProduct = self.env['product.product'].create({
                'name': values.get('product_name'),
                'categ_id':values.get('product_categ'),
                'is_laundry':True
            })
            values['product_generic_id'] = pProduct.id
            product = super(Netline_genericlaundry_template, self).create(values);
            return product
        else:
            raise exceptions.ValidationError("Cet article existe déjà !")
        

    def write(self, values):
        Product = super(Netline_genericlaundry_template, self).write(values)
        self.product_generic_id.product_tmpl_id.write({'name': self.product_name, 'categ_id': self.product_categ.id})

        return Product
        

    def unlink(self):
        product_product = self.env['product.product'].search([('id', '=', self.product_generic_id.id)])
        #netline_compter
        #self.product_generic_id.id
        product_product.unlink()
        Product = super(Netline_genericlaundry_template, self).unlink()
        return Product

class Netline_genericpressing_template(models.Model):
    _name = 'netline.genericproduct_pressing'
    product_generic_id = fields.Many2one('product.product', 'Netline Generic Product Pressing',  domain='[("is_pressing", "=", True)]')
    product_name = fields.Char("Nom Produit")
    product_categ = fields.Many2one(related="product_generic_id.categ_id",store=True)
    is_pressing = fields.Boolean("pressing", default=True)


    def name_get(self):
        res = []
        # designation_client, designation, type, couleur
        for rec in self:
            res.append((rec.id, rec.product_name))
        return res

    @api.model
    def create(self, values):
        pressing_product = self.env['netline.genericproduct_pressing'].search([('product_name', 'ilike', values.get('product_name')),('product_categ', '=', values.get('product_categ'))])
        if len(pressing_product) == 0 :
            pProduct = self.env['product.product'].create({
                'name': values.get('product_name'),
                'categ_id':values.get('product_categ'),
                'is_pressing':True
            })
            values['product_generic_id'] = pProduct.id
            product = super(Netline_genericpressing_template, self).create(values);
            return product
        else:
            raise exceptions.ValidationError("Cet article existe déjà !")


    def write(self, values):
        Product = super(Netline_genericpressing_template, self).write(values)
        self.product_generic_id.product_tmpl_id.write({'name': self.product_name, 'categ_id': self.product_categ.id})

        return Product
        

    def unlink(self):
        pressing_product = self.env['product.product'].search([('id', '=', self.product_generic_id.id)])
        pressing_product.unlink()
        Product = super(Netline_genericpressing_template, self).unlink()
        return Product
    
class Netline_genericvt_template(models.Model):
    _name = 'netline.genericproduct_vt'
    product_generic_id = fields.Many2one('product.product', 'Netline Generic Product Vetement Traival',  domain='[("is_pressing", "=", True)]')
    product_name = fields.Char("Nom Produit")
    product_categ = fields.Many2one(related="product_generic_id.categ_id",store=True)
    is_vt = fields.Boolean("Vetement Travail", default=True)


    def name_get(self):
        res = []
        # designation_client, designation, type, couleur
        for rec in self:
            res.append((rec.id, rec.product_name))
        return res

    @api.model
    def create(self, values):
        vt_product = self.env['netline.genericproduct_vt'].search([('product_name', 'ilike', values.get('product_name')),('product_categ', '=', values.get('product_categ'))])
        if len(vt_product) == 0 :
            pProduct = self.env['product.product'].create({
                'name': values.get('product_name'),
                'categ_id':values.get('product_categ'),
                'is_vt':True
            })
            values['product_generic_id'] = pProduct.id
            product = super(Netline_genericvt_template, self).create(values);
            return product    
        else:
            raise exceptions.ValidationError("Cet article existe déjà !")


    def write(self, values):
        Product = super(Netline_genericvt_template, self).write(values)
        self.product_generic_id.product_tmpl_id.write({'name': self.product_name, 'categ_id': self.product_categ.id})
        return Product
        

    def unlink(self):
        vt_product = self.env['product.product'].search([('id', '=', self.product_generic_id.id)])
        vt_product.unlink()
        Product = super(Netline_genericvt_template, self).unlink()
        return Product
