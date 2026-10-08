# -*- coding: utf-8 -*-
from odoo import models, fields, api


class CreateRFQWizard(models.TransientModel):
    _name = 'create.rfq.wizard'
    _description = 'Create RFQ Wizard'

    requisition_id = fields.Many2one('material.requisition', string='Requisition', required=True)
    supplier_id = fields.Many2one('res.partner', string='Supplier', domain="[('supplier_rank', '>', 0)]", required=True)
    line_ids = fields.One2many('create.rfq.wizard.line', 'wizard_id', string='Order Lines')

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_id = self.env.context.get('active_id')
        requisition = self.env['material.requisition'].browse(active_id)
        res['requisition_id'] = requisition.id
        res['line_ids'] = [(0, 0, {
            'product_id': line.product_id.id,
            'product_uom_qty': line.product_qty,
            'product_uom': line.product_uom_id.id,
        }) for line in requisition.line_ids]
        return res

    def action_create_rfq(self):
        PurchaseOrder = self.env['purchase.order']
        for rec in self:
            order_lines = []
            for line in rec.line_ids:
                line_vals = {
                    'product_id': line.product_id.id,
                    'product_qty': 1,
                    'date_planned': fields.Date.today(),
                    'name': f'{line.product_id.name}'
                }
                order_lines.append((0, 0, line_vals))

                order_lines.update({
                    'mr_line_id': line.id,
                })

            if order_lines:
                po_vals = {
                    'partner_id': rec.supplier_id.id,
                    'date_order': fields.Date.today(),
                    'origin': rec.requisition_id.name,
                    'requisition_id': rec.requisition_id.id,
                    'order_line': order_lines,
                }
                po = PurchaseOrder.create(po_vals)
                po.button_confirm()
                rec.requisition_id.state = 'rfq_created'
                rec.requisition_id.purchase_order_id = po.id
                rec.requisition_id.send_email_notification()
        return {
            'type': 'ir.actions.act_window',
            'name': 'RFQ',
            'res_model': 'purchase.order',
            'res_id': po.id,
            'view_mode': 'form',
            'target': 'current'
        }


class CreateRFQWizardLine(models.TransientModel):
    _name = 'create.rfq.wizard.line'
    _description = 'Create RFQ Wizard Line'

    wizard_id = fields.Many2one(
        'create.rfq.wizard',
        string='Wizard',
        required=True,
        ondelete='cascade'
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True
    )
    product_uom_qty = fields.Float(
        string='Quantity',
        required=True,
        default=1.0
    )
    product_uom = fields.Many2one(
        'uom.uom',
        string='Unit of Measure',
        required=True
    )
    onhand_qty = fields.Float(
        string='On Hand Qty',
        related='product_id.qty_available',
        readonly=True
    )
