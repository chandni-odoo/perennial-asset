# -*- coding: utf-8 -*-
from odoo import models, fields


class PhaseMaster(models.Model):
    _name = 'phase.master'
    _description = 'Phase Master'

    name = fields.Integer(string='Phase')

    _sql_constraints = [
        ('unique_phase_name', 'UNIQUE(name)', 'The Phase must be unique.')
    ]
