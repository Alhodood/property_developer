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
from odoo.tools import float_compare

class PaymentPlan(models.Model):
    _name = 'property.payment.plan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _description = 'Property Payment Plan'
    _order = 'id desc'

    name = fields.Char(string="Name")

    payment_line_ids = fields.One2many('property.payment.plan.line',
                                       'payment_id',
                                       string="Payment Lines")
    property_project_id = fields.Many2one(
        'property.project',
        string="Property Project",
        tracking=True
    )

    before_percentage = fields.Float(
        string="Before Percentage",
        default=0.0,
        tracking=True,
    )

    after_percentage = fields.Float(
        string="After Percentage",
        default=0.0,
        tracking=True,
    )

    @api.constrains('payment_line_ids', 'payment_line_ids.percentage')
    def _check_total_percentage(self):
        for plan in self:
            total = sum(plan.payment_line_ids.mapped('percentage'))

            if plan.payment_line_ids and float_compare( total, 100.0, precision_digits=2) != 0:
                raise UserError(
                    "Total percentage of all payment lines must be exactly 100%.\n"
                    f"Current total: {total}%"
                )

    def action_view_payment_plans(self):
        """ View All  Payment Plan """
        return {
            'name': 'Payment Plan',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'property.payment.plan',
            'res_id': self.id,
            'target': 'current',
        }


class PaymentPlanLine(models.Model):
    _name = 'property.payment.plan.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'description'
    _description = 'Property Payment Plan Lines'
    _order = 'id ASC'

    payment_id = fields.Many2one(
        'property.payment.plan',
        string="Payment"
    )

    description = fields.Char(
        string="Milestone",
        tracking=True
    )

    installment_month = fields.Integer(
        string="Installments month",
        tracking=True
    )

    percentage = fields.Float(
        string="Percentage(%)",
        tracking=True,
        digits=(16, 2)
    )

    period_covered = fields.Selection([
        ('on_booking','On Booking'),
        ('before','Before Completion'),
        ('after','After Completion')],
        string="Period Covered",
        requitrd=True,
        tracking=True
    )

    start_date = fields.Date(
        string="Start date",
        tracking=True
    )

    end_date = fields.Date(
        string="End date",
        tracking=True
    )

    monthly_per = fields.Float(
        string="Monthly Percentage",
        compute='_compute_monthly_percentage'
    )

    quarterly_per = fields.Float(
        string="Quarterly Percentage",
        compute='_compute_quarterly_percentage'
    )

    half_yearly_per = fields.Float(
        string="Half Yearly Percentage",
        compute='_compute_half_yearly_percentage'
    )


    @api.depends('percentage','installment_month')
    def _compute_monthly_percentage(self):
        for rec in self:
            if rec.percentage != 0.0 and rec.installment_month !=0.0 and rec.period_covered != 'on_booking':
                rec.monthly_per = rec.percentage / rec.installment_month
            else:
                rec.monthly_per = 0.0

    @api.depends('percentage','installment_month','monthly_per')
    def _compute_quarterly_percentage(self):
        for rec in self:
            if rec.percentage != 0.0 and rec.installment_month != 0.0 and rec.monthly_per != 0.0 and rec.period_covered != 'on_booking':
                quarter_in_month = int(rec.installment_month / 3)
                if quarter_in_month != 0.0:
                    rec.quarterly_per = rec.percentage / quarter_in_month
                else:
                    rec.quarterly_per = 0.0
            else:
                rec.quarterly_per = 0.0

    @api.depends('percentage', 'installment_month', 'monthly_per')
    def _compute_half_yearly_percentage(self):
        for rec in self:
            if rec.percentage != 0.0 and rec.installment_month !=0.0 and rec.monthly_per != 0.0 and rec.period_covered != 'on_booking':
                quarter_in_month = int(rec.installment_month /6)
                if quarter_in_month != 0.0:
                    rec.half_yearly_per = rec.percentage / quarter_in_month
                else:
                    rec.half_yearly_per = 0.0
            else:
                rec.half_yearly_per = 0.0