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
from odoo import models, fields
from odoo.exceptions import UserError


class InvoiceScheduleConfirmWizard(models.TransientModel):
    _name = 'invoice.schedule.confirm.wizard'
    _description = 'Invoice Schedule Confirmation'

    line_id = fields.Many2one('invoice.schedule.line', required=True)

    def action_yes(self):
        company = self.line_id.project_id.company_id or self.env.company

        # Find expense account
        account = self.env['account.account'].search([
            ('account_type', '=', 'expense')
        ], limit=1)

        if not account:
            raise UserError("No Expense Account found for this company.")

        analytic_distribution = {}
        if self.line_id.project_id.account_id:
            analytic_distribution = {
                self.line_id.project_id.account_id.id: 100.0
            }

        invoice_lines = []

        # 🔹 Main line (positive)
        invoice_lines.append((0, 0, {
            'name': f"{self.line_id.project_id.name} -- {self.line_id.date} -- ({self.line_id.actual_progress}% of {self.line_id.project_id.project_value})",
            'quantity': 1.0,
            'price_unit': self.line_id.amount,
            'account_id': account.id,
            'analytic_distribution': analytic_distribution,
        }))

        # 🔹 Advance deduction (minus)
        if self.line_id.advance_amount:
            invoice_lines.append((0, 0, {
                'name': 'Advance Deduction',
                'quantity': 1.0,
                'price_unit': -self.line_id.advance_amount,
                'account_id': account.id,
                'analytic_distribution': analytic_distribution,
            }))

        # 🔹 Retention deduction (minus)
        if self.line_id.retention_amount:
            invoice_lines.append((0, 0, {
                'name': 'Retention Deduction',
                'quantity': 1.0,
                'price_unit': -self.line_id.retention_amount,
                'account_id': account.id,
                'analytic_distribution': analytic_distribution,
            }))

        bill_vals = {
            'move_type': 'in_invoice',
            'partner_id': self.line_id.partner_id.id,
            'invoice_date': self.line_id.date,
            'company_id': company.id,
            'invoice_origin': self.line_id.project_id.name,
            'property_type': 'construction',
            'project_construction_id': self.line_id.project_id.id,
            'invoice_line_ids': invoice_lines
        }

        bill = self.env['account.move'].create(bill_vals)

        bill.action_post()

        self.line_id.invoice_id = bill.id
        self.line_id.is_invoiced = True
        self.line_id.state = 'invoiced'

    def action_no(self):
        return {'type': 'ir.actions.act_window_close'}
