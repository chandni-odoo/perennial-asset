# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    po_loi_no = fields.Integer(string="P.O. / LOI NO.")
    po_loi_date = fields.Date(string="P.O. / LOI Date")
    business_unit_id = fields.Many2one('business.unit', string="Business Unit")
    client_type_id = fields.Many2one('client.type', string="Type of Client")
    safety_sensitivity = fields.Selection([
        ('high', 'Highest'),
        ('moderate', 'Moderate'),
        ('low', 'Low')
    ], string="Safety Type", default='high')

    asset_requirement_ids = fields.One2many('crm.asset.requirement', 'lead_id', string="Assets Requirement")
    asset_scope_of_work_ids = fields.One2many('crm.asset.scope.of.work', 'lead_id', string="Scope Of Work")
    document_line_ids = fields.One2many('lead.document.line', 'lead_id', string='Document Lines')
    logistics_line_ids = fields.One2many('lead.logistics.line', 'lead_id', string='Logistics Lines')
    related_contact_ids = fields.One2many('res.partner', 'lead_id', string='Related Contacts')

    user_id = fields.Many2one('res.users', string='Salesperson')
    sale_payment_term_id = fields.Many2one('account.payment.term', string='Sale Payment Terms')
    sale_payment_method = fields.Selection([('cash', 'Cash'), ('bank', 'Bank')], string='Sale Payment Method')

    buyer_id = fields.Many2one('res.users', string='Buyer')
    purchase_payment_term_id = fields.Many2one('account.payment.term', string='Purchase Payment Terms')
    purchase_payment_method = fields.Selection([('cash', 'Cash'), ('bank', 'Bank')], string='Purchas Payment Method')
    receipt_reminder = fields.Boolean(string='Receipt Reminder')
    # address_title = fields.Char(string='title')
    # related_contact_ids = fields.One2many(
    #     'res.partner',
    #     'lead_id',
    #     string='Child Contacts',
    #     related='partner_id.child_ids',
    #     readonly=False  # Important: makes it editable
    # )

    # @api.depends('partner_id')
    # def _compute_related_contacts(self):
    #     for lead in self:
    #         if lead.partner_id:
    #             lead.related_contact_ids = lead.partner_id.child_ids
    #         else:
    #             lead.related_contact_ids = False

class CrmAssetRequirement(models.Model):
    _name = 'crm.asset.requirement'
    _description = 'CRM Asset Requirement'

    lead_id = fields.Many2one('crm.lead', string='Crm Lead')
    sr_no = fields.Integer(string='Sr. No')
    rating = fields.Many2one('rating.master', string='Rating/KVA')
    no_of_phase = fields.Many2one('phase.master', string='Phase')
    voltage = fields.Many2one('voltage.master', string='Voltage')
    qty = fields.Integer(string='QTY')
    recurring = fields.Selection([
        ('fixed', 'Fixed'),
        ('forever', 'Forever'),
    ], string='Recurring')
    rental_start_date = fields.Date(string='Rental Start Date')
    rental_end_date = fields.Date(string='Rental End Date')
    description = fields.Text(string='Description')


class CrmAssetScopeOfWork(models.Model):
    _name = 'crm.asset.scope.of.work'
    _description = 'Scope of Work Line'
    _order = 'sr_no'

    lead_id = fields.Many2one('crm.lead', string='Crm Lead')
    sr_no = fields.Integer(string='Sr. No')
    product_id = fields.Many2one(
        'product.product',
        string='Product'
    )
    scope = fields.Selection([
        ('ptpl', 'PTPL'),
        ('client', 'Client'),
        ('vendor', 'Vendor'),
    ], string='Scope')
    description = fields.Text(string='Description')
    qty = fields.Integer(string='Quantity')
    unit_price = fields.Float(string='Unit Price')
    uom_id = fields.Many2one(
        'uom.uom',
        string='Unit of Measurement'
    )
    special_requirement = fields.Text(string='Special Requirement')


class LeadDocumentLine(models.Model):
    _name = 'lead.document.line'
    _description = 'Lead Document Line'

    lead_id = fields.Many2one('crm.lead', string='Lead Reference')
    sr_no = fields.Integer(string='Sr No')
    document_type = fields.Selection([
        ('invoice', 'Invoice'),
        ('po', 'Purchase Order'),
        ('agreement', 'Agreement'),
        ('other', 'Other'),
    ], string='Type of Document')


class LeadLogisticsLine(models.Model):
    _name = 'lead.logistics.line'
    _description = 'Lead Logistics Line'

    lead_id = fields.Many2one('crm.lead', string='Lead Reference')
    delivery_date = fields.Date(string='Delivery Expected')
    loading_address = fields.Char(string='Loading Address')
    unloading_address = fields.Char(string='Unloading Address')
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle Requirement')
    description = fields.Text(string='Description')
