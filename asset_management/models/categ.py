# -*- coding: utf-8 -*-
from odoo import models, fields


class AssetCategory(models.Model):
    _name = 'asset.category'
    _description = 'Category Type'

    name = fields.Char(string='Name', required=True)

    _sql_constraints = [
        ('unique_category_name', 'UNIQUE(name)', 'The Category type name must be unique.')
    ]
