# -*- coding: utf-8 -*-
from odoo import models, fields


class AssetOwner(models.Model):
    _name = 'asset.owner'
    _description = 'Asset Owner'

    name = fields.Char(string='Name', required=True)

    _sql_constraints = [
        ('unique_owner_name', 'UNIQUE(name)', 'The asset owner name must be unique.')
    ]
