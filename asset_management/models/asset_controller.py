# -*- coding: utf-8 -*-
from odoo import models, fields


class AssetControllerDetails(models.Model):
    _name = 'asset.controller.line'
    _description = 'Asset Controller Details'

    asset_id = fields.Many2one('asset.asset', string='Asset')
    controller_id = fields.Many2one('asset.controller', string="Controller")
    manufacturing_year = fields.Integer(string='Manufacturing Year')
    current_hr_reading = fields.Integer(string='Current HR Reading')#, compute='_compute_hr_reading')
    status = fields.Selection([
        ('active', 'Active'),
        ('deactive', 'Deactive')
    ], string='Status', default='active')

    # @api.depends()
    # def _compute_hr_reading(self):
    #     for record in self:
    #         record.current_hr_reading = 0  # Replace with actual logic if available
