# -*- coding: utf-8 -*-
from odoo import models, fields, api


class MaintenanceRequest(models.Model):
    _name = 'maintenance.request'
    _description = 'Maintenance Request Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Request No', required=True, copy=False, readonly=True, default='New')
    asset_id = fields.Many2one('asset.asset', string='Asset Name')
    serial_number = fields.Char(string='Serial Number', related='asset_id.serial_number')
    location = fields.Char(string='Location')
    assigned_to = fields.Many2one('res.users', string='Assign To')
    inward_date = fields.Date(string='Inward Date')
    estimated_delivery_date = fields.Date(string='Estimation Delivery Date')
    maintenance_master_id = fields.Many2one('maintenance.master', string='Maintenance Master')
    actual_delivery_date = fields.Date(string='Actual Delivery Date')
    er_no = fields.Char(string='ER No')
    customer_name = fields.Char(string='Customer Name')

    stage = fields.Selection([
        ('new', 'New Request'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancel', 'Cancel')
    ], default='new', string='Stage', tracking=True)

    pre_inspection_ids = fields.One2many('maintenance.request.pre.inspection', 'request_id', string='Pre Inspection')
    job_card_ids = fields.One2many('maintenance.request.job.card', 'request_id', string='Job Card')
    final_inspection_ids = fields.One2many('maintenance.request.final.inspection', 'request_id', string='Final Inspection')
    timesheet_ids = fields.One2many('account.analytic.line', 'maintenance_request_id', string='Timesheet')

    # @api.model
    # def create(self, vals):
    #     if vals.get('name', 'New') == 'New':
    #         vals['name'] = self.env['ir.sequence'].next_by_code('maintenance.request') or 'MR/00000'
    #     return super().create(vals)

    def action_material_requisition(self):
        # Custom logic
        pass

    def action_create_sales_order(self):
        # Custom logic
        pass

    def action_create_invoice(self):
        # Custom logic
        pass


class MaintenanceRequestPreInspection(models.Model):
    _name = 'maintenance.request.pre.inspection'
    _description = 'Pre Inspection'

    request_id = fields.Many2one('maintenance.request')
    section = fields.Char(string='Section')
    item = fields.Char(string='Item')
    issue = fields.Text(string='Issue')
    remarks = fields.Text(string='Remarks')


class MaintenanceRequestJobCard(models.Model):
    _name = 'maintenance.request.job.card'
    _description = 'Job Card'

    request_id = fields.Many2one('maintenance.request')
    section = fields.Char(string='Section')
    type = fields.Selection([
        ('service', 'Service'),
        ('product', 'Product')
    ], string='Type')
    product_id = fields.Many2one('product.product', string='Product Name')
    activity = fields.Text(string='Activity')
    quantity = fields.Float(string='Qty')
    uom_id = fields.Many2one('uom.uom', string='UOM')
    cost = fields.Float(string='Cost')
    unit_price = fields.Float(string='Unit Price')
    tax_ids = fields.Many2many('account.tax', string='Tax')
    subtotal = fields.Float(string='Sub Total', compute='_compute_subtotal')
    remarks = fields.Text(string='Remarks')
    technician_id = fields.Many2one('res.partner', string='Technician Name')

    @api.depends('quantity', 'unit_price', 'cost')
    def _compute_subtotal(self):
        for rec in self:
            rec.subtotal = (rec.unit_price + rec.cost) * rec.quantity


class MaintenanceRequestFinalInspection(models.Model):
    _name = 'maintenance.request.final.inspection'
    _description = 'Final Inspection'

    request_id = fields.Many2one('maintenance.request')
    section = fields.Char(string='Section')
    item = fields.Char(string='Item')
    issue = fields.Text(string='Issue')
    remarks = fields.Text(string='Remarks')


# Optional: Extend account.analytic.line for timesheet link
class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    maintenance_request_id = fields.Many2one('maintenance.request', string='Maintenance Request')
