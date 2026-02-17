# -*- coding: utf-8 -*-
#############################################################################
from num2words import num2words

#    Alhodood Technologies.
#
#    Copyright (C) 2024-TODAY Alhodood Technologies(<https://www.alhodood.com>)
#    Author: Alhodood Technologies(<https://www.alhodood.com>)
#
#    You can modify it under the terms of the GNU Affero General Public License
#    (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License (AGPL v3) for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from odoo import models, fields, api,_
from odoo.exceptions import UserError


class PdcPaymentReceived(models.Model):
    _inherit = 'pdc.payment.received'

    property_type = fields.Selection([
        ('sale', 'Sales'),
    ],
        string="Property Type",
    )

    property_project_id = fields.Many2one(
        'property.project',
        string="Sale Project",
        tracking=True
    )

    property_unit_id = fields.Many2one(
        'property.unit',
        string="Sale Unit",
    )

    spa_id = fields.Many2one(
        comodel_name='spa.book',
        string="Spa"
    )


    def action_print_pdc_list(self):
        customers = self.mapped('customer_id')

        # if more than one unique customer → raise warning
        if len(customers) > 1:
            raise UserError(
                "You can print the PDC list only for the same customer."
            )
        return self.env.ref(
            'property_sales.action_report_pdc'
        ).report_action(self)

    @api.model
    def amount_to_words(self, amount, currency_name=''):
        """
        Convert a number to words with currency, capitalize each word.
        Example: 10500, 'AED' => 'AED Ten Thousand Five Hundred Zero Only'
        """
        if not amount:
            return ''
        # Convert number to words
        words = num2words(amount, to='currency', lang='en')
        # Remove euro/cents words if present
        words = words.replace('euro', '').replace('cents', '').replace('and', ',').strip()
        # Capitalize first letter of each word
        words = ' '.join(word.capitalize() for word in words.replace('-', ' ').split())
        # Add currency
        if currency_name:
            return f"{currency_name} {words} Only"
        return f"{words} Only"

    def action_draft_to_receive(self):
        if self.property_type == 'sale':
            if self.enable_accounting_entry:
                if self.property_project_id and self.property_unit_id:
                    pdc_journal_id = self.env['account.journal'].search(
                        [('is_pdc', '=', True)], limit=1)
                    if not pdc_journal_id:
                        raise UserError(
                            _('Please Configure the PDC Journal !!'))
                    if not self.customer_id.property_account_receivable_id:
                        raise UserError(
                            _('Please Configure Customer Receivable Account !!'))
                    debit_acc_id = pdc_journal_id.credit_account_id
                    credit_acc_id = self.customer_id.property_account_receivable_id
                    journal_entry_lines = [
                        (0, 0, {
                            'debit': self.amount,
                            'credit': 0.0,
                            'account_id': debit_acc_id.id,
                        }),
                        (0, 0, {
                            'debit': 0.0,
                            'credit': self.amount,
                            'account_id': credit_acc_id.id,
                        })
                    ]
                    journal_entry = self.env['account.move'].create({
                        'journal_id': pdc_journal_id.id,
                        'date': fields.Date.today(),
                        'line_ids': journal_entry_lines,
                        'ref': f"Journal Entry for PDC {self.property_project_id.name} - {self.property_unit_id.name}",
                        'move_type': 'entry',
                        'state': 'draft',
                        'property_type': 'sale',
                        'property_project_id': self.property_project_id.id,
                        'property_unit_id': self.property_unit_id.id,
                        'pdc_received_id': self.id,
                    })
                    self.journal_entry_id = journal_entry.id
                else:
                    raise UserError(
                        _('Please Configure Sale Property And Unit !!'))
        res = super(PdcPaymentReceived, self).action_draft_to_receive()
        return res

    def action_reject(self):
        res = super(PdcPaymentReceived, self).action_reject()
        return res

    def action_matured(self):
        if self.property_type == 'sale':
            if self.property_project_id and self.property_unit_id:
                payment_id = self.env['account.payment'].create({
                    'payment_type': 'inbound',
                    'partner_type': 'customer',
                    'partner_id': self.customer_id.id,
                    'amount': self.amount,
                    'memo': self.cheque_no,
                    'journal_id': self.deposited.id,
                    'property_project_id': self.property_project_id.id,
                    'property_unit_id': self.property_unit_id.id,
                    'pdc_received_id': self.id,
                    'property_type': 'sale',
                })
                self.payment_id = payment_id.id
            else:
                raise UserError(
                    _('Please Configure Sale Property And Unit !!'))
        res = super(PdcPaymentReceived, self).action_matured()
        return res

    def action_view_journal_entry(self):
        journal_ids = self.env['account.move'].sudo().search(
            [('pdc_received_id', '=', self.id)])
        if journal_ids:
            return {
                'name': 'Journals',
                'view_type': 'list',
                'view_mode': 'list,form',
                'res_model': 'account.move',
                'domain': [('id', '=', journal_ids.ids)],
                'type': 'ir.actions.act_window',
                'context': {
                    'create': False,
                    'delete': False,
                }
            }

    def action_view_payment_invoice(self):
        payments = self.env['account.payment'].sudo().search(
            [('pdc_received_id', '=', self.id)])
        if payments:
            return {
                'name': 'Payments',
                'view_type': 'list',
                'view_mode': 'list,form',
                'res_model': 'account.payment',
                'domain': [('id', '=', payments.ids)],
                'type': 'ir.actions.act_window',
                'context': {
                    'create': False,
                    'delete': False,
                }
            }

