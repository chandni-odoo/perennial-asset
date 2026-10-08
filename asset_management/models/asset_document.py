# -*- coding: utf-8 -*-
from odoo import models, fields


class AssetDocument(models.Model):
    _name = 'asset.document'
    _description = 'Asset Documents'

    asset_id = fields.Many2one('asset.asset', string='Asset')
    name = fields.Char(string='Document Name')
    document_date = fields.Date(string='Document Date')
    expiry_date = fields.Date(string='Expiry Date')
    certificate_attachment = fields.Binary(string='Certificates Attachment')
    attachment_filename = fields.Char(string='Attachment Filename')
