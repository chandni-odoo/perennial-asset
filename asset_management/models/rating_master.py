# -*- coding: utf-8 -*-
from odoo import models, fields


class RatingMaster(models.Model):
    _name = 'rating.master'
    _description = 'Rating KVA Master'

    name = fields.Integer(string='Rating/KVA')

    _sql_constraints = [
        ('unique_rating_name', 'UNIQUE(name)', 'The Rating value must be unique.')
    ]
