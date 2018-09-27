#-*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 OpenERP SA (<http://openerp.com>). All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api

class SampleDevelopmentReport(models.AbstractModel):
    _name = 'report.sales_tax_report.sale_report'

    @api.model
    def render_html(self,docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('sales_tax_report.sale_report')
        active_wizard = self.env['sales.tax.report'].search([])

        emp_list = []
        for x in active_wizard:
            emp_list.append(x.id)
        emp_list = emp_list
        emp_list_max = max(emp_list) 

        record_wizard = self.env['sales.tax.report'].search([('id','=',emp_list_max)])
        record_wizard_del = self.env['sales.tax.report'].search([('id','!=',emp_list_max)])
        record_wizard_del.unlink()

        to = record_wizard.to
        form = record_wizard.form

        records = self.env['account.invoice'].search([('date_invoice', '>=', form),('date_invoice','<=',to)])

        out_tax = 0
        in_tax = 0
        for x in records:
            if x.type == 'out_invoice':
                for y in x.tax_line_ids:
                    if y.name == 'Sales Tax' or y.name == 'Additional Tax':
                        out_tax = out_tax + y.amount

        for x in records:
            if x.type == 'in_invoice':
                for y in x.tax_line_ids:
                    if y.name == 'Sales Tax' or y.name == 'Additional Tax':
                        in_tax = in_tax + y.amount

        opeing_balace = in_tax - out_tax

        vendor_sales = 0
        vendor_additional = 0

        for x in records:
            if x.type == 'in_invoice':
                for y in x.tax_line_ids:
                    if y.name == 'Sales Tax':
                        vendor_sales = vendor_sales + y.amount

        for x in records:
            if x.type == 'in_invoice':
                for y in x.tax_line_ids:
                    if y.name == 'Additional Tax':
                        vendor_additional = vendor_additional + y.amount

        customer_sales = 0

        for x in records:
            if x.type == 'out_invoice':
                for y in x.tax_line_ids:
                    if y.name == 'Sales Tax':
                        customer_sales = customer_sales + y.amount

        closing_balance = opeing_balace + (vendor_sales + vendor_additional) - customer_sales
        remaining_sales_value = (closing_balance*100)/17

        stock = self.env['stock.history'].search([])

        stock_value = 0
        products = self.env['product.template'].search([])

        for x in products:
            stock = self.env['stock.history'].search([('product_id.id','=',x.id)])
            current_prod_value = 0

            for y in stock:
                if y.product_id.id == x.id:
                    current_prod_value = current_prod_value + y.quantity

            if current_prod_value > 0:
                current_prod_value = current_prod_value * x.list_price
                stock_value = stock_value + current_prod_value

        stock_value = stock_value * (.17)
        difference = remaining_sales_value - stock_value

        docargs = {
            'doc_ids': docids,
            'doc_model': 'account.invoice',
            'data': data,
            'to': to,
            'form': form,
            'opeing_balace': opeing_balace,
            'vendor_sales': vendor_sales,
            'vendor_additional': vendor_additional,
            'customer_sales': customer_sales,
            'closing_balance': closing_balance,
            'remaining_sales_value': remaining_sales_value,
            'stock_value': stock_value,
            'difference': difference
            }

        return report_obj.render('sales_tax_report.sale_report', docargs)