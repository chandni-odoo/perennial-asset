# -*- coding: utf-8 -*-
from odoo import models, fields


class AssetIOT(models.Model):
    _name = 'asset.iot'
    _description = 'IOT Devices'

    asset_id = fields.Many2one('asset.asset', string='Asset')
    name = fields.Char(string='IOT Device Name')
    qr_code = fields.Char(string='IOT Device QR Code')