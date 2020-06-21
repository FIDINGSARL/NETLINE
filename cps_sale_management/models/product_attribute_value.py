# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import date

class CpsProductAttributeValue(models.Model):
    _inherit= 'product.attribute.value'
    _order = 'name'

    attribute_name=fields.Char(related='attribute_id.name', store=True, string="Attribute_name")

    def name_get(self):
        res = []
        for rec in self:
            res.append((rec.id, rec.name))
        return res
