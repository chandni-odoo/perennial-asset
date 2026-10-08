# -*- coding: utf-8 -*-
from email.policy import default
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class MaterialRequisition(models.Model):
    _name = 'material.requisition'
    _description = 'Material Requisition'

    name = fields.Char(string='Order Number', required=True, copy=False, readonly=True, default='New')
    purpose = fields.Text(string="Purpose")

    request_raised_by_id = fields.Many2one('hr.employee', string="Request Raised By")
    department_id_by = fields.Many2one('hr.department', string='Department')
    job_id_by = fields.Many2one('hr.job', 'Job Position')
    reporting_manager_id = fields.Many2one('res.users', string='Reporting Manager')
    destination_location_id = fields.Many2one('stock.location', string='Destination Location')

    request_raised_for_id = fields.Many2one('hr.employee', string='Request Raised For')
    department_id_for = fields.Many2one('hr.department', string='Department')
    job_id_for = fields.Many2one('hr.job', 'Job Position')
    indent_date = fields.Datetime(string='Indent Date')
    required_date = fields.Datetime(string='Required Date')
    requirement = fields.Selection([
        ('normal', 'Normal'),
        ('urgent', 'Urgent'),
    ], default='normal', string='Requirement')

    line_ids = fields.One2many('material.requisition.line', 'material_id', string='Requested Products')
    notes = fields.Text(string="Additional Information")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('store_verify', 'Verified By Store Team'),
        ('waiting_for_approval','Waiting for Approval'),
        # ('first_approval', '1st Approval'),
        # ('second_approval', '2nd Approval'),
        # ('third_approval', '3rd Approval'),
        ('approved', 'Approved'),
        ('reject', 'Reject'),
        ('rfq_created', 'RFQ Created'),
        ('delivery_created', 'Delivered')],
        default='draft', string='Status')

    store_verified_remark = fields.Text(string='Store Verified Remark')

    approval_remark = fields.Text(string='Approval Remark')
    purchase_order_id = fields.Many2one('purchase.order', string="Purchase")
    stock_picking_id = fields.Many2one('stock.picking', string="Stock")

    ribbon_state_html = fields.Html(string="Ribbon State", compute="_compute_ribbon_state_html", sanitize=False)

    def _compute_ribbon_state_html(self):
        for rec in self:
            color_map = {
                'first_approval': 'badge-warning',
                'second_approval': 'badge-delivery_createdorange',
                'third_level': 'badge-primary',
                'third_approval': 'badge-success',
                'rejected': 'badge-danger',
                'rfq_created': 'badge-secondary',
                'delivery_created': 'badge-info',
            }
            state = rec.state or 'draft'
            label = dict(rec._fields['state']._description_selection(rec.env)).get(state, 'Unknown')
            badge_class = color_map.get(state, 'badge-secondary')
            rec.ribbon_state_html = f'<span class="badge {badge_class}">{label}</span>'

    company_id = fields.Many2one(
        comodel_name='res.company',
        required=True, index=True,
        default=lambda self: self.env.company)

    @api.onchange('request_raised_by_id')
    def request_raised_by(self):
        for rec in self:
            if rec.request_raised_by_id:
                rec.department_id_by = rec.request_raised_by_id.department_id.id
                rec.job_id_by = rec.request_raised_by_id.job_id.id

    @api.onchange('request_raised_for_id')
    def request_raised_for(self):
        for rec in self:
            if rec.request_raised_for_id:
                rec.department_id_for = rec.request_raised_for_id.department_id.id
                rec.job_id_for = rec.request_raised_for_id.job_id.id

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            fiscal_year = self._get_fiscal_year()
            sequence = self.env['ir.sequence'].next_by_code('material.requisition') or '00001'
            vals['name'] = f'MR/{fiscal_year}/{sequence}'
        return super(MaterialRequisition, self).create(vals)

    def _get_fiscal_year(self):
        today = fields.Date.context_today(self)
        year = today.year
        if today.month >= 4:
            return f'{str(year)[-2:]}-{str(year + 1)[-2:]}'
        else:
            return f'{str(year - 1)[-2:]}-{str(year)[-2:]}'

    def open_store_remark_wizard(self):
        if not self.approval_type:
            raise UserError("Material Approval is required for Verified Store!")
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'store.remark.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_requisition_id':self.id,'default_store_verified_remark': self.store_verified_remark},
        }

    def button_submit(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'approval.remark.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_approval_remark': self.approval_remark
            }
        }

    def action_view_purchase_orders(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Purchase Orders',
            'view_mode': 'list,form',
            'res_model': 'purchase.order',
            'domain': [('id', '=', self.purchase_order_id.id)],
            'context': {'create': False}
        }

    def action_view_picking(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Stock Picking',
            'view_mode': 'list,form',
            'res_model': 'stock.picking',
            'domain': [('id', '=', self.stock_picking_id.id)],
            'context': {'create': False}
        }


    def button_approve_1(self):
        self.state = 'second_approval'

    def button_approve_2(self):
        self.state = 'third_approval'

    def button_approve_3(self):
        self.state = 'approved'

    def button_delivery_created(self):
        StockPicking = self.env['stock.picking']
        StockMove = self.env['stock.move']

        picking_type = self.env.ref('stock.picking_type_out')
        picking_vals = {
            'picking_type_id': picking_type.id,
            'location_id': picking_type.default_location_src_id.id,
            'location_dest_id': self.destination_location_id.id,
            'origin': self.name,
        }
        picking = StockPicking.create(picking_vals)

        for line in self.line_ids:
            if line.product_qty <= 0:
                raise UserError("Quantity must be greater than 0 for all lines.")
            StockMove.create({
                'name': line.product_id.name,
                'product_id': line.product_id.id,
                'product_uom_qty': line.product_qty,
                'product_uom': line.product_id.uom_po_id.id,
                'location_id': self.destination_location_id.id,
                'location_dest_id': self.destination_location_id.id,
                'picking_id': picking.id,
            })

        picking.action_confirm()
        self.state = 'delivery_created'
        self.stock_picking_id = picking.id
        return {
            'name': 'Delivery Order',
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'view_mode': 'form',
            'res_id': picking.id,
        }

    def button_reject(self):
        for rec in self:
            rec.state = 'reject'

    def send_email_notification(self):
        mail_template = self.env.ref('material_requisition.email_template_purchase_order_notification')
        mail_template.email_to = self.request_raised_by_id.work_email
        mail_template.send_mail(self.id, force_send=True)

    def action_approve(self):
        # Check if current user is one of the approvers
        approver_line = self.requisition_history_ids.filtered(lambda r: r.user_id.id == self.env.uid)

        if not approver_line:
            raise UserError("You are not authorized to approve this request.")

        # Update the approval status for that user's line
        for line in approver_line:
            if line.status == 'approve':
                raise UserError("You have already approved this request.")

            line.write({
                'status': 'approve',
                'date_done': fields.Datetime.now(),
            })

        # Check if all approvals are done
        self._check_all_approved()

    def _check_all_approved(self):
        if all(line.status == 'approve' for line in self.requisition_history_ids):
            self.state = 'approved'

    can_user_approve = fields.Boolean(
        string='Can Current User Approve?',
        compute='_compute_can_user_approve',
        store=True
    )

    @api.depends('requisition_history_ids')
    def _compute_can_user_approve(self):
        for rec in self:
            for line in rec.requisition_history_ids:
                if line.user_id.id == self.env.uid and line.status == 'approve':
                    rec.can_user_approve = True


    # Approve Tab
    approval_type = fields.Many2one('material.request.approver', string='Material Approvals')
    no_of_approvals = fields.Integer(string='No. of Approvals')

    requisition_history_ids = fields.One2many('requisition.approval.history', 'requisition_id', string="Approval History", readonly=True)
    first_approver_id = fields.Many2one('res.users', string='First Approval')
    second_approver_id = fields.Many2one('res.users', string='Second Approval')
    third_approver_id = fields.Many2one('res.users', string='Third Approval')
    fourth_approver_id = fields.Many2one('res.users', string='Fourth Approval')
    fifth_approver_id = fields.Many2one('res.users', string='Fifth Approval')

    @api.onchange('approval_type')
    def onchange_approvers(self):
        for rec in self:
            if rec.approval_type:
                rec.no_of_approvals = rec.approval_type.no_of_approvals


class MrCustomLine(models.Model):
    _name = 'material.requisition.line'
    _description = 'Material Requisition Line'

    material_id = fields.Many2one('material.requisition', string='Material Requisition', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    product_qty = fields.Float(string='Quantity Required', required=True, default=1.0)
    product_uom_id = fields.Many2one('uom.uom', string='Unit of Measure', required=True)
    on_hand_qty = fields.Float(string='On-Hand Quantity', compute='_compute_on_hand_qty', store=True)
    short_close = fields.Boolean(string='Short Close')

    @api.depends('product_id')
    def _compute_on_hand_qty(self):
        for line in self:
            if line.product_id:
                location = line.material_id.destination_location_id.id if line.material_id.destination_location_id else False
                line.on_hand_qty = line.product_id.with_context(location=location).qty_available
            else:
                line.on_hand_qty = 0.0


class RequisitionApprovalsHistory(models.Model):
    _name = "requisition.approval.history"
    _description = "Approval History"

    requisition_id = fields.Many2one('material.requisition', string="Requisition")
    user_id = fields.Many2one('res.users', string="Approver")
    status = fields.Selection([
        ('pending', 'Pending'),
        ('approve', 'Approved'),
        ('reject', 'Rejected')], default='pending', copy=False, string="Approval Status")
    date_done = fields.Datetime(string="Approval Date")
