# -*- coding: utf-8 -*-
from odoo import models, fields


class AssetController(models.Model):
    _name = 'asset.controller'
    _description = 'Controller Type'

    name = fields.Char(string='Name', required=True)

    _sql_constraints = [
        ('unique_controller_name', 'UNIQUE(name)', 'The controller type name must be unique.')
    ]
