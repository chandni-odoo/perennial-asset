# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class MaterialRequestApprover(models.Model):
    _name = 'material.request.approver'
    _description = 'Material Request Approver Rules'

    name = fields.Char(string='Material Type', required=True)
    approval_type = fields.Selection([
        ('material', 'Material Request Approvers'),
    ], default='material', string='Approvals Type')
    no_of_approvals = fields.Integer(string='No. of Approvals', required=True)
    approver_line_id = fields.One2many('material.approval.lines', 'approver_id', string="Approver(s)")

    first_approver_id = fields.Many2one('res.users', string='First Approval')
    second_approver_id = fields.Many2one('res.users', string='Second Approval')
    third_approver_id = fields.Many2one('res.users', string='Third Approval')
    fourth_approver_id = fields.Many2one('res.users', string='Fourth Approval')
    fifth_approver_id = fields.Many2one('res.users', string='Fifth Approval')

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    @api.constrains('approver_line_id', 'no_of_approvals')
    def _check_approvals_limit(self):
        for record in self:
            if len(record.approver_line_id) > record.no_of_approvals:
                raise ValidationError(
                    f"Only {record.no_of_approvals} approvers allowed. You added {len(record.approver_line_id)}."
                )

    @api.constrains('approver_line_id')
    def _check_duplicate_user_id(self):
        for approval in self:
            for user in approval.approver_line_id.mapped("user_id"):
                line_ids = self.env['material.approval.lines'].search_count([('approver_id', '=', approval.id), ('user_id', '=', user.id)])
                if line_ids > 1:
                    raise ValidationError(("Duplicated approver not allow"))


class MaterialApprovalLines(models.Model):
    _name = "material.approval.lines"
    _description = 'material Approval Lines'

    approver_id = fields.Many2one('material.request.approver', string="Sale Request")
    user_id = fields.Many2one("res.users", string="Approver")
