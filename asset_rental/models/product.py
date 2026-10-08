# -*- coding: utf-8 -*-
from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    rerent_ok = fields.Boolean(string="RE-Rented")
    rental_intervals = fields.Many2many('rental.intervals', string='RE-Rented Intervals')


class ProductProduct(models.Model):
    _inherit = 'product.product'

    rerent_ok = fields.Boolean(related='product_tmpl_id.rerent_ok', string="RE-Rented", readonly=False)
    rental_intervals = fields.Many2many(related='product_tmpl_id.rental_intervals', string='RE-Rented Intervals')
