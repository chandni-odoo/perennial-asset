# -*- coding: utf-8 -*-

from odoo import models, fields

class ClientType(models.Model):
    _name = 'client.type'
    _description = 'Type of Client'

    name = fields.Char(string='Client Type Name', required=True)