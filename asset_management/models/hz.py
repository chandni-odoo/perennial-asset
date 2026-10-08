# -*- coding: utf-8 -*-
from odoo import models, fields


class AssetTHZ(models.Model):
    _name = 'asset.hz'
    _description = 'HZ Value'

    name = fields.Integer(string='Name')


    _sql_constraints = [
        ('unique_hz_name', 'UNIQUE(name)', 'The HZ value must be unique.')
    ]
