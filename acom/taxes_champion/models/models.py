# -*- coding: utf-8 -*-
from constraint import *
from odoo import models, fields, api
import random

class taxes_champion(models.Model):
	_inherit = 'account.tax'

	type_tax_use = fields.Selection([ ('sale', 'Sales'), ('purchase', 'Purchases'), ('none', 'None'), ('payment', 'Payment'), ('receipt', 'Receipt'), ('salary', 'Salary'),])

	amount_type = fields.Selection([('group', 'Group of Taxes'), ('fixed', 'Fixed'), ('percent', 'Percentage of Price'), ('division', 'Percentage of Price Tax Included') ])

	cp_sales_type = fields.Many2one('sales.type.bcube','Sales Type')
	cp_sro_no = fields.Many2one('sro.schno.bcube','SRO No. /Schedule No')
	cp_item_sr_no = fields.Many2one('item.srno.bcube','Item Sr. No')
	cp_item_desc = fields.Many2one('item.desc.bcube','Description')
	fbr_tax_code = fields.Char(string="FBR Tax Code")
	enable_child_tax = fields.Boolean('Tax on Children')

class SalesTypeBcube(models.Model):
	_name = 'sales.type.bcube'
	name = fields.Char('Name')

class ItemSrnoBcube(models.Model):
	_name = 'item.srno.bcube'
	name = fields.Char('Name')

class SroSchnoBcube(models.Model):
	_name = 'sro.schno.bcube'
	name = fields.Char('Name')

class ItemDescBcube(models.Model):
	_name = 'item.desc.bcube'
	name = fields.Char('Name')

class OtherCostTree(models.Model):
	_name ="other.cost.tree"

	date = fields.Date(string="Date")
	expense_type = fields.Many2one('account.account',string="Expense Type")
	vendor = fields.Many2one('res.partner',string="Vendor Name")
	bank = fields.Many2one('account.journal', string="Bank")
	reference = fields.Char(string="Reference")
	amount = fields.Float(string="Amount")
	tree_link = fields.Many2one('account.invoice', string="Tree Link")

class AccountInvoiceBcube(models.Model):
	_inherit = 'account.invoice'

	date_invoice = fields.Date(string="Invoice Date", required=True, readonly=False, select=True, default=lambda self: fields.date.today())
	others_tree = fields.One2many('other.cost.tree','tree_link')

	@api.one
	def _compute_amount(self):
		res = super(AccountInvoiceBcube, self)._compute_amount()
		self.amount_tax = sum(line.amount for line in self.tax_line_ids)
		self.amount_total = self.amount_untaxed + self.amount_tax
		return res

	@api.multi
	def generate_lines(self):
		remaining = 0
		for x in self.import_tree:
			product_price = x.product_id.list_price
			product_quant = int(x.price_subtotal/product_price)
			counted_price = product_price * product_quant
			product_difference = x.price_subtotal - counted_price
			difference_percentage = int((product_difference * 100)/ x.price_subtotal)

			if product_difference != 0:

				if difference_percentage <= 10:
					product_increment = product_difference/product_quant
					product_price = x.product_id.list_price + product_increment
					counted_price = product_price * product_quant

					create_invoice_line = self.env['account.invoice.line'].create({
						'product_id': x.product_id.id,
						'name': x.descrip,
						'account_id': x.account.id,
						'quantity': product_quant,
						'price_unit': product_price,
						'amount_subtoal': counted_price,
						'invoice_id': self.id,
						
						})
					line_data = self.env['account.invoice.line'].search([('id','=',create_invoice_line.id)])
					for a in line_data:
						for z in x.line_taxes:
							a.bcube_taxes_id = [(4,z.id)]
						unit_price = a.price_unit -(a.price_unit * (a.discount/100) )
						a.bcube_amount_tax = self.invoice_line_ids.calculateTaxAmount(a.bcube_taxes_id,a.quantity,unit_price)

				else:
					problem = Problem()
					numberofproducts = 3
					limit = product_difference
					
					current_list = 'abcdefghijklmnopqrstuvwxyz'
					products = self.env['product.template'].search([('list_price','<',limit)])
					
					record_list = []
					for a in products:
						record_list.append(int(a.list_price))

					required_list = []
					for i in range(0, numberofproducts):
						required_list.append(current_list[i])
					required_var = ''.join(required_list)

					def fun(*required_list):
						amount = 0
						for line in record_list:
							amount += line
							if amount <=limit:
								return amount <= limit

					problem.addVariables(required_var, record_list)
					problem.addConstraint(fun, required_var)
					problem.addConstraint(ExactSumConstraint(limit))
					solutions = problem.getSolutions()

					if solutions:
						secure_random = random.SystemRandom()
						combination = (secure_random.choice(solutions))
						size = len(combination)
						last_prices = []
						for b in range(0,size):
							last_prices.append(combination.values()[b])

						last_products = []
						listed_product = []

						for price in last_prices:
							for prod in products:
								if int(prod.list_price) == price:
									listed_product.append(prod)
									
									for y in listed_product:
										lst_listed_product = y
									last_products.append(lst_listed_product)

						product_check = []
						for e in last_products:
							if e not in product_check:
								product_check.append(e)
								prod_quant = 0
								for y in last_products:
									if y == e:
										prod_quant = prod_quant + 1

								create_invoice_line = self.env['account.invoice.line'].create({
									'product_id': x.product_id.id,
									'name': e.name,
									'account_id': x.account.id,
									'quantity': prod_quant,
									'price_unit': e.list_price,
									'amount_subtoal': int(e.list_price * prod_quant),
									'invoice_id': self.id,
									
									})
								line_data = self.env['account.invoice.line'].search([('id','=',create_invoice_line.id)])
								for a in line_data:
									for z in x.line_taxes:
										a.bcube_taxes_id = [(4,z.id)]
									unit_price = a.price_unit -(a.price_unit * (a.discount/100) )
									a.bcube_amount_tax = self.invoice_line_ids.calculateTaxAmount(a.bcube_taxes_id,a.quantity,unit_price)

						create_invoice_line = self.env['account.invoice.line'].create({
							'product_id': x.product_id.id,
							'name': x.descrip,
							'account_id': x.account.id,
							'quantity': product_quant,
							'price_unit': product_price,
							'amount_subtoal': int(counted_price),
							'invoice_id': self.id,
							
							})

						line_data = self.env['account.invoice.line'].search([('id','=',create_invoice_line.id)])
						for a in line_data:
							for z in x.line_taxes:
								a.bcube_taxes_id = [(4,z.id)]
							unit_price = a.price_unit -(a.price_unit * (a.discount/100) )
							a.bcube_amount_tax = self.invoice_line_ids.calculateTaxAmount(a.bcube_taxes_id,a.quantity,unit_price)

					else:
						product_increment = product_difference/product_quant
						product_price = x.product_id.list_price + product_increment
						counted_price = product_price * product_quant

						create_invoice_line = self.env['account.invoice.line'].create({
							'product_id': x.product_id.id,
							'name': x.descrip,
							'account_id': x.account.id,
							'quantity': product_quant,
							'price_unit': product_price,
							'amount_subtoal': counted_price,
							'invoice_id': self.id,
							
							})
						line_data = self.env['account.invoice.line'].search([('id','=',create_invoice_line.id)])
						for a in line_data:
							for z in x.line_taxes:
								a.bcube_taxes_id = [(4,z.id)]
							unit_price = a.price_unit -(a.price_unit * (a.discount/100) )
							a.bcube_amount_tax = self.invoice_line_ids.calculateTaxAmount(a.bcube_taxes_id,a.quantity,unit_price)

			elif product_difference == 0:

				create_invoice_line = self.env['account.invoice.line'].create({
					'product_id': x.product_id.id,
					'name': x.descrip,
					'account_id': x.account.id,
					'quantity': product_quant,
					'price_unit': product_price,
					'amount_subtoal': counted_price,
					'invoice_id': self.id,
					
					})
				line_data = self.env['account.invoice.line'].search([('id','=',create_invoice_line.id)])
				for a in line_data:
					for z in x.line_taxes:
						a.bcube_taxes_id = [(4,z.id)]
					unit_price = a.price_unit -(a.price_unit * (a.discount/100) )
					a.bcube_amount_tax = self.invoice_line_ids.calculateTaxAmount(a.bcube_taxes_id,a.quantity,unit_price)

	@api.multi
	def validator(self):
		seq = self.env['ir.sequence'].search([('name','=','Vendor Bills')])
		seq.code = 'vendor.bills.seq'
		self.number = self.env['ir.sequence'].next_by_code('vendor.bills.seq')
		create_move = self.env['account.move'].create({
			'journal_id':self.journal_id.id,
			'date':self.date_invoice,
			'ref':self.number

		})

		create_move_line = self.env['account.move.line'].create({
			'account_id': self.account_id.id,
			'name': 'name',
			'move_id': create_move.id,
			'date_maturity': self.date_invoice,
			'partner_id': self.partner_id.id,
			'debit': self.amount_untaxed
		})

		create_move_line = self.env['account.move.line'].create({
			'account_id': self.partner_id.property_account_payable_id.id,
			'name': 'name2',
			'move_id': create_move.id,
			'date_maturity': self.date_invoice,
			'partner_id': self.partner_id.id,
			'credit': self.amount_untaxed
		})

		for x in self.tax_line_ids:

			create_move_line = self.env['account.move.line'].create({
				'account_id': x.account_id.id,
				'name': 'name',
				'move_id': create_move.id,
				'date_maturity': self.date_invoice,
				'partner_id': self.partner_id.id,
				'debit': x.amount
			})

			create_move_line = self.env['account.move.line'].create({
				'account_id': x.tax_id.counter_tax.id,
				'name': 'name2',
				'move_id': create_move.id,
				'date_maturity': self.date_invoice,
				'partner_id': self.partner_id.id,
				'credit': x.amount
			})

		return self.write({'state':'draft'})

	@api.onchange('invoice_line_ids')
	def _onchange_invoice_line_ids(self):
		res = super(AccountInvoiceBcube, self)._onchange_invoice_line_ids()
		self.tax_line_ids = 0
		records = []
		taxes_ids = []
		for taxes in self.invoice_line_ids:
			for tax in taxes.bcube_taxes_id:
				if tax.id not in taxes_ids:
					taxes_ids.append(tax.id)
					
					records.append({
						'name':tax.name,
						'account_id':taxes.account_id.id,
						'invoice_id':self.id,
						'tax_id':tax.id,
						'amount': 0,
						})
				
			self.tax_line_ids = records
		for taxes in self.invoice_line_ids:
			for tax in taxes.bcube_taxes_id:
				
				if self.type == 'in_invoice':
					unit_price = taxes.assessed -(taxes.assessed * (taxes.discount/100) )
				
				if self.type == 'out_invoice':
					unit_price = taxes.price_unit -(taxes.price_unit * (taxes.discount/100) )

				amount_tax = self.invoice_line_ids.calculateTaxAmount(tax,taxes.quantity,unit_price)
				if self.tax_line_ids:
					for line in self.tax_line_ids:
						if line.name == tax.name:
							line.amount = line.amount + amount_tax

		return res

class AccountMoveRemoveValidation(models.Model):
	_inherit = "account.move"


	@api.multi
	def assert_balanced(self):
		if not self.ids:
			return True
		prec = self.env['decimal.precision'].precision_get('Account')

		self._cr.execute("""\
			SELECT      move_id
			FROM        account_move_line
			WHERE       move_id in %s
			GROUP BY    move_id
			HAVING      abs(sum(debit) - sum(credit)) > %s
			""", (tuple(self.ids), 10 ** (-max(5, prec))))
		# if len(self._cr.fetchall()) != 0:
		#     raise UserError(_("Cannot create unbalanced journal entry."))
		return True

class AccountInvoiceLineBcube(models.Model):
	_inherit = 'account.invoice.line'

	bcube_taxes_id = fields.Many2many('account.tax',
		'account_invoice_line_tax', 'invoice_line_id', 'tax_id',
		string='Taxes', domain=[('type_tax_use','!=','none'), '|', ('active', '=', False), ('active', '=', True)], oldname='invoice_line_tax_id')
	bcube_amount_tax = fields.Float(string = "Amount Tax")

	assessed = fields.Float(string="Assessed")
	per_unit_cost = fields.Float(string="Per Unit Cost")
	tax_Amount = fields.Float(string="Tax Amount")

	line_taxes = fields.Many2many('account.tax',string="Taxes")

	amount_subtoal = fields.Float(string="Amount")


	@api.onchange('bcube_taxes_id','price_unit','quantity','discount','assessed')
	def onChBcubeTaxes(self):

		if self.invoice_id.type == 'out_invoice':
			unit_price = self.price_unit -(self.price_unit * (self.discount/100) )
		
		if self.invoice_id.type == 'in_invoice':
			unit_price = self.assessed -(self.assessed * (self.discount/100) )

		self.bcube_amount_tax = self.calculateTaxAmount(self.bcube_taxes_id, self.quantity, unit_price)


	@api.onchange('product_id')
	def getProductTaxes(self):
		all_taxes = []
		for x in self.invoice_id.partner_id.property_account_position_id.tax_ids:
			all_taxes.append((4,x.tax_dest_id.id))

		self.bcube_taxes_id = all_taxes
		self.discount = self.invoice_id.partner_id.discount
		
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

class DiscountAmount(models.Model):
	_inherit  = 'res.partner'
	discount = fields.Float(string="Discount%")

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

	@api.onchange('product_id')
	def onchange_product_id(self):
		self.unit_price = self.product_id.list_price
		self.quantity = 1
		self.descrip = self.product_id.name

	@api.onchange('quantity','unit_price')
	def onchange_quant(self):
		self.price_subtotal = self.quantity * self.unit_price

class ImportInvoice_lines(models.Model):
	_inherit = 'account.invoice'

	import_tree = fields.One2many('sales.invoice.tree','tree_link')

class AccountTaxAmount(models.Model):
	_inherit = 'account.tax'

	counter_tax = fields.Many2one('account.account',string="Counter Tax")