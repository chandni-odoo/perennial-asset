# -*- coding: utf-8 -*-
from odoo import models, fields, api


class MaterialApprovalRemarkWizard(models.TransientModel):
    _name = 'approval.remark.wizard'
    _description = 'Approval Remark Wizard'

    enable_default_remark = fields.Boolean(string='Enable Default Remark')
    approval_remark = fields.Text(string="Remark")

    @api.onchange('enable_default_remark')
    def _onchange_default_remark(self):
        if self.enable_default_remark:
            self.approval_remark = "Requisition Approval got confirmed without Remarks"

    def submit_remark(self):
        today = fields.Date.context_today(self).strftime('%d/%m/%Y')
        user = self.env.user.name
        requisition = self.env['material.requisition'].browse(self.env.context.get('active_id'))

        new_remark = f"[{user}][{today}] - {self.approval_remark or 'No Remarks'}"
        if requisition.approval_remark:
            requisition.approval_remark += '\n' + new_remark
        else:
            requisition.approval_remark = new_remark

        requisition.state = 'waiting_for_approval'
