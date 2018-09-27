# -*- coding: utf-8 -*-

from odoo import models, fields, api


# Class extending res.partner class
class CPCustomerFormExtention(models.Model):
    _inherit  = 'res.partner'
    cp_cnic = fields.Char(string="CNIC No")
    cp_ntn = fields.Char(string="National Tax No")
    cp_st_reg = fields.Char(string="ST Registration No")



# Class extending res.company class
class CPCompanyFormExtention(models.Model):
    _inherit  = 'res.company'
    cp_ntn = fields.Char(string="National Tax No")
    cp_st_reg = fields.Char(string="ST Registration No")