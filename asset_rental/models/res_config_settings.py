# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    rent_before_delivery_reminder_days = fields.Integer(config_parameter="asset_rental.rent_before_delivery_reminder_days")
