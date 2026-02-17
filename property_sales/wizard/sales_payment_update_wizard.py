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

class OfferPaymentUpdate(models.TransientModel):
    _name = 'offer.payment.update.wizard'
    _description = "Offer Payment Update"

    sale_order = fields.Many2one(
        'sale.order',
        string="Sales Offer",
        readonly=True
    )

    final_total_property_value = fields.Float(
        string="Final Sale Value",
        readonly=True
    )

    line_ids = fields.One2many(
        'offer.payment.update.wizard.line',
        'wizard_id',
        string="Payment Lines"
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        sales = self.env['sale.order'].browse(
            self.env.context.get('default_sale_order'))
        lines = []
        for line in sales.plan_lines_ids.sorted('sequence'):
            lines.append((0, 0, {
                'offer_line_id': line.id,
                'name': line.name,
                'in_offer': line.in_offer,
                'plan_date': line.plan_date,
                'percentage': line.percentage,
                'amount': line.amount,
                'rounded_amount': line.rounded_amount,
            }))
        res['line_ids'] = lines
        return res


    def action_confirm_update(self):
        for order in self:
            total_percentage = sum(
                order.line_ids.mapped('percentage')
            )
            if order.line_ids and round(total_percentage, 2) != 100.0:
                raise UserError(_(
                    "The total Payment Plan percentage with invoiced lines must be 100%%.\n"
                    "Current total: %.2f%%"
                ) % total_percentage)
            non_invoiced_lines = order.sale_order.plan_lines_ids
            non_invoiced_lines.unlink()
            sales_amount = order.final_total_property_value
            running_total = 0.0
            lines = order.line_ids.sorted(
                key=lambda l: l.plan_date or fields.Date.max)
            last_index = len(lines) - 1
            for idx, line in enumerate(lines):
                amount = (sales_amount * line.percentage) / 100
                if idx != last_index:
                    integer_part = int(amount)
                    last_two = integer_part % 100
                    rounded = integer_part - last_two if last_two < 50 else integer_part + (
                                100 - last_two)
                    running_total += rounded
                else:
                    rounded = sales_amount - running_total
                self.env['payment.plan.offer.line'].create({
                    'sale_order': order.sale_order.id,
                    'name': line.name,
                    'in_offer': line.in_offer,
                    'plan_date': line.plan_date,
                    'percentage': line.percentage,
                    'payment_id': order.sale_order.payment_plan_id.id,
                    'amount': amount,
                    'actual_amount': amount,
                    'rounded_amount': rounded,
                })


class OfferPaymentUpdateWizardLine(models.TransientModel):
    _name = 'offer.payment.update.wizard.line'
    _description = 'Update Offer Payment Line'

    wizard_id = fields.Many2one(
        'offer.payment.update.wizard',
        required=True,
        ondelete='cascade'
    )

    in_offer = fields.Boolean(
        string="In Booking",
        default=False
    )

    offer_line_id = fields.Many2one(
        'payment.plan.offer.line',
        string="Original Line"
    )

    name = fields.Char(
        string="Name"
    )

    plan_date = fields.Date(
        string="Date"
    )
    percentage = fields.Float(
        string="Percentage (%)"
    )

    amount = fields.Float(
        string="Amount",
        readonly=True,
        compute='_compute_total_amount'
    )

    rounded_amount = fields.Float(
        string="Rounded Amount",
        readonly=True
    )


    @api.depends('percentage', 'amount')
    def _compute_total_amount(self):
        for rec in self:
            rec.amount = 0.0
            if rec.wizard_id.final_total_property_value:
                amount = (rec.wizard_id.final_total_property_value * rec.percentage) / 100
                rec.amount = amount

    @api.depends('percentage', 'amount')
    def _compute_rounded_amount(self):
        """
        Rounds the actual_amount using the rule:
        last two digits < 50 → round down
        last two digits ≥ 50 → round up
        """
        for rec in self:
            if rec.amount:
                last_line = rec.wizard_id.line_ids.sorted(
                    lambda l: (l.plan_date or fields.Date.today()),
                )[-1]
                if last_line and rec.id == last_line.id:
                    if rec.wizard_id.final_total_property_value:
                        sales_amount = rec.wizard_id.final_total_property_value
                        other_lines = rec.wizard_id.line_ids.filtered(
                            lambda l: l.id != rec.id
                        )
                        other_total = sum(
                            l.rounded_amount for l in other_lines
                        )
                        rec.rounded_amount = sales_amount - other_total
                    else:
                        integer_part = int(rec.amount)
                        last_two_digits = integer_part % 100
                        if last_two_digits < 50:
                            rounded = integer_part - last_two_digits
                        else:
                            rounded = integer_part + (100 - last_two_digits)

                        rec.rounded_amount = float(rounded)
                else:
                    integer_part = int(rec.amount)
                    last_two_digits = integer_part % 100
                    if last_two_digits < 50:
                        rounded = integer_part - last_two_digits
                    else:
                        rounded = integer_part + (100 - last_two_digits)

                    rec.rounded_amount = float(rounded)
            else:
                rec.rounded_amount = 0.0

    # def action_delete_line(self):
    #     for record in self:
    #         if record.inv_created:
    #             raise UserError(
    #                 _("You can't delete payment lines already invoiced!")
    #             )
    #     return self.unlink()


class BookingPaymentUpdate(models.TransientModel):
    _name = 'booking.payment.update.wizard'
    _description = "Booking Payment Update"

    booking_id = fields.Many2one(
        'offer.booking',
        string="Offer Booking",
        readonly=True
    )

    final_total_property_value = fields.Float(
        string="Final Sale Value",
        readonly=True
    )

    line_ids = fields.One2many(
        'booking.payment.update.wizard.line',
        'wizard_id',
        string="Payment Lines"
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        offer_booking = self.env['offer.booking'].browse(
            self.env.context.get('default_booking_id'))
        lines = []
        for line in offer_booking.payment_schedule_ids.filtered(
                lambda l: not l.inv_created).sorted('sequence'):
            lines.append((0, 0, {
                'offer_line_id': line.id,
                'name': line.name,
                'plan_date': line.plan_date,
                'percentage': line.percentage,
                'amount': line.amount,
                'rounded_amount': line.rounded_amount,
                'inv_created': line.inv_created,
            }))
        res['line_ids'] = lines
        return res


    def action_confirm_update(self):
        for order in self:
            total_percentage = sum(
                order.line_ids.mapped('percentage')
            )
            product_lines = order.booking_id.payment_schedule_ids.filtered(
                lambda l: l.inv_created)
            line_percentage = sum(product_lines.mapped('percentage'))
            invoiced_rounded_total = sum(product_lines.mapped('rounded_amount'))
            total_percentage = total_percentage + line_percentage
            if order.line_ids and round(total_percentage, 2) != 100.0:
                raise UserError(_(
                    "The total Payment Plan percentage with invoiced lines must be 100%%.\n"
                    "Current total: %.2f%%"
                ) % total_percentage)
            non_invoiced_lines = order.booking_id.payment_schedule_ids.filtered(
                lambda l: not l.inv_created)
            non_invoiced_lines.unlink()
            sales_amount = order.final_total_property_value
            running_total = invoiced_rounded_total
            lines = order.line_ids.sorted(
                key=lambda l: l.plan_date or fields.Date.max)
            last_index = len(lines) - 1
            for idx, line in enumerate(lines):
                amount = (sales_amount * line.percentage) / 100
                if idx != last_index:
                    integer_part = int(amount)
                    last_two = integer_part % 100
                    rounded = integer_part - last_two if last_two < 50 else integer_part + (
                                100 - last_two)
                    running_total += rounded
                else:
                    rounded = sales_amount - running_total
                self.env['payment.schedule.line'].create({
                    'offer_id': order.booking_id.id,
                    'property_project_id': order.booking_id.property_project_id.id,
                    'property_unit_id': order.booking_id.property_unit_id.id,
                    'buyer_id': order.booking_id.partner_id.id,
                    'sale_order': order.booking_id.sale_id.id,
                    'name': line.name,
                    'plan_date': line.plan_date,
                    'percentage': line.percentage,
                    'payment_id': order.booking_id.payment_plan_id.id,
                    'amount': amount,
                    'rounded_amount': rounded,
                })


class BookingPaymentUpdateWizardLine(models.TransientModel):
    _name = 'booking.payment.update.wizard.line'
    _description = 'Update Booking Payment Line'

    wizard_id = fields.Many2one(
        'booking.payment.update.wizard',
        required=True,
        ondelete='cascade'
    )


    inv_created = fields.Boolean(
        string="Invoice Created"
    )

    offer_line_id = fields.Many2one(
        'payment.schedule.line',
        string="Original Line"
    )

    name = fields.Char(
        string="Name"
    )

    plan_date = fields.Date(
        string="Date"
    )
    percentage = fields.Float(
        string="Percentage (%)"
    )

    amount = fields.Float(
        string="Amount",
        readonly=True,
        compute='_compute_total_amount'
    )

    rounded_amount = fields.Float(
        string="Rounded Amount",
        readonly=True
    )


    @api.depends('percentage', 'amount')
    def _compute_total_amount(self):
        for rec in self:
            rec.amount = 0.0
            if rec.wizard_id.final_total_property_value:
                amount = (rec.wizard_id.final_total_property_value * rec.percentage) / 100
                rec.amount = amount

    @api.depends('percentage', 'amount')
    def _compute_rounded_amount(self):
        """
        Rounds the actual_amount using the rule:
        last two digits < 50 → round down
        last two digits ≥ 50 → round up
        """
        for rec in self:
            if rec.amount:
                last_line = rec.wizard_id.line_ids.sorted(
                    lambda l: (l.plan_date or fields.Date.today()),
                )[-1]
                if last_line and rec.id == last_line.id:
                    if rec.wizard_id.final_total_property_value:
                        sales_amount = rec.wizard_id.final_total_property_value
                        other_lines = rec.wizard_id.line_ids.filtered(
                            lambda l: l.id != rec.id
                        )
                        other_total = sum(
                            l.rounded_amount for l in other_lines
                        )
                        rec.rounded_amount = sales_amount - other_total
                    else:
                        integer_part = int(rec.amount)
                        last_two_digits = integer_part % 100
                        if last_two_digits < 50:
                            rounded = integer_part - last_two_digits
                        else:
                            rounded = integer_part + (100 - last_two_digits)

                        rec.rounded_amount = float(rounded)
                else:
                    integer_part = int(rec.amount)
                    last_two_digits = integer_part % 100
                    if last_two_digits < 50:
                        rounded = integer_part - last_two_digits
                    else:
                        rounded = integer_part + (100 - last_two_digits)

                    rec.rounded_amount = float(rounded)
            else:
                rec.rounded_amount = 0.0

    def action_delete_line(self):
        for record in self:
            if record.inv_created:
                raise UserError(
                    _("You can't delete payment lines already invoiced!")
                )
        return self.unlink()

