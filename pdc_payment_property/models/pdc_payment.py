# -*- coding: utf-8 -*-
#############################################################################
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
from datetime import date, timedelta
from odoo.exceptions import UserError


class PdcPaymentSubmit(models.Model):
    _name = 'pdc.payment.submit'
    _description = 'PDC Submitted'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'cheque_no'

    cheque_no = fields.Char(string='Cheques Number', tracking=True)
    supplier_id = fields.Many2one('res.partner', string="Supplier", tracking=True)
    cheque_date = fields.Date(string="Cheque Date", tracking=True)
    amount = fields.Float(string="Amount", tracking=True)
    bank = fields.Char(string="Bank Name", tracking=True)
    status = fields.Selection(
        [('draft', 'Draft'),('received', 'Received'), ('matured', 'Matured'), ('rejected', 'Bounced'), ('hold', 'Hold'),
         ('returned', 'Returned')], tracking=True, default='received', copy=False)
    reject_reason = fields.Text(string='Reject Reason', tracking=True)
    hold_reason = fields.Text(string='Hold Reason', tracking=True)
    return_reason = fields.Text(string='Return Reason', tracking=True)
    is_delayed = fields.Boolean(string='Is Delayed', compute='_compute_is_delayed')
    company_id = fields.Many2one(
        'res.company',
        string="Company",
        tracking=True,
        default=lambda self: self.env.company,
        readonly=True
    )
    journal_entry_id = fields.Many2one(
        'account.move',
        string="Journal Entry"
    )

    @api.depends('cheque_date', 'status')
    def _compute_is_delayed(self):
        for record in self:
            if record and record.cheque_date:
                if record.status == 'received' and record.cheque_date < fields.Date.today():
                    record.is_delayed = True
                else:
                    record.is_delayed = False
            else:
                record.is_delayed = False

    def action_draft_to_receive(self):
        # pdc_ac_ids = self.env['pdc.account'].search([()], limit=1)
        # if not pdc_ac_ids:
        #     raise UserError(_('Please Configure the PDC Account'))
        # if not self.journal_id:
        #     raise UserError(_('Please Configure the Journal'))
        # self.acc_id = pdc_ac_ids.acc_id.id
        # self.p_acc_id = pdc_ac_ids.p_acc_id.id
        # journal_entry_lines = [
        #     (0, 0, {
        #         'debit': self.amount,
        #         'credit': 0.0,
        #         'account_id': self.acc_id.id,
        #         'partner_id': self.customer_id.id if self.customer_id else False,
        #     }),
        #     (0, 0, {
        #         'debit': 0.0,
        #         'credit': self.amount,
        #         'account_id': self.p_acc_id.id,
        #         'partner_id': self.customer_id.id if self.customer_id else False,
        #     })
        # ]
        #
        # journal_entry = self.env['account.move'].create({
        #     'journal_id': self.journal_id.id,
        #     'date': fields.Date.today(),
        #     'line_ids': journal_entry_lines,
        #     'ref': f"Journal Entry for PDC - {self.customer_id.name}" if self.customer_id else 'PDC Entry',
        #     'move_type': 'entry',
        #     'state': 'draft',
        # })
        self.status = 'received'

    def action_deposit(self):
        self.status = 'matured'
        if self.status == ' matured':
            self.env['account.payment'].create({
                'payment_type': 'inbound',
                'partner_type': 'supplier',
                'partner_id': self.supplier_id.id,
                'amount': self.amount,
                'cheque_reference': self.cheque_no
            })

    def action_reject(self):
        self.status = 'rejected'
        return {
            'name': 'Reason',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            "view_type": "form",
            'res_model': 'pdc.reason.wizard',
            'target': 'new',
            'context': {'active_id': self.id,
                        'state': 'rejected'
                        }
        }

    def action_hold(self):
        self.status = 'hold'
        return {
            'name': 'Reason',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            "view_type": "form",
            'res_model': 'pdc.reason.receive.hold.wizard',
            'target': 'new',
            'context': {'active_id': self.id,
                        'type': 'submit'
                        }
        }

    def action_returned(self):
        self.status = 'returned'
        return {
            'name': 'Reason',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            "view_type": "form",
            'res_model': 'pdc.reason.wizard',
            'target': 'new',
            'context': {'active_id': self.id,
                        'state': 'returned'
                        }
        }

    def send_reminder_pdc_submitted(self):
        today = fields.Date.today()
        two_days_ahead = today + timedelta(days=2)
        one_day_ahead = today + timedelta(days=1)
        records = self.search([
            ('cheque_date', 'in', [two_days_ahead, one_day_ahead, today]),
            ('status', '=', 'received')
        ])
        for record in records:
            account_manager_group = self.env.ref('base_accounting_kit.group_account_manager')
            account_user_group = self.env.ref('base_accounting_kit.group_account_user')
            users_to_notify = account_manager_group.user_ids | account_user_group.user_ids
            for user in users_to_notify:
                if user.email and self.env.user.email:
                    subject = f"Reminder: Cheque {record.cheque_no} Due Soon"
                    body = f"""
                                   <p>Hello {record.customer_id.name},</p>
                                   <p>This is a reminder that your cheque <strong>{record.cheque_no}</strong> is due on <strong>{record.cheque_date}</strong>.</p>
                                   <p>Please ensure timely action.</p>
                                   <p>Thank you!</p>
                                   """
                    # Send the email
                    mail_values = {
                        'subject': subject,
                        'body_html': body,
                        'email_from': self.env.user.email,
                        'email_to': user.email,  # Send to customer email
                    }
                    self.env['mail.mail'].create(mail_values).send()


class PdcPaymentReceived(models.Model):
    _name = 'pdc.payment.received'
    _description = 'PDC Received'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'cheque_no'

    cheque_no = fields.Char(string='Cheques Number', tracking=True)
    customer_id = fields.Many2one('res.partner', string="Customer", tracking=True)
    cheque_date = fields.Date(string="Cheque Date", tracking=True)
    amount = fields.Float(string="Amount", tracking=True)
    bank = fields.Char(string="Bank Name", tracking=True)
    status = fields.Selection(
        [('draft', 'Draft'), ('received', 'Received'), ('deposited', 'Deposited'), ('matured', 'Matured'),
         ('rejected', 'Bounced'), ('hold', 'Hold'),
         ('returned', 'Returned')], tracking=True, default='draft', copy=False)
    reject_reason = fields.Text(string='Reject Reason', tracking=True)
    hold_reason = fields.Text(string='Hold Reason', tracking=True)
    return_reason = fields.Text(string='Return Reason', tracking=True)
    is_delayed = fields.Boolean(string='Is Delayed', compute='_compute_is_delayed')
    deposited = fields.Many2one('account.journal', string='Deposited On',
                                domain="[('type', '=', 'bank')]")
    deposited_on = fields.Date(string='Deposited Date')
    payment_id = fields.Many2one('account.payment',string="Payment")
    acc_id = fields.Many2one('account.account', string="Account Receivable")
    p_acc_id = fields.Many2one('account.account', string="Post Date Check Receivable")
    journal_id = fields.Many2one('account.journal',string="Journal")
    journal_entry_id = fields.Many2one(
        'account.move',
        string="Journal Entry"
    )
    company_id = fields.Many2one(
        'res.company',
        string="Company",
        tracking=True,
        default=lambda self: self.env.company,
        readonly=True
    )
    enable_accounting_entry = fields.Boolean(
        string="Enable Accounting Entry",
        default=False
    )
    cheque_pay_name = fields.Char(
        string="Cheque Pay Name",

    )

    @api.depends('cheque_date', 'status')
    def _compute_is_delayed(self):
        for record in self:
            if record and record.cheque_date:
                if record.status == 'received' and record.cheque_date < fields.Date.today():
                    record.is_delayed = True
                else:
                    record.is_delayed = False
            else:
                record.is_delayed = False

    def action_draft_to_receive(self):
        self.status = 'received'

    def action_deposit(self):
        return {
            'name': 'Deposit Details',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            "view_type": "form",
            'res_model': 'pdc.deposited.wizard',
            'target': 'new',
            'context': {
                'active_id': self.id,
            }
        }

    def action_matured(self):
        if self.enable_accounting_entry:
            if self.journal_entry_id.state != 'posted':
                raise UserError(
                    _("Journal is Not Posted Yet!!"))
        self.status = 'matured'
        if self.enable_accounting_entry:
            action = self.env.ref(
                'account.action_view_account_move_reversal'
            ).read()[0]

            action['context'] = {
                'active_model': 'account.move',
                'active_ids': [self.journal_entry_id.id],
                'active_id': self.journal_entry_id.id,
            }
            return action

    def action_reject(self):
        self.status = 'rejected'
        # tenancy_id = self.env['tenancy.contract.schedule'].search(
        #     [('pdc_received_id', '=', self.id), ('state', '=', 'in_progress')])
        # if tenancy_id:
        #     # self.env['legal.case'].create({
        #     #     'case_type': 'cheque_return',
        #     #     'property_id': tenancy_id.property_id.id,
        #     #     'tenant_id': tenancy_id.tenancy_id.tenant.id,
        #     #     'amount': self.amount,
        #     #     'bank': self.bank,
        #     #     'priority': '2',
        #     # })
        #     tenancy_id.penalty_amount = tenancy_id.tenancy_id.penalty_amount
        return {
            'name': 'Reason',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            "view_type": "form",
            'res_model': 'pdc.reason.receive.wizard',
            'target': 'new',
            'context': {'active_id': self.id,
                        'state': 'rejected'
                        }
        }

    def action_hold(self):
        self.status = 'hold'
        return {
            'name': 'Reason',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            "view_type": "form",
            'res_model': 'pdc.reason.receive.hold.wizard',
            'target': 'new',
            'context': {'active_id': self.id,
                        'type': 'receive'
                        }
        }

    def action_returned(self):
        self.status = 'returned'
        return {
            'name': 'Reason',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            "view_type": "form",
            'res_model': 'pdc.reason.receive.wizard',
            'target': 'new',
            'context': {'active_id': self.id,
                        'state': 'returned'
                        }
        }

    def send_reminder_pdc_received(self):
        today = fields.Date.today()
        upcoming_dates = [today + timedelta(days=i) for i in range(6)]
        records = self.search([
            ('cheque_date', 'in', upcoming_dates),
            ('status', '=', 'received')
        ])
        for record in records:
            if record.customer_id.email:
                subject = f"Reminder: Cheque {record.cheque_no} Due in soon"
                body = f"""
                                <p>Hello {record.customer_id.name},</p>
                                <p>This is a reminder that cheque <strong>{record.cheque_no}</strong> is due on <strong>{record.cheque_date}</strong>.</p>
                                <p>Please ensure timely action.</p>
                                <p>Thank you!</p>
                                """
                mail_values = {
                    'subject': subject,
                    'body_html': body,
                    'email_from': self.env.user.email,
                    'email_to': record.customer_id.email,
                    'email_cc': self.created_by.partner_id.email,
                }
                self.env['mail.mail'].create(mail_values).send()

    def send_reminder_deposit(self):
        today = fields.Date.today()
        records = self.search([
            ('deposited_on', '<', today),
            ('status', '=', 'deposited')
        ])
        for record in records:
            if record.customer_id.email:
                subject = f"Reminder: Cheque {record.cheque_no} Not Matured !!"
                body = f"""
                                <p>Hello {record.customer_id.name},</p>
                                <p>This is a reminder that cheque <strong>{record.cheque_no}</strong> was deposited on <strong>{record.deposited_on}</strong>, but it has not yet matured.</p>
                                <p>Please ensure any necessary actions are taken to process the cheque timely</p>
                                <p>Thank you!</p>
                                """
                mail_values = {
                    'subject': subject,
                    'body_html': body,
                    'email_from': self.env.user.email,
                    'email_to': record.customer_id.email,
                }
                self.env['mail.mail'].create(mail_values).send()

class PDCAccount(models.Model):
    _name = 'pdc.account'
    _description = 'PDC Account'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'acc_id'

    acc_id = fields.Many2one('account.account',string="Account Receivable")
    p_acc_id = fields.Many2one('account.account',string="Post Date Check Receivable")