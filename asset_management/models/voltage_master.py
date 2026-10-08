# -*- coding: utf-8 -*-
from odoo import models, fields


class VoltageMaster(models.Model):
    _name = 'voltage.master'
    _description = 'Voltage Master'

    name = fields.Integer(string='Voltage')
