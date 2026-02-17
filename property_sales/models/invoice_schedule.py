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
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError

class InvoiceScheduleLine(models.Model):
    _name = 'invoice.schedule.line'
    _description = 'Invoice Schedule Line'

    project_id = fields.Many2one(
        'project.project',
        string="Project",
        ondelete='cascade'
    )

    date = fields.Date(
        string="Date",
        required=True
    )

    actual_progress = fields.Float(
        string='Actual Progress (%)'
    )

    invoice_id = fields.Many2one(
        'account.move',
        string='Invoice',
        readonly=True
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('invoiced', 'Invoiced'),
        ('paid', 'Paid')
    ],
        default='draft',
        string="Status"
    )

    payment_status = fields.Selection(
        related='invoice_id.payment_state',
        string='Payment Status',
        store=True
    )

    partner_id = fields.Many2one(
        'res.partner',
        string="Client",
        tracking=True,
    )

    amount = fields.Float(
        "Amount",
        compute='_compute_amount')

    is_invoiced = fields.Boolean(
        string="Is Invoiced",
        default=False
    )

    is_advance = fields.Boolean(
        string="Is Advance",
        default=False,
    )

    is_retention = fields.Boolean(
        string="Is Retention",
        default=False
    )

    total_inv_amount = fields.Float(
        string='Total Invoice Amount',
        default=0.0
    )

    retention_amount = fields.Float(
        string='Retention Amount',
        default=0.0
    )

    advance_amount = fields.Float(
        string='Advance Amount',
        default=0.0
    )

    def unlink(self):
        if self.state!='draft':
            raise UserError('Delete Not Possible')
        return super(InvoiceScheduleLine, self).unlink()


    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        project_id = self.env.context.get('default_project_id')
        if project_id:
            project = self.env['project.project'].browse(project_id)
            res['partner_id'] = project.partner_id.id
        return res


    @api.onchange('date','project_id')
    def _onchange_date_in_schedule(self):
        if self.project_id:
            self.partner_id = self.project_id.partner_id.id

    @api.constrains('actual_progress', 'project_id')
    def _check_total_progress(self):
        for line in self:
            if not line.project_id:
                continue

            lines = self.search([
                ('project_id', '=', line.project_id.id),
                ('id', '!=', line.id),
            ])

            total_progress = sum(lines.mapped('actual_progress')) + (line.actual_progress or 0.0)

            if total_progress > 100:
                raise ValidationError(_(
                    'Total Actual Progress for this project cannot exceed 100%%.\n'
                    'Current total: %.2f%%'
                ) % total_progress)

    def _calculate_amounts(self):
        for line in self:
            if line.is_advance or line.is_retention:
                line.amount = line.invoice_id.amount_total
            else:
                if not line.project_id or not line.actual_progress:
                    line.amount = 0.0
                    continue
                actual_progress_value = (
                        line.project_id.project_value * (line.actual_progress / 100.0)
                )
                line.amount = actual_progress_value

                # Percentages from project
                advance_percentage = line.project_id.advance_percentage or 0.0
                retention_percentage = line.project_id.retention_percentage or 0.0

                # Compute amounts
                if not line.is_advance and not line.is_retention:
                    line.advance_amount = -(actual_progress_value * (advance_percentage / 100.0))
                    line.retention_amount = -(actual_progress_value * (retention_percentage / 100.0))

                # Net invoice amount
                line.total_inv_amount = (
                        actual_progress_value
                        + line.advance_amount
                        + line.retention_amount
                )

    def _compute_amount(self):
        self._calculate_amounts()

    @api.onchange(
        'is_advance',
        'is_retention',
        'invoice_id',
        'project_id',
        'actual_progress',
    )
    def _onchange_amount_fields(self):
        self._calculate_amounts()

    def action_create_invoice(self):
        if self.project_id.schedule_line_ids:
            lines = self.project_id.schedule_line_ids
            has_advance = any(line.is_advance for line in lines)
            has_invoiced_normal_line = any(
                not l.is_retention and not l.is_advance and l.state == 'invoiced'
                for l in lines
            )
            if not has_advance and self.project_id.advance_amount>0:
                if not has_invoiced_normal_line:
                    return self.action_confirm_create()

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

        invoice_lines = []

        # 🔹 Main line (positive)
        invoice_lines.append((0, 0, {
            'name': f"{self.project_id.name} -- {self.date} -- ({self.actual_progress}% of {self.project_id.project_value})",
            'quantity': 1.0,
            'price_unit': self.amount,
            'analytic_distribution': analytic_distribution,
        }))

        # 🔹 Advance deduction (minus)
        if self.advance_amount:
            invoice_lines.append((0, 0, {
                'name': 'Advance Deduction',
                'quantity': 1.0,
                'price_unit': -self.advance_amount,
                'analytic_distribution': analytic_distribution,
            }))

        # 🔹 Retention deduction (minus)
        if self.retention_amount:
            invoice_lines.append((0, 0, {
                'name': 'Retention Deduction',
                'quantity': 1.0,
                'price_unit': -self.retention_amount,
                'analytic_distribution': analytic_distribution,
            }))

        bill_vals = {
            'move_type': 'in_invoice',
            'partner_id': self.partner_id.id,
            'invoice_date': self.date,
            'company_id': company.id,
            'invoice_origin': self.project_id.name,
            'property_type': 'construction',
            'project_construction_id': self.project_id.id,
            'invoice_line_ids': invoice_lines
        }

        bill = self.env['account.move'].create(bill_vals)

        bill.action_post()

        self.invoice_id = bill.id
        self.is_invoiced = True
        self.state = 'invoiced'

    def action_confirm_create(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Confirmation',
            'res_model': 'invoice.schedule.confirm.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_line_id': self.id,
            }
        }