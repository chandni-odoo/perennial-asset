# -*- coding: utf-8 -*-
from odoo import models, fields, api


class Picking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        res = super().button_validate()
        asset_model = self.env['asset.asset']
        created_serials = set()
        acccount_asset_model = self.env['account.asset']
        for picking in self.filtered(lambda p: p.state == 'done'):
            for move in picking.move_ids_without_package:
                for move_line in move.move_line_ids:
                    product = move_line.product_id
                    template = product.product_tmpl_id
                    lot = move_line.lot_id
                    stockmove_line = move_line

                    purchase_order = self.env['purchase.order'].search([('name', '=', picking.origin)], limit=1)

                    if product.is_asset and purchase_order and product.asset_level == 'primary' and lot and lot.name not in created_serials:
                        # Match product with purchase order line to get unit price
                        po_line = purchase_order.order_line.filtered(lambda l: l.product_id == product)
                        original_value = po_line.price_unit if po_line else 0.0
                        # purchase_order = self.env['purchase.order'].search([('name', '=', picking.origin)], limit=1)
                        # if product.is_asset and purchase_order and product.asset_level == 'primary' and lot and lot.name not in created_serials:
                        asset_vals = {
                            'name': product.name,
                            'category_id': template.asset_type_id.category_id.id,
                            'make_id': template.asset_type_id.make_id.id or '',
                            'rating': template.asset_type_id.rating.id or '',
                            'unit': product.uom_id.name,
                            'voltage': template.asset_type_id.voltage.id or 0,
                            'no_of_phase': template.asset_type_id.no_of_phase.id or 0,
                            'type_id': template.asset_type_id.type_id.id,
                            'hz_id': template.asset_type_id.hz_id.id,
                            'owner_id': template.asset_type_id.owner_id.id,
                            'model_name': template.asset_type_id.name,
                            'purchase_type': 'purchase',
                            'serial_number': lot.name,
                            'manufacturing_date': fields.Date.context_today(self),
                            'purchase_id': purchase_order.id,
                            'purchase_date': purchase_order.date_approve,
                            'rerental_vendor_id': purchase_order.partner_id.id,
                        }
                        asset_model.create(asset_vals)
                        accounting_asset_primary = {
                            'name': product.name,
                            'stock_move_line_id': stockmove_line.id,
                            'acquisition_date': fields.Date.context_today(self),
                            'original_value': original_value,
                        }

                        acccount_asset_model.create(accounting_asset_primary)
                        created_serials.add(lot.name)
                    if product.is_asset and purchase_order and product.asset_level == 'secondary' and lot and lot.name not in created_serials:
                        po_line = purchase_order.order_line.filtered(lambda l: l.product_id == product)
                        original_value = po_line.price_unit if po_line else 0.0
                        accounting_asset_secondary = {
                            'name': product.name,
                            'stock_move_line_id': stockmove_line.id,
                            'acquisition_date': fields.Date.context_today(self),
                            'original_value': original_value,
                        }
                        acccount_asset_model.create(accounting_asset_secondary)
        return res
