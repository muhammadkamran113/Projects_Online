from odoo import models, fields, api

class PurchaseInvoiceExtention(models.Model):
	_inherit = 'account.invoice'

	@api.onchange('invoice_line_ids')
	def _onchange_invoice_line_ids(self):
		# res = super(PurchaseInvoiceExtention, self)._onchange_invoice_line_ids()
		print "xzzzzzzzzzzzzzzzzzz"
		self.tax_line_ids = 0
		records = []
		taxes_ids = []
		for taxes in self.invoice_line_ids:
			for tax in taxes.line_taxes:
				if tax.id not in taxes_ids:
					taxes_ids.append(tax.id)
					
					records.append({
						'name':tax.name,
						'account_id':taxes.account_id.id,
						'invoice_id':self.id,
						'tax_id':tax.id,
						'amount': 0,
						})
		# print records


			self.tax_line_ids = records

			print self.tax_line_ids
			print "ooooooooooooooooooooooooooooooooo"

		for taxes in self.invoice_line_ids:
			for tax in taxes.line_taxes:
				unit_price = taxes.price_unit -(taxes.price_unit * (taxes.discount/100) )
				amount_tax = self.invoice_line_ids.calculateTaxAmount(tax,taxes.quantity,unit_price)
				if self.tax_line_ids:
					print "?--------------------------?"
					for line in self.tax_line_ids:
						if line.name == tax.name:
							line.amount = line.amount + amount_tax
		return True

	def calculateTaxAmount(self, taxes, qty, price_unit):
		amount_tax = 0
		child_tax = 0
		child_tax_final=0
		for tax in taxes:
			if tax.enable_child_tax:
				if tax.children_tax_ids:
					child_tax = 0
					for childtax in tax.children_tax_ids:
						child_amount_tax = qty * price_unit * (childtax.amount/100) * (tax.amount/100)
		
						child_tax = child_tax + child_amount_tax 
					parent_tax = qty * price_unit * (tax.amount /100)
					child_tax_final = child_tax + parent_tax
					amount_tax += child_tax_final

			else:
				amount_tax += qty * price_unit * (tax.amount /100)
		
		return amount_tax


class PurchaseInvoiceTreeExtention(models.Model):
	_inherit = 'account.invoice.line'

	declared = fields.Float(string="Declared")
	per_unit_cost = fields.Float(string="Per Unit Cost")
	tax_Amount = fields.Float(string="Tax Amount")

	line_taxes = fields.Many2many('account.tax',string="Taxes")

	@api.onchange('price_subtotal','line_taxes')
	def tax_tree(self):
		if self.line_taxes:
			taxing = 1.0
			taxed = 1
			for x in self.line_taxes:
				taxing = taxing * (x.amount/100)

			taxed = taxing * self.price_subtotal
			self.tax_Amount = taxed

class SalesInvoiceExtension(models.Model):
	_name = 'sales.invoice.tree'
	_rec_name = 'product_id'

	product_id = fields.Many2one('product.product',string="Product")
	account = fields.Many2one('account.account',string="Account")
	tree_link = fields.Many2one('account.invoice')

	quantity = fields.Float(string="Quantity")
	unit_price = fields.Float(string="Unit Price")
	tax_amount = fields.Float(string="Amount Tax")
	price_subtotal = fields.Float(string="Amount")

	line_taxes = fields.Many2many('account.tax',string="Taxes")

	descrip = fields.Text(string="Description")

class ImportInvoice_lines(models.Model):
	_inherit = 'account.invoice'

	import_tree = fields.One2many('sales.invoice.tree','tree_link')