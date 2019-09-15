# -*- coding: utf-8 -*-

from odoo import fields, models, api
import datetime
import openerp.addons.decimal_precision as dp
from reportlab.lib.validators import inherit
from datetime import date


class res_partner(models.Model):
    _inherit = 'res.partner'
    _name = 'res.partner'

    identifiant_fiscal = fields.Char('Identifiant Fiscal')
    ice_company = fields.Char('ICE Société')

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    mode_paiement = fields.Selection([('1', 'Paiement Espèce'), ('2', 'Cheque'), ('3', 'Prelevement'),
                                           ('4', 'Virement'), ('5', 'Effet'), ('6', 'Compensation'),
                                           ('7', 'Autre')],'Mode de Paiement')
    date_paiement = fields.Date('Date de paiement')

    def action_invoice_open(self):
        # OVERRIDE
        # edits date_paiement with the validation date if the date is empty
        res = super(AccountInvoice, self).action_invoice_open()
        if not self.date_paiement:
            self.date_paiement = date.today()
        return res

class account_payment(models.Model):
    _inherit = 'account.payment'

    def action_validate_invoice_payment(self):
        # OVERRIDE
        # updates date_paiement with the payment date
        res = super(account_payment, self).action_validate_invoice_payment()
        self.invoice_ids[0].date_paiement = self.payment_date
        if self.journal_id.type == 'cash':
            self.invoice_ids[0].mode_paiement = '1'
        else: #bank
            self.invoice_ids[0].mode_paiement = '4'
        return res

class account_invoice_line(models.Model):
    _inherit = 'account.invoice.line'
    _order = "id"

    mode_paiement = fields.Selection([('1', 'Paiement Espèce'), ('2', 'Cheque'), ('3', 'Prelevement'),
                                           ('4', 'Virement'), ('5', 'Effet'), ('6', 'Compensation'),
                                           ('7', 'Autre')], related='invoice_id.mode_paiement', string='Mode de Paiement')

    date_paiement = fields.Date('Date de paiement' , related='invoice_id.date_paiement')
    date_invoice = fields.Date(string='Date Facture', readonly=True, index=True,
        help="Keep empty to use the current date", copy=False, related='invoice_id.date_invoice')

    identifiant_fiscal = fields.Char('Identifiant Fiscal', related='partner_id.identifiant_fiscal')
    ice_company = fields.Char('ICE Société', related='partner_id.ice_company')
    x_taux = fields.Float('Taux', compute='_compute_taux')
    tva_amount = fields.Float(string='Montant TVA', compute='_compute_tva_amount')
    ttc_amount = fields.Float(string='Montant TTC', compute='_compute_ttc_amount')
    to_declare = fields.Boolean(string='A declarer', default=True)
    declared = fields.Boolean('Deja Déclaré')

    @api.one
    @api.depends('invoice_line_tax_ids.amount')
    def _compute_taux(self):
        self.x_taux = sum(line.amount for line in self.invoice_line_tax_ids)

    @api.one
    @api.depends('x_taux', 'price_subtotal')
    def _compute_tva_amount(self):
        self.tva_amount = self.x_taux * self.price_subtotal / 100

    @api.one
    @api.depends('tva_amount', 'price_subtotal')
    def _compute_ttc_amount(self):
        self.ttc_amount = self.tva_amount + self.price_subtotal
