# -*- coding: utf-8 -*-
from odoo import models, fields


class InspectionMaster(models.Model):
    _name = 'inspection.master'
    _description = 'Inspection Master'

    name = fields.Char(string='Name', required=True)
    asset_type_id = fields.Many2one('asset.master', string='Asset Type (Master)')
    frequency = fields.Selection([
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly')
    ], string='Frequency')
    usage_meter_reading = fields.Float(string='Usage Meter Reading')
    usage_uom = fields.Many2one('uom.uom', string='Usage UOM')
    checklist_required = fields.Selection([
        ('required', 'Required'),
        ('not_required', 'Not Required')
    ], string='Checklist Required', default='required')

    checklist_line_ids = fields.One2many(
        'inspection.checklist.line',
        'inspection_id',
        string='Inspection Checklist'
    )


class InspectionChecklistLine(models.Model):
    _name = 'inspection.checklist.line'
    _description = 'Inspection Checklist Line'

    inspection_id = fields.Many2one('inspection.master', string='Inspection')
    section = fields.Char(string='Section')
    task_list = fields.Text(string='Task List')
    expected_value = fields.Char(string='Expected Value Option')
