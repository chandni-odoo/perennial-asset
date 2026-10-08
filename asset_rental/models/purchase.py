# -*- coding: utf-8 -*-
from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    re_rental_order_id = fields.Many2one('purchase.rental.order', string="Re-Rental Order")
    payment_date = fields.Date(string="Payment Date")

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    is_rerental = fields.Boolean(string='Re-Rental Line?')
    rental_line_id = fields.Many2one('purchase.rental.order.line', string='Re-Rental', copy=False)
