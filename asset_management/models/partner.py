# -*- coding: utf-8 -*-
from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    lead_id = fields.Many2one('crm.lead', string='CRM Lead')