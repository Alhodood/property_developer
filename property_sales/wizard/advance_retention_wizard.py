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
from odoo import fields, models, _, api
from odoo.exceptions import UserError


class AdvanceRetentionWizard(models.TransientModel):
    _name = 'advance.retention.wizard'
    _description = "Advance Retention Wizard"

    already_created = fields.Boolean(default=True)
    project_id = fields.Many2one(
        'project.project',
        string='Project',
    )
    bill_id = fields.Many2one(
        'account.move',
        string='Vendor Bill',
        domain="[('move_type', '=', 'in_invoice'), ('state', '=', 'posted')]",
        required=False
    )
    is_advance = fields.Boolean(default=False)
    is_retention = fields.Boolean(default=False)

    amount = fields.Float(string='Amount')

    @api.onchange('actual_progress')
    def _compute_amount(self):
        for line in self:
            if not line.project_id or not line.actual_progress:
                line.inv_amount = 0.0
                continue
            actual_progress_value = (
                    line.project_id.project_value * (line.actual_progress / 100.0)
            )
            line.inv_amount = actual_progress_value

            # Percentages from project
            advance_percentage = line.project_id.advance_percentage or 0.0
            retention_percentage = line.project_id.retention_percentage or 0.0

            # Compute amounts
            line.advance_amount = actual_progress_value * (advance_percentage / 100.0)
            line.retention_amount = actual_progress_value * (retention_percentage / 100.0)

            # Net invoice amount
            line.total_inv_amount = (
                    actual_progress_value
                    - line.advance_amount
                    - line.retention_amount
            )

    date = fields.Date(string='Date',default=fields.Date.today())
    partner_id = fields.Many2one('res.partner')

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        project_id = self.env.context.get('default_project_id')
        if project_id:
            project = self.env['project.project'].browse(project_id)
            res['partner_id'] = project.partner_id.id
        return res

    def action_add_done(self):
        if self.is_advance:
            if self.already_created:
                bill =self.bill_id
                line = self.schedule_lines_with_bill(bill)
                line.total_inv_amount = line.amount
                self.project_id.advance_amount = line.amount
                advance_percentage = (line.amount / self.project_id.project_value) * 100
                self.project_id.advance_percentage = advance_percentage
            else:
                bill = self._create_vendor_bill(
                    name='Advance Amount'
                )
                self.schedule_lines_with_bill(bill)
                self.project_id.advance_amount= self.amount
                advance_percentage = (self.amount / self.project_id.project_value) * 100
                self.project_id.advance_percentage = advance_percentage
        elif self.is_retention:
            if self.already_created:
                bill = self.bill_id
                line = self.schedule_lines_with_bill(bill)
                line.total_inv_amount = line.amount
                self.project_id.retention_amount = line.amount
                retention_percentage = (line.amount / self.project_id.project_value) * 100
                self.project_id.retention_percentage = retention_percentage
            else:
                bill = self._create_vendor_bill(
                    name='Advance Amount'
                )
                self.schedule_lines_with_bill(bill)
                self.project_id.retention_amount= self.amount
                retention_percentage = (self.amount / self.project_id.project_value) * 100
                self.project_id.retention_percentage = retention_percentage

    def schedule_lines_with_bill(self,bill):
        line = self.env['invoice.schedule.line'].create({
            'project_id': self.project_id.id,
            'date': self.date,
            'amount': self.amount,
            'total_inv_amount': self.amount,
            'invoice_id': bill.id if bill else False,
            'is_advance': self.is_advance,
            'is_retention': self.is_retention,
            'is_invoiced': True,
            'state': 'invoiced',
            'partner_id': self.partner_id.id,
        })
        return line



    def _create_vendor_bill(self, name):
        self.ensure_one()

        company = self.project_id.company_id or self.env.company

        if not self.partner_id:
            raise UserError("Please select a Vendor.")

        # Find expense account
        account = self.env['account.account'].search([
            ('account_type', '=', 'expense')
        ], limit=1)

        if not account:
            raise UserError("No Expense Account found for this company.")

        analytic_distribution = {}
        if self.project_id.account_id:
            analytic_distribution = {
                self.project_id.account_id.id: 100.0
            }
        bill_vals = {
            'move_type': 'in_invoice',
            'partner_id': self.partner_id.id,
            'invoice_date': self.date,
            'company_id': company.id,
            'property_type':'construction',
            'project_construction_id':self.project_id.id,
            'invoice_origin': self.project_id.name,
            'invoice_line_ids': [(0, 0, {
                'name': name,
                'quantity': 1.0,
                'price_unit': self.amount,
                'analytic_distribution': analytic_distribution,
            })]
        }

        bill = self.env['account.move'].create(bill_vals)

        bill.action_post()
        return bill
