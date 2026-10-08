# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AssetAsset(models.Model):
    _name = 'asset.asset'
    _description = 'Asset'

    name = fields.Char(string='Asset Name', required=True)
    asset_code = fields.Char(string='Asset Code', readonly=True, copy=False)
    category_id = fields.Many2one('product.category', string='Asset Category', required=True)
    make_id = fields.Many2one('asset.make', string='Make')
    model_name = fields.Char(string='Asset Model No')
    variant = fields.Char(string='Asset Variant')
    unit = fields.Char(string='Asset Unit')

    rating = fields.Many2one('rating.master', string='Asset Rating/KVA')
    no_of_phase = fields.Many2one('phase.master', string='Phase')
    voltage = fields.Many2one('voltage.master', string='Voltage')

    special_feature = fields.Text(string='Remarks')
    purchase_type = fields.Selection([
        ('purchase', 'Purchase'),
        ('rental', 'Rental'),
    ], string='Purchase/Rental')
    serial_number = fields.Char(string='ESN Serial No', required=True)
    esn_msn = fields.Char(string='Asset_ESN / Asset_MSN')# UNused
    manufacturing_date = fields.Date(string='Asset Manufacturing Year')
    asset_asn = fields.Char(string='Asset_ASN')
    old_asset_code = fields.Char(string='Old Asset Code')
    type_id = fields.Many2one('asset.category', string="Asset Type", required=True)
    type_name = fields.Char(related='type_id.name', store=True)
    owner_id = fields.Many2one('asset.owner', string="Asset Owner")
    hz_id = fields.Many2one('asset.hz', string="HZ")

    @api.model
    def create(self, vals):
        if not vals.get('asset_code'):
            vals['asset_code'] = self.env['ir.sequence'].next_by_code('asset.asset') or 'NEW'
        return super().create(vals)

    # Purchase tab
    purchase_id = fields.Many2one('purchase.order', string='Purchase Order')
    purchase_date = fields.Date(string='Purchase Date')
    ownership_transfer = fields.Boolean(string='Ownership Transfer')
    warranty_expiry_date = fields.Date(string="Warranty Expiry Date")

    # Rerental tab
    rerental_vendor_id = fields.Many2one('res.partner', string='Vendor Name')
    rerental_order_no = fields.Char(string="Rerental Order No", copy=False)

    # Manual selection
    maintenance_scope = fields.Selection([
        ('perennial', 'Perennial'),
        ('vendor', 'Vendor'),
        ('combined', 'Combined')
    ], string="Maintenance Scope")

    # IOT tab
    iot_ids = fields.One2many('asset.iot', 'asset_id', string='IOT Devices')

    # Document tab
    document_ids = fields.One2many('asset.document', 'asset_id', string='Asset Documents')

    # Controller tab
    controller_ids = fields.One2many('asset.controller.line', 'asset_id', string='Controller Details')

    # Inspection
    inspection_schedule_ids = fields.Many2many(
        'inspection.master',
        'asset_inspection_asset_rel',
        'asset_id',
        'inspection_id',
        string='Master Inspection Schedule'
    )

    # MAintenance
    maintenance_ids = fields.Many2many(
        'maintenance.master',
        'maintenance_inspection_rel',
        'inspection_id',
        'maintenance_id',
        string='Master Maintanance Schedule'
    )

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


    # @api.constrains('type_id')
    # def _check_required_fields(self):
    #     REQUIRED_MATRIX = {
    #         'Genset': ['category_id', 'asset_code', 'serial_number', 'asset_asn', 'rating', 'make_id', 'model_name', 'manufacturing_date', 'purchase_type', 'owner_id', 'unit', 'voltage', 'hz_id', 'no_of_phase', 'old_asset_code'],
    #         'Lighting Tower': ['category_id', 'asset_code', 'serial_number', 'model_name', 'manufacturing_date', 'purchase_type', 'owner_id', 'unit', 'voltage', 'hz_id', 'no_of_phase'],
    #         'Panels': ['category_id', 'asset_code', 'serial_number', 'make_id', 'model_name', 'manufacturing_date', 'purchase_type', 'owner_id', 'unit', 'voltage', 'hz_id', 'no_of_phase'],
    #         'Transformer': ['category_id', 'asset_code', 'serial_number', 'make_id', 'model_name', 'manufacturing_date', 'purchase_type', 'owner_id', 'unit', 'voltage', 'hz_id', 'no_of_phase'],
    #         'UPS': ['category_id', 'asset_code', 'serial_number', 'make_id', 'model_name', 'manufacturing_date', 'purchase_type', 'owner_id', 'unit', 'voltage', 'hz_id', 'no_of_phase'],
    #         'Load Bank': ['category_id', 'asset_code', 'serial_number', 'rating', 'make_id', 'model_name', 'manufacturing_date', 'purchase_type', 'owner_id', 'unit', 'voltage'],
    #         'Compressor': ['category_id', 'asset_code', 'serial_number', 'model_name', 'manufacturing_date', 'purchase_type', 'owner_id', 'unit', 'voltage'],
    #         'Pump': ['category_id', 'asset_code', 'serial_number', 'model_name', 'manufacturing_date', 'purchase_type', 'owner_id', 'unit', 'voltage'],
    #         'DG Trolley': ['category_id', 'asset_code', 'serial_number', 'asset_asn', 'model_name', 'manufacturing_date', 'purchase_type', 'owner_id', 'unit', 'voltage', 'hz_id', 'no_of_phase', 'old_asset_code'],
    #         'MLT Trolley': ['category_id', 'asset_code', 'serial_number', 'asset_asn', 'rating', 'make_id', 'model_name', 'manufacturing_date', 'purchase_type', 'owner_id', 'unit', 'voltage', 'hz_id', 'no_of_phase', 'old_asset_code'],
    #     }

    #     for record in self:
    #         controller_name = record.category_id.name
    #         required_fields = REQUIRED_MATRIX.get(controller_name, [])
    #         missing_fields = [field for field in required_fields if not record[field]]
    #         if missing_fields:
    #             raise ValidationError(
    #                 f"The following fields are required for {controller_name}: {', '.join(missing_fields)}"
    #             )
