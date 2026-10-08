# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AssetMaster(models.Model):
    _name = 'asset.master'
    _description = 'Asset Master'


    name = fields.Char(string='Name (Type)', required=True)
    category_id = fields.Many2one('product.category', string='Category', required=True)
    rating = fields.Many2one('rating.master', string='Rating/KVA')
    no_of_phase = fields.Many2one('phase.master', string='No of Phase')
    voltage = fields.Many2one('voltage.master', string='Voltage', required=True)
    make_id = fields.Many2one('asset.make', string='Make')
    measurement_unit_id = fields.Many2one('uom.uom', string='Measurement Unit for Usage', required=True)
    tag_ids = fields.Many2many(
        'asset.tags',
        'asset_tags_rel',
        'asset_id',
        'tag_id',
        string='Tags'
    )
    type_id = fields.Many2one('asset.category', string="Type")
    type_name = fields.Char(related='type_id.name', store=True)
    hz_id = fields.Many2one('asset.hz', string="HZ")
    owner_id = fields.Many2one('asset.owner', string="Asset Owner")
    inspection_master_id = fields.Many2one('inspection.master', string='Inspection Master')
    maintenance_master_id = fields.Many2one('maintenance.master', string='Maintenance Master')

    material_line_ids = fields.One2many('asset.material.line', 'asset_id', string='Asset Materials')
    inspection_line_ids = fields.One2many('inspection.master.line', 'asset_id', string='Inspection Masters')
    maintenance_line_ids = fields.One2many('maintenance.master.line', 'asset_id', string='Maintenance Masters')

    @api.constrains('type_id', 'rating', 'no_of_phase', 'voltage', 'hz_id', 'make_id')
    def _check_required_fields_by_type(self):
        REQUIRED_INFO = {
            'Genset': ['rating', 'no_of_phase', 'voltage', 'hz_id', 'make_id'],
            'Lighting Tower': ['no_of_phase', 'voltage', 'hz_id'],
            'Panels': ['voltage', 'hz_id', 'make_id'],
            'Transformer': ['voltage', 'hz_id', 'make_id'],
            'UPS': ['voltage', 'hz_id', 'make_id'],
            'Load Bank': ['rating', 'voltage', 'hz_id', 'make_id'],
            'Compressor': ['voltage', 'make_id'],
            'Pump': ['voltage', 'make_id'],
            'DG Trolley': ['no_of_phase', 'voltage', 'hz_id'],
            'MLT Trolley': ['rating', 'no_of_phase', 'voltage', 'hz_id', 'make_id'],
        }

        for rec in self:
            type_name = rec.type_id.name
            required_fields = REQUIRED_INFO.get(type_name, [])
            missing = []

            for field_name in required_fields:
                if not getattr(rec, field_name):
                    missing.append(self._fields[field_name].string)

            if missing:
                raise ValidationError(
                    f"For asset type '{type_name}', the following fields are required: {', '.join(missing)}"
                )


class AssetMaterialLine(models.Model):
    _name = 'asset.material.line'
    _description = 'Asset Material Line'

    asset_id = fields.Many2one('asset.master', string='Asset')

    product_id = fields.Many2one('product.product', string='Part No/Product')
    description = fields.Char(string='Description')
    uom_id = fields.Many2one('uom.uom', string='UOM')
    quantity = fields.Integer(string='Quantity')

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for line in self:
            if line.product_id:
                line.description = line.product_id.display_name
                line.uom_id = line.product_id.uom_id.id
            else:
                line.description = False
                line.uom_id = False


class InspectionMasterLine(models.Model):
    _name = 'inspection.master.line'
    _description = 'Inspection Master Line'

    asset_id = fields.Many2one('asset.master', string='Asset')

    inspection_id = fields.Many2one('inspection.master', string="Inspection")
    frequency = fields.Selection([
        ('daily', 'Daily'),
        ('monthly', 'Monthly'),
    ], string='Frequency')

    @api.onchange('inspection_id')
    def _onchange_inspection_id(self):
        for rec in self:
            if rec.inspection_id:
                rec.frequency = rec.inspection_id.frequency


class MaintenanceMasterLine(models.Model):
    _name = 'maintenance.master.line'
    _description = 'Maintenance Master Line'

    asset_id = fields.Many2one('asset.master', string='Asset')

    maintenance_id = fields.Many2one('maintenance.master', string="Maintenance")
    hourly_reading = fields.Integer(string='Hourly Reading')
    frequency = fields.Selection([
        ('daily', 'Daily'),
        ('monthly', 'Monthly'),
    ], string='Frequency')

    @api.onchange('maintenance_id')
    def _onchange_maintenance_id(self):
        for rec in self:
            if rec.maintenance_id:
                rec.frequency = rec.maintenance_id.frequency
