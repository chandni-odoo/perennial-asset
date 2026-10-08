# -*- coding: utf-8 -*-
from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_asset = fields.Boolean(string='Is Asset')
    asset_type_id = fields.Many2one('asset.master', string='Asset Type')
    asset_level = fields.Selection([
        ('primary', 'Primary'),
        ('secondary', 'Secondary')
    ], string="Asset Level")


class ProductProduct(models.Model):
    _inherit = "product.product"

    is_asset = fields.Boolean(
        related='product_tmpl_id.is_asset',
        string='Is Asset',
        store=True,
        readonly=False
    )
    asset_type_id = fields.Many2one(
        related='product_tmpl_id.asset_type_id',
        string='Asset Type',
        store=True,
        readonly=False
    )
    asset_level = fields.Selection([
        ('primary', 'Primary'),
        ('secondary', 'Secondary')
    ], string="Asset Level")
