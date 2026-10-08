# -*- coding: utf-8 -*-
from odoo import models, fields


class MaintenanceMaster(models.Model):
    _name = 'maintenance.master'
    _description = 'Maintenance Master'

    name = fields.Char(string='Name', required=True)
    asset_type_id = fields.Many2one('asset.master', string='Asset Type (Master)')
    frequency = fields.Selection([
        ('daily', 'Daily'),
        ('monthly', 'Monthly'),
    ], string='Frequency')
    usage_meter_reading = fields.Float(string='Usage Meter Reading')
    usage_uom = fields.Many2one('uom.uom', string='Usage UOM')
    checklist = fields.Text(string='Checklist')

    checklist_line_ids = fields.One2many(
        'maintenance.checklist.line',
        'maintenance_id',
        string='Maintenance Checklist Lines'
    )


class MaintenanceChecklistLine(models.Model):
    _name = 'maintenance.checklist.line'
    _description = 'Maintenance Checklist Line'

    maintenance_id = fields.Many2one('maintenance.master', string='Maintenance')
    section = fields.Char(string='Section')
    type = fields.Selection([
        ('service', 'Service'),
        ('product', 'Product')
    ], string='Type')
    product_id = fields.Many2one('product.product', string='Product Name/Item')
    activity = fields.Text(string='Activity')
