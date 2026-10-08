# -*- coding: utf-8 -*-

import logging
from collections import defaultdict
from dateutil.relativedelta import relativedelta
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta, date


_logger = logging.getLogger(__name__)


class PurchaseRentalOrder(models.Model):
    _name = 'purchase.rental.order'
    _description = 'Vendor Rental Agreement'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Rental Agreement', required=True, copy=False, readonly=True, default='New')
    company_id = fields.Many2one(
        comodel_name='res.company',
        required=True, index=True,
        default=lambda self: self.env.company)
    partner_id = fields.Many2one('res.partner', string="Vendor", required=True, domain=[('supplier_rank', '>', 0)])
    partner_invoice_id = fields.Many2one(
        comodel_name='res.partner',
        string="Invoice Address",
        compute='_compute_partner_invoice_id',
        store=True, readonly=False, required=True, precompute=True,
        check_company=True)
    partner_shipping_id = fields.Many2one(
        comodel_name='res.partner',
        string="Delivery Address",
        compute='_compute_partner_shipping_id',
        store=True, readonly=False, required=True, precompute=True,
        check_company=True)

    @api.depends('partner_id')
    def _compute_partner_invoice_id(self):
        for rental in self:
            rental.partner_invoice_id = rental.partner_id.address_get(['invoice'])['invoice'] if rental.partner_id else False

    @api.depends('partner_id')
    def _compute_partner_shipping_id(self):
        for rental in self:
            rental.partner_shipping_id = rental.partner_id.address_get(['delivery'])['delivery'] if rental.partner_id else False

    order_date = fields.Datetime(string="Order Date", default=lambda self: fields.Datetime.now())
    reference = fields.Char(string="Reference")
    close_date = fields.Date(string="Close Date")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed Rental'),
        ('close', 'Closed Rental')
    ], default='draft', tracking=True, string='Status')

    amount_untaxed = fields.Monetary(string='Untaxed Amount', compute='_compute_amount', store=True)
    amount_tax = fields.Monetary(string='Taxes', compute='_compute_amount', store=True)
    amount_total = fields.Monetary(string='Total', compute='_compute_amount', store=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)

    rental_line_ids = fields.One2many('purchase.rental.order.line', 'order_id', string="Rental Lines")
    purchase_order_ids = fields.One2many('purchase.order', 're_rental_order_id', string="Purchase Orders")
    purchase_order_id = fields.Many2one('purchase.order', string="Purchase Orders")
    pickings = fields.Many2many(
        'stock.picking',
        'rental_agreement_picking_rel',
        'rental_agreement_id',
        'picking_id',
        string='Stock Pickings'
    )
    total_pickings = fields.Integer(string="Receipts", compute="_compute_total_pickings", store=False)
    vendor_bill_ids = fields.Many2many('account.move', compute='_compute_vendor_bill_ids')
    vendor_bill_count = fields.Integer(string="Vendor Bill Count", compute='_compute_vendor_bill_ids')

    history_ids = fields.One2many(
        'purchase.rental.history',
        'order_id',
        string='Invoice History')

    @api.depends('purchase_order_ids.invoice_ids')
    def _compute_vendor_bill_ids(self):
        for rec in self:
            rec.vendor_bill_ids = rec.purchase_order_ids.mapped('invoice_ids')
            rec.vendor_bill_count = len(rec.purchase_order_ids.mapped('invoice_ids').ids)

    def _compute_total_pickings(self):
        for rec in self:
            pickings = rec.purchase_order_ids.mapped('picking_ids')
            rec.total_pickings = len(pickings)

    def action_confirm(self):
        if not self.rental_line_ids:
            raise ValidationError("No rental lines found. Please add rental lines before confirming.")
        self.action_create_purchase_order()
        self.create_rental_history_lines()
        self.write({'state': 'confirm'})

    def create_rental_history_lines(self):
        for order in self:
            for line in order.rental_line_ids:
                if not line.rental_intervals:
                    continue

                currency = order.currency_id
                quantity = line.product_qty
                price_unit = line.price_unit

                start_date = line.date_start
                rule_type = line.rental_intervals.recurring_rule_type
                interval = line.rental_intervals.recurring_interval
                delta = line._get_relativedelta(interval, rule_type)

                current_date = start_date
                cycles = 0
                max_cycles = line.duration_cycle_count if line.duration_cycle == 'limited' else 999

                while cycles < max_cycles:
                    # end_date = current_date + delta - timedelta(days=1)
                    end_date = current_date + delta
                    self.env['purchase.rental.history'].create({
                        'order_id': order.id,
                        'rental_line_id': line.id,
                        'interval_name': line.rental_intervals.name,
                        'start_date': current_date,
                        'end_date': end_date,
                        'amount': price_unit * quantity,
                        'currency_id': currency.id,
                    })

                    current_date += delta
                    cycles += 1

    def action_create_purchase_order(self):
        PurchaseOrder = self.env['purchase.order']
        for rec in self:
            order_lines = []
            for rental in rec.rental_line_ids:
                first_line = rec.rental_line_ids[:1]  # Get first line safely
                payment_date = first_line.date_end if first_line else False
                line_vals = {
                    'product_id': rental.product_id.id,
                    'product_qty': 1,
                    'price_unit': rental.price_unit,
                    'date_planned': fields.Date.today(),
                    'name': f'Re-rental: {rental.description or rental.product_id.name}',
                }

                # Only include re-rental fields if applicable
                if rental.product_id.rerent_ok:
                    line_vals.update({
                        'is_rerental': True,
                        'rental_line_id': rental.id,
                    })

                order_lines.append((0, 0, line_vals))

            if order_lines:
                po_vals = {
                    'partner_id': rec.partner_id.id,
                    'date_order': fields.Date.today(),
                    'origin': rec.name,
                    're_rental_order_id': rec.id,
                    'order_line': order_lines,
                    'payment_date': payment_date,
                }
                po = PurchaseOrder.create(po_vals)

                # Link PO to current record (Many2one or One2many as defined)
                rec.purchase_order_ids = [(4, po.id)]

                # Confirm the PO if needed
                po.button_confirm()

                # Optionally update pickings and state
                rec.pickings = rec.purchase_order_ids.mapped('picking_ids')
                rec.state = 'confirm'
        self.write({'purchase_order_id': po})


    # def action_validate_receipt(self):
    #     for rec in self:
    #         for po in rec.purchase_order_ids:
    #             # Get incoming pickings that are not done or canceled
    #             pickings = po.picking_ids.filtered(lambda p: p.state not in ['done', 'cancel'])
    #             for picking in pickings:
    #                 if picking.state == 'draft':
    #                     picking.action_confirm()
    #                 for move in picking.move_ids_without_package:
    #                     move.quantity_done = move.product_uom_qty
    #                 picking.button_validate()
    #                 rec.picking_id = picking.id
    #                 rec.picking_id.origin = rec.name
    #                 rec.state = 'received'

    def action_close(self):
        # Check all linked Purchase Orders are 'done' and fully received
        for rec in self:
            for po in rec.purchase_order_ids:
                if po.state != 'done':
                    raise UserError(f"Purchase Order {po.name} is not done.")

                for line in po.order_line:
                    if line.product_qty > line.qty_received:
                        raise UserError(f"Purchase Order {po.name} has lines not fully received.")

            # Check all related Vendor Bills are paid
            for bill in rec.vendor_bill_ids:
                if bill.payment_state != 'paid':
                    raise UserError(f"Vendor Bill {bill.name} is not fully paid.")

            self.close_date = fields.Date.today()
            self.write({'state': 'close'})

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('purchase.rental.order') or 'New'
        return super(PurchaseRentalOrder, self).create(vals)

    def action_view_purchase_orders(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Purchase Orders',
            'view_mode': 'list,form',
            'res_model': 'purchase.order',
            'domain': [('id', 'in', self.purchase_order_ids.ids)],
            'context': {'create': False}
        }

    def action_view_pickings(self):
        self.ensure_one()
        pickings = self.purchase_order_ids.mapped('picking_ids')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Vendor Receipts',
            'view_mode': 'list,form',
            'res_model': 'stock.picking',
            'domain': [('id', 'in', pickings.ids)],
            'context': {'create': False},
        }

    def action_open_vendor_bills(self):
        self.ensure_one()
        return {
            'name': 'Vendor Bills',
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form',
            'res_model': 'account.move',
            'domain': [('id', 'in', self.vendor_bill_ids.ids)],
            'context': {'default_move_type': 'in_invoice'},
        }

    @api.depends('rental_line_ids.price_subtotal')
    def _compute_amount(self):
        for order in self:
            order.amount_untaxed = sum(order.rental_line_ids.mapped('price_subtotal'))
            order.amount_tax = 0
            order.amount_total = order.amount_untaxed + order.amount_tax


class PurchaseRentalOrderLine(models.Model):
    _name = 'purchase.rental.order.line'
    _description = 'Rental Order Line'

    order_id = fields.Many2one('purchase.rental.order', string='Rental Order')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    product_category_id = fields.Many2one(related='product_id.categ_id', string='Product Category')
    description = fields.Char(string='Description')
    product_qty = fields.Float(string="Quantity")
    price_unit = fields.Float(string="Price Unit")
    tax_ids = fields.Many2one('account.tax', string="Tax")
    price_subtotal = fields.Float(string="Subtotal", compute='_compute_subtotal', store=True)
    rerent_ok = fields.Boolean(related='product_id.rerent_ok', store=True, readonly=False)

    date_start = fields.Date(string='Start Date', default=fields.Date.today)
    date_end = fields.Date(
        compute='_compute_date_end',
        string='End Date',
        store=True, readonly=False, precompute=True)
    duration_cycle = fields.Selection([
        ('limited', 'Fixed')
    ], string='Duration', default='limited')
    duration_cycle_count = fields.Integer(string="Duration Cycle Count")
    product_rental_intervals = fields.Many2many(related='product_id.rental_intervals', string="Product Rental Intervals", depends=['product_id'])
    rental_intervals = fields.Many2one(
        'rental.intervals',
        domain="[('id', 'in', product_rental_intervals)]",
        string='Interval',
    )
    product_type = fields.Selection(related='product_id.type', depends=['product_id'])
    recurring_next_date = fields.Date(string='Next Order Date', store=True)

    @api.constrains('product_id', 'rental_intervals')
    def _check_rental_intervals_required(self):
        for line in self:
            if line.product_id and line.product_id.rerent_ok and not line.rental_intervals:
                raise ValidationError("The 'Rental Intervals' field is required for re-rentable products.")

    @api.depends('date_start', 'rental_intervals', 'duration_cycle', 'duration_cycle_count')
    def _compute_date_end(self):
        for line in self:
            if line.date_start and line.duration_cycle == 'limited' and line.rental_intervals:
                recurring_interval = line.rental_intervals.recurring_interval
                recurring_rule_type = line.rental_intervals.recurring_rule_type
                periods = {'daily': 'days', 'weekly': 'weeks', 'monthly': 'months', 'semesterly': 'months', 'quarterly': 'months', 'yearly': 'years'}
                if recurring_rule_type == 'quarterly':
                    recurring_interval *= 3
                elif recurring_rule_type == 'semesterly':
                    recurring_interval *= 6
                line.date_end = fields.Date.from_string(line.date_start) + relativedelta(**{
                    periods[recurring_rule_type]: line.duration_cycle_count * recurring_interval})

    def _get_relativedelta(self, interval, rule_type):
        if rule_type == 'daily':
            return relativedelta(days=interval)
        elif rule_type == 'weekly':
            return relativedelta(weeks=interval)
        elif rule_type == 'monthly':
            return relativedelta(months=interval)
        elif rule_type == 'yearly':
            return relativedelta(years=interval)
        return relativedelta()

    @api.depends('price_unit', 'tax_ids')
    def _compute_subtotal(self):
        for line in self:
            tax_amount = 0.0
            if line.tax_ids:
                tax_amount = (line.price_unit * line.tax_ids.amount) / 100
            line.price_subtotal = line.price_unit + tax_amount


class PurchaseRentalHistory(models.Model):
    _name = 'purchase.rental.history'
    _description = 'Rental History'
    _order = 'date desc'

    order_id = fields.Many2one('purchase.rental.order', string='Rental Order')
    rental_line_id = fields.Many2one('purchase.rental.order.line', string="Rental Line", required=True, ondelete='cascade')
    product_id = fields.Many2one(related='rental_line_id.product_id', string="Product")
    interval_name = fields.Char(string="Interval")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    amount = fields.Monetary(string="Amount")
    currency_id = fields.Many2one('res.currency', string="Currency")

    #Invoice
    invoice_id = fields.Many2one('account.move', string="Invoice", domain=[('move_type', '=', 'in_invoice')])
    date = fields.Date(string="Invoice Date", related='invoice_id.invoice_date', store=True)
    amount = fields.Monetary(string="Amount", related='invoice_id.amount_total', store=True)
    currency_id = fields.Many2one('res.currency', related='invoice_id.currency_id', store=True)

    @api.model
    def generate_vendor_rental_invoices(self):
        today = fields.Date.today()

        # Step 1: Fetch rental history records that are due and not yet invoiced
        history_lines = self.search([
            ('invoice_id', '=', False),
            ('start_date', '<=', today),
        ])
        if not history_lines:
            return

        grouped_lines = defaultdict(list)
        for line in history_lines:
            purchase_order = line.order_id.purchase_order_id
            if not purchase_order:
                continue
            grouped_lines[purchase_order].append(line)

        # Step 2: Create bills
        for po, lines in grouped_lines.items():
            if not po.partner_id:
                raise UserError(_("Purchase Order %s has no vendor.") % po.name)

            move_vals = {
                'move_type': 'in_invoice',
                'partner_id': po.partner_id.id,
                'invoice_origin': po.name,
                'invoice_date': today,
                'invoice_line_ids': [],
            }

            invoice_lines = []
            for line in lines:
                rental_line = line.rental_line_id
                invoice_line_vals = (0, 0, {
                    'name': 'Rental Line',
                    'product_id': line.product_id.id,
                    'quantity': rental_line.product_qty or 1.0,
                    'price_unit': rental_line.price_unit or 0.0,
                    'account_id': line.product_id.property_account_expense_id.id or line.product_id.categ_id.property_account_expense_categ_id.id,
                })
                invoice_lines.append(invoice_line_vals)

            move_vals['invoice_line_ids'] = invoice_lines

            # Create the invoice
            invoice = self.env['account.move'].create(move_vals)

            # Link invoice to rental history lines
            rental_records = self.browse([line.id for line in lines])
            rental_records.write({'invoice_id': invoice.id})

            # Step 3: Set the quantity in PO picking and mark as done
            for po_line in po.order_line:
                picking = self.env['stock.picking'].search([
                    ('origin', '=', po.name),
                    ('state', 'in', ['draft', 'assigned']),
                ], limit=1)
                if picking:
                    for move_line in picking.move_line_ids:
                        if move_line.product_id == po_line.product_id:
                            move_line.qty_done = po_line.product_qty

                    picking.action_confirm()
                    picking.action_assign()
                    picking.button_validate()

            # Step 4: Call action_create_invoice on rental order
            rental_order = self.env['purchase.rental.order'].search([
                ('purchase_order_id', '=', po.id)
            ], limit=1)

            if rental_order:
                rental_order.purchase_order_id.action_create_invoice()
