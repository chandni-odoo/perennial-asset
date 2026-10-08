# -*- coding: utf-8 -*-
from odoo import models, fields


class AssetFeature(models.Model):
    _name = 'asset.feature'
    _description = 'Asset Features'

    asset_id = fields.Many2one('asset.asset', string='Asset')
    name = fields.Char(string='Feature Name')
    description = fields.Text(string='Description')