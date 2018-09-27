# -*- coding: utf-8 -*-

from odoo import models, fields, api

class taxes_chart_champion(models.Model):
    _inherit = 'account.tax'
    testing_tax_of_carts = fields.Many2one('res.partner')
    parent_id = fields.Many2one('account.tax')
    child_ids = fields.One2many('account.tax','parent_id', 'Child Accounts')
    parent_left = fields.Integer('Left Parent', index=1)
    parent_right = fields.Integer('Right Parent', index=1)
    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = 'name'
