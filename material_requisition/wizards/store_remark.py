# -*- coding: utf-8 -*-
from odoo import models, fields, api


class StoreRemarkWizard(models.TransientModel):
    _name = 'store.remark.wizard'
    _description = 'Store Verified Remark Wizard'

    requisition_id = fields.Many2one('material.requisition', string='Requisition', required=True)
    store_verified_remark = fields.Text(string="Store Verified Remark")

    def submit_remark(self):
        active_id = self.env.context.get('active_id')
        if active_id:
            requisition = self.env['material.requisition'].browse(active_id)
            requisition.store_verified_remark = self.store_verified_remark
            requisition.state = 'store_verify'

            # Clear previous history
            requisition.requisition_history_ids.unlink()

            if requisition.approval_type.approver_line_id:
                # Create approval history
                for line in requisition.approval_type.approver_line_id:
                    self.env['requisition.approval.history'].create({
                        'requisition_id': requisition.id,
                        'user_id': line.user_id.id,
                        'status': 'pending',
                    })
