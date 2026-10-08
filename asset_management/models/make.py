# -*- coding: utf-8 -*-
from odoo import models, fields


class AssetMake(models.Model):
    _name = 'asset.make'
    _description = 'Asset Make'

    name = fields.Char(string='Name', required=True)

    _sql_constraints = [
        ('unique_make_name', 'UNIQUE(name)', 'The Make name must be unique.')
    ]
