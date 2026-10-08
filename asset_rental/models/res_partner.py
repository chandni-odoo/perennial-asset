# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    purchase_rental_order_count = fields.Integer(
        string='Rental Orders',
        compute='_compute_purchase_rental_order_count'
    )

    def _compute_purchase_rental_order_count(self):
        RentalOrder = self.env['purchase.rental.order']
        for partner in self:
            partner.purchase_rental_order_count = RentalOrder.search_count([
                ('partner_id', '=', partner.id)
            ])

    def action_open_purchase_rental_orders(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Rental Orders',
            'res_model': 'purchase.rental.order',
            'view_mode': 'list,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id}
        }
