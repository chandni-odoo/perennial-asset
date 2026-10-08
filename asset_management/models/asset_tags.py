# -*- coding: utf-8 -*-
from odoo import models, fields


class AssetTag(models.Model):
    _name = 'asset.tags'
    _description = 'Asset Tags'

    name = fields.Char(string='Tag Name', required=True, translate=True)
    color = fields.Integer(string='Color Index')
