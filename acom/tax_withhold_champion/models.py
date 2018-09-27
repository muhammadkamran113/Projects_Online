from odoo import models, fields, api
import xlsxwriter

class TaxWithold(models.Model):
	_name = 'tax.withold'
	_rec_name = 'ref_no'

	supplier       = fields.Char(string="Supplier" )
	date           = fields.Date(string="Date")
	amount         = fields.Integer(string="Amount")
	tax            = fields.Float(string="Tax Withheld")
	tax_name       = fields.Many2one('account.tax',string="Tax Name")
	ref_no     	   = fields.Char(string="Refrence No.")
	paid		   = fields.Boolean(string="Paid")
	challan_no     = fields.Char(string="Challan No.")



	@api.multi
	def epay(self):
		pass

class TaxWitholdWizard(models.Model):
	_name = "tax.withold.wizard"

	paid		   = fields.Boolean(string="Paid")
	challan_no     = fields.Char(string="Challan No.", required = True)

	@api.multi
	def punch(self):
		active_class = self.env['tax.withold'].browse(self._context.get('active_ids'))
		if active_class:
			print "Active"
			for x in active_class:
				x.challan_no = self.challan_no ; x.paid = self.paid

class epayWizard(models.Model):
	_name = "epay.wizard"

	challan_no     = fields.Char(string="Challan No.", required = True)

	@api.multi
	def get_epay(self):
		# active_class = self.env['tax.withold'].browse(self._context.get('active_id'))
		active_class 	= self.env['tax.withold'].search([('challan_no','=',self.challan_no)])

		if active_class:

			with xlsxwriter.Workbook("/home/odoo/Desktop/ePayment_xlsx_Report.xlsx") as workbook:
						
				main_heading = workbook.add_format({
					"bold": 1,
					"align": 'center',
					"valign": 'vcenter',
					"font_color":'black',
					"bg_color": '999999'
					})

				main_data = workbook.add_format({
					"align": 'center',
					"valign": 'vcenter'

					})

				worksheet = workbook.add_worksheet('Sheet1')

				worksheet.set_column('A:J', 20)

				worksheet.write('A1', 'Payment Section',main_heading)
				worksheet.write('B1', 'TaxPayer_NTN',main_heading)
				worksheet.write('C1', 'TaxPayer_CNIC',main_heading)
				worksheet.write('D1', 'TaxPayer_Name',main_heading)
				worksheet.write('E1', 'TaxPayer_City',main_heading)
				worksheet.write('F1', 'TaxPayer_Address',main_heading)
				worksheet.write('G1', 'TaxPayer_Status',main_heading)
				worksheet.write('H1', 'TaxPayer_Business_Name',main_heading)
				worksheet.write('I1', 'Taxable_Amount',main_heading)
				worksheet.write('J1', 'Tax_Amount',main_heading)

				row = 1
				col = 0

				for x in active_class:
					if self.challan_no == x.challan_no:
						z 	= self.env['customer.payment.bcube'].search([('number','=',x.ref_no)])
						worksheet.write_string (row, col,str(1),main_data)
						worksheet.write_string (row, col+1,z.partner_id.cp_ntn,main_data)
						worksheet.write_string (row, col+2,z.partner_id.cp_cnic,main_data)
						worksheet.write_string (row, col+3,z.partner_id.name,main_data)
						worksheet.write_string (row, col+4,z.partner_id.city,main_data)
						worksheet.write_string (row, col+5,z.partner_id.street + z.partner_id.street2,main_data)
						worksheet.write_string (row, col+6,"INDIVIDUAL",main_data)
						worksheet.write_string (row, col+7,str(z.partner_id.function),main_data)
						worksheet.write_string (row, col+8,str(x.amount),main_data)
						worksheet.write_string (row, col+9,str(x.tax),main_data)
					row +=1



				in_row = 1
				in_col = 0

				worksheet = workbook.add_worksheet("PaymentSections")

				worksheet.set_column('A:A', 15)
				worksheet.set_column('B:B', 30)
				worksheet.set_column('C:C', 50)
				worksheet.set_column('D:D', 10)

				worksheet.write('A1', 'Section',main_heading)
				worksheet.write('B1', 'Tax Payment Nature',main_heading)
				worksheet.write('C1', 'Tax Payment Section',main_heading)
				worksheet.write('D1', 'Code',main_heading)


				worksheet.write_string (in_row, in_col,str(1),main_data)
				worksheet.write_string (in_row, in_col+1,str(1),main_data)
				worksheet.write_string (in_row, in_col+2,str(1),main_data)
				worksheet.write_string (in_row, in_col+3,str(1),main_data)


