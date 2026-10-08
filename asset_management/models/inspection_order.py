# -*- coding: utf-8 -*-
from odoo import models, fields


class InspectionOrder(models.Model):
    _name = 'inspection.order'
    _description = 'Inspection Order'

    customer_name = fields.Char(string='Customer Name')
    asset_id = fields.Many2one('asset.master', string='Asset Name')
    product_id = fields.Many2one('product.product', string='Product Name')
    serial_number = fields.Char(string='Serial Number')
    location = fields.Char(string='Location')
    assign_to = fields.Many2one('res.users', string='Assign To')
    inspection_master_id = fields.Many2one('inspection.master', string='Inspection Master')
    scheduled_date = fields.Date(string='Scheduled Date')
    inspected_date = fields.Date(string='Inspected Date')

    inspection_line_ids = fields.One2many('inspection.line', 'order_id', string='Inspection Lines')

    stage = fields.Selection([
        ('new', 'New Request'),
        ('progress', 'In Progress'),
        ('done', 'Done'),
        ('cancel', 'Cancel')
    ], string='Stage', default='new')

    def action_create_maintenance_order(self):
        self.stage = 'progress'
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': 'Maintenance Order Created!',
                'sticky': False,
                'type': 'success',
            }
        }

class InspectionLine(models.Model):
    _name = 'inspection.line'
    _description = 'Inspection Line'

    order_id = fields.Many2one('inspection.order', string='Inspection Order', ondelete='cascade')
    section = fields.Char(string='Section')
    item = fields.Char(string='Item')
    activity = fields.Char(string='Activity')
    remarks = fields.Text(string='Remarks')
