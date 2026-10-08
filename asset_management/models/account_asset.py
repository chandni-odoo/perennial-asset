# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AccountAsset(models.Model):
    _inherit = 'account.asset'

    stock_move_line_id = fields.Many2one('stock.move.line', string='Stock Move Line')
