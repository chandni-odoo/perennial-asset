# -*- coding: utf-8 -*-

from odoo import models, fields

class BusinessUnit(models.Model):
    _name = 'business.unit'
    _description = 'Business Unit'

    name = fields.Char(string='Business Unit Name', required=True)