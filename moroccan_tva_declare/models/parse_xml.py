# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import datetime
from reportlab.lib.validators import inherit
import base64
from lxml import etree
import time
import calendar
from datetime import date
from odoo.exceptions import UserError

class InvoiceLineTampon(models.Model):
    _name= "invoice.line.tampon"
    _order = 'num_ordre'

    declaration_id = fields.Many2one('tva.declaration.creation')

    num_ordre = fields.Char(string="Num d'Ordre")
    invoice_id = fields.Char(string="Num de Facture")
    date_invoice = fields.Char(string="Date de la Facture")
    name = fields.Char(string="Designation des Biens et Services")
    partner_id = fields.Char(string="Nom du Fournisseur")
    identifiant_fiscal = fields.Char(string="Identifiant Fiscal Fournisseur")
    ice_company = fields.Char(string="ICE")
    price_subtotal = fields.Char(string="Montant HT")
    x_taux = fields.Char(string="Taux")
    tva_amount = fields.Char(string="Montant TVA")
    ttc_amount = fields.Char(string="Montant TTC")
    mode_paiement = fields.Char(string="Mode de Paiement")
    date_paiement = fields.Char(string="Date de Paiement")
    declared = fields.Boolean('Déclarée')

class TVA_declaration_Creation(models.Model):
    _name= "tva.declaration.creation"

    identifiant_fiscal =  fields.Integer('Identifiant Fiscal', required=True)
    annee =  fields.Integer('Annee', required=True)
    periode_month =  fields.Selection([("1", '1'), ('2', '2'), ('3', '3'),
                                           ('4', '4'), ('5', '5'), ('6', '6'),
                                           ('7', '7'), ('8', '8'), ('9', '9'),
                                           ('10', '10'), ('11', '11'), ('12', '12')],'Periode')
    periode_trimestre =  fields.Selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4')],'Periode')
    regime =  fields.Selection([('1', 'Mensuel'), ('2', 'Trimestriel')], 'Regime', required=True, default='1')
    name =  fields.Char('Reference', required=True, placeholder="eg. Trimestre 1 2019")
    type =  fields.Selection([('encaissement', 'Encaissement'), ('debit', 'Debit')], 'Type', required=True, default='encaissement')
    start_date =  fields.Date('Date de Debut')
    end_date =  fields.Date('Date')
    tampon_invoices = fields.One2many('invoice.line.tampon', 'declaration_id')
    related_invoices = fields.Many2many('account.invoice.line', 'declaration_invoice_line_id','declaration_id','invoice_line_id')

    txt_file =  fields.Binary('Fichier EDI TVA')
    file_name = fields.Char('Nom du Fichier', size=64)

    declared = fields.Boolean('Déclaré', default=False)


    @api.multi
    @api.onchange('declared')
    def onchange_declared(self):
        print('trigered onchange_declared')
        #for declaration in self:
        for related_invoice in self.related_invoices:
            print('related invoice',related_invoice )
            related_invoice.write({'declared' : self.declared })

        for tampon_invoice in self.tampon_invoices:
            tampon_invoice.write({'declared' : self.declared })

    # this methode filters the needed invoices according to selected criterias
    # stores it in filtered invoices as buffering data

    def filtre_xml(self, context=None):
        for xml_file in self:
            invoice_obj = self.env['account.invoice']

            if xml_file.regime == '1' :
                last_day_of_month = calendar.monthrange(xml_file.annee,int(xml_file.periode_month))[1]

                xml_file.end_date = date(xml_file.annee, int(xml_file.periode_month), last_day_of_month)
                xml_file.start_date = date(xml_file.annee, int(xml_file.periode_month), 1)

            if xml_file.regime == '2' :
                last_day_of_trimestre = calendar.monthrange(xml_file.annee,int(xml_file.periode_trimestre)*3)[1]

                xml_file.end_date = date(xml_file.annee, int(xml_file.periode_trimestre)*3, last_day_of_trimestre)
                xml_file.start_date = date(xml_file.annee, int(xml_file.periode_trimestre)*3 - 2, 1)

            if xml_file.type == 'encaissement':
                selected_invoices = invoice_obj.search([('state','=','paid'),('type','in',('in_invoice','in_refund')),('date_paiement','>=',xml_file.start_date),('date_paiement','<=',xml_file.end_date)])

            if xml_file.type == 'debit':
                selected_invoices = invoice_obj.search([('state','in',('open','paid')),('type','in',('in_invoice','in_refund')),('date_invoice','>=',xml_file.start_date),('date_invoice','<=',xml_file.end_date)])
                print('selected_invoice',selected_invoices)

            xml_file.write({'tampon_invoices':[(5,0,{})]})
            xml_file.write({'related_invoices':[(5,0,{})]})
            for selected_invoice in selected_invoices:
                for selected_invoice_line in selected_invoice.invoice_line_ids :
                    if selected_invoice_line.to_declare:
                        xml_file.write({'related_invoices':[(4,selected_invoice_line.id,{})]})
                        xml_file.write({'tampon_invoices':[(0,0,{
                            'num_ordre' : selected_invoice_line.id,
                            'invoice_id' : selected_invoice.number,
                            'date_invoice' : selected_invoice_line.date_invoice,
                            'name' : selected_invoice_line.name,
                            'partner_id' : selected_invoice_line.partner_id.name,
                            'identifiant_fiscal' : selected_invoice_line.partner_id.identifiant_fiscal,
                            'ice_company' : selected_invoice_line.ice_company,
                            'price_subtotal' : selected_invoice_line.price_subtotal if selected_invoice.type == 'in_invoice' else -selected_invoice_line.price_subtotal,
                            'x_taux' : selected_invoice_line.x_taux,
                            'tva_amount' : selected_invoice_line.tva_amount if selected_invoice.type == 'in_invoice' else -selected_invoice_line.tva_amount,
                            'ttc_amount' : selected_invoice_line.ttc_amount if selected_invoice.type == 'in_invoice' else -selected_invoice_line.ttc_amount,
                            'mode_paiement' : selected_invoice_line.mode_paiement,
                            'date_paiement' : selected_invoice_line.date_paiement,
                        })]})


    # this function "generate_xml " is called from button click on view.xml
    # stores the encoded xml data into database column

    def generate_xml(self, context=None):
        for xml_file in self:
            DeclarationReleveDeduction = etree.Element("DeclarationReleveDeduction")

            identifiantFiscal = etree.SubElement(DeclarationReleveDeduction, "identifiantFiscal")
            identifiantFiscal.text = str(xml_file.identifiant_fiscal)

            annee = etree.SubElement(DeclarationReleveDeduction, "annee")
            annee.text = str(xml_file.annee)

            periode = etree.SubElement(DeclarationReleveDeduction, "periode")
            if xml_file.regime == '1' :
                periode.text = str(xml_file.periode_month)
            if xml_file.regime == '2' :
                periode.text = str(xml_file.periode_trimestre)

            regime = etree.SubElement(DeclarationReleveDeduction, "regime")
            regime.text = str(xml_file.regime)

            releveDeductions = etree.SubElement(DeclarationReleveDeduction, "releveDeductions")
            xmlstr = ""

            for invoice_line in xml_file.tampon_invoices:

                    rd = etree.SubElement(releveDeductions, "rd")

                    ord = etree.SubElement(rd, "ord")
                    ord.text = str(invoice_line.num_ordre)

                    num = etree.SubElement(rd, "num")
                    num.text = invoice_line.invoice_id

                    des = etree.SubElement(rd, "des")
                    des.text = invoice_line.name

                    mht = etree.SubElement(rd, "mht")
                    mht.text = str(invoice_line.price_subtotal)

                    tva = etree.SubElement(rd, "tva")
                    tva.text = str(invoice_line.tva_amount)

                    ttc = etree.SubElement(rd, "ttc")
                    ttc.text = str(invoice_line.ttc_amount)

                    refF = etree.SubElement(rd, "refF")

                    If = etree.SubElement(refF, "if")
                    If.text = str(invoice_line.identifiant_fiscal)

                    nom = etree.SubElement(refF, "nom")
                    nom.text = invoice_line.partner_id

                    ice = etree.SubElement(refF, "ice")
                    ice.text = str(invoice_line.ice_company)

                    tx = etree.SubElement(rd, "tx")
                    tx.text = str(invoice_line.x_taux)

                    mp = etree.SubElement(rd, "mp")

                    id = etree.SubElement(mp, "id")
                    id.text = str(invoice_line.mode_paiement)

                    dpai = etree.SubElement(rd, "dpai")
                    dpai.text = str(invoice_line.date_paiement)

                    dfac = etree.SubElement(rd, "dfac")
                    dfac.text = str(invoice_line.date_invoice)


                    xmlstr = etree.tostring(DeclarationReleveDeduction, pretty_print=True)

            if xmlstr :
                xml_file.write({'txt_file': base64.encodestring(xmlstr), 'file_name': xml_file.name + '.xml'})

            else :
                raise UserError( "Aucune ligne de facture n'a ete cree durant la periode choisie.")
