# -*- coding: utf-8 -*-
from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    requisition_id = fields.Many2one('material.requisition', string='Requisition')


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    mr_line_id = fields.Many2one('material.requisition.line', string='Material Requisition', copy=False)
