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
from odoo.tools import float_compare
from odoo.exceptions import UserError
import uuid
import base64
from io import BytesIO
from openpyxl import Workbook
from dateutil.relativedelta import relativedelta

SALE_ORDER_STATE = [
    ('draft', "Quotation"),
    ('sent', "Offer Sent"),
    ('accepted', "Client Accepted"),
    ('rejected', "Client Rejected"),
    ('sale', "Sales Order"),
    ('cancel', "Cancelled"),
]

def _default_access_token(self):
    return uuid.uuid4().hex

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection(
        selection=SALE_ORDER_STATE,
        string="Status",
        readonly=True, copy=False, index=True,
        tracking=3,
        default='draft')

    property_type = fields.Selection([
        ('broker', 'Brokerage'),
        ('rent', 'Rent')
    ],
        string="Property Type"
    )

    property_project_id = fields.Many2one(
        'property.project',
        string="Project",
        tracking=True
    )

    property_unit_id = fields.Many2one(
        'property.unit',
        string="Unit",
        domain='[("project_id", "=", property_project_id),("status","=","available")]',
    )

    client_type = fields.Selection(
        [('direct', 'Direct'),
         ('indirect', 'Indirect')],
        string="Client Type",
    )


    php = fields.Monetary(
        string="Unit Sale Price",
        currency_field='currency_id',
        related='property_unit_id.php',
        store=True
    )

    discount_per = fields.Float(
        string="Special Discount (%)"
    )

    total_amount_unit_price = fields.Float(
        string="Sales Total Amount",
        compute='_compute_total_amount_unit'
    )

    allowed_payment_plan_ids = fields.Many2many(
        'property.payment.plan',
        readonly=True,
        compute='_compute_allowed_payment_plan_ids'
    )

    payment_plan_id = fields.Many2one(
        'property.payment.plan',
        string="Payment Plan",
        domain='[("id", "in", allowed_payment_plan_ids)]',

    )

    start_date = fields.Date(
        string="Start Date"
    )

    period_of_installment = fields.Selection(
        [('monthly','Monthly'),
         ('quarterly','Quarterly'),
         ('half_year','Half Yearly'),
         ('yearly','Yearly')]
    )

    payment_plan_summary_ids = fields.One2many(
        'payment.plan.summary',
        'sale_order',
        string="Payment Plan Summary",

    )

    plan_lines_ids = fields.One2many(
        'payment.plan.offer.line',
        'sale_order',
        string="Plan Lines"
    )
    offer_quote_line_ids = fields.One2many(
        'offer.quote.line',
        'sale_order',
        string="Plan Lines"
    )

    verify_line = fields.Boolean(
        string="Verify Line",
        default=False,
        tracking=True
    )

    booking = fields.Boolean(
        string="Booking",
        default=False
    )

    eoi = fields.Boolean(
        string="EOI",
        default=False
    )

    booking_id = fields.Many2one(
        'offer.booking',
        string="Offer Booking"
    )

    access_token = fields.Char('Invitation Token',
                               default=_default_access_token)
    crm_lead_id = fields.Many2one(
        'crm.lead',
        string="Lead"
    )

    lead_agent_id = fields.Many2one(
        'res.partner',
        string="Agent",
        domain="[('par_type', '=', 'agent')]",
    )
    generate_line = fields.Boolean(
        string="Generate Lines",
        default=False
    )

    reserve_property = fields.Boolean(
        string="Reserve Property",
        default=False
    )

    is_block_lead = fields.Boolean(
        string="Is Block Lead",
        default=False
    )

    block_type = fields.Selection(
        [('blocked', 'Unit Blocked')],
        string="Block Status",
    )

    property_blocking_request_ids = fields.One2many(
        'blocking.request',
        'sale_order',
        string="Blocking Request"
    )

    print_reference = fields.Char(string="Print Reference")

    total_rounded_amount = fields.Monetary(
        string="Total Rounded Amount",
        compute="_compute_total_rounded_amount",
        currency_field='currency_id',
        store=True
    )

    client_reject_reason = fields.Text("Client Reject Reason")
    discount_based_on = fields.Selection(
        [('down_payment','Down Payment'),
         ('Payment_Plan','Payment Plan')
         ],
        string="Discount Based On"
    )

    discount_approval_status = fields.Selection(
        [('discount_approval','Please request discount approval from the manager.')],
        string="Discount Approval Status",
    )
    discount_approval_need = fields.Boolean(
        string="Discount Approval Need",
        compute='_compute_discount_approval_need'
    )

    discount_approved = fields.Boolean(
        string="Discount Approved",
        default=False,
        tracking=True,
    )

    request_for_approval = fields.Boolean(
        string="Request For Approval",
        default=False,
        tracking=True
    )

    discount_status = fields.Selection(
        [('waiting','Waiting For Approval'),
                 ('approved','Approved'),
                 ('rejected','Rejected')],
        string="Discount Status",
        tracking=True
    )

    approved_reject_reason = fields.Text(
        string="Approved/Reject Reason",
        tracking=True
    )

    discount_approved_percentage = fields.Float(
        string="Discount Approved Percentage",
        default=0.0
    )

    @api.depends('discount_per','discount_based_on','payment_plan_id','discount_approved','plan_lines_ids','property_project_id')
    def _compute_discount_approval_need(self):
        for rec in self:
            rec.discount_approval_need = False
            if rec.discount_per >0:
                if rec.client_type == 'direct':
                    if rec.discount_based_on == 'down_payment':
                        plan_lines = rec.plan_lines_ids.filtered(lambda l: l.in_offer)
                        if plan_lines:
                            percentage = sum(plan_lines.mapped('percentage'))
                            if rec.property_project_id.direct_down_payment_ids:
                                # matching_line = rec.property_project_id.direct_down_payment_ids.filtered(
                                #     lambda l: l.down_payment == percentage
                                # )
                                matching_line = rec.property_project_id.direct_down_payment_ids.filtered(
                                    lambda l: float_compare(
                                        l.down_payment,
                                        percentage,
                                        precision_digits=2
                                    ) == 0
                                )
                                if matching_line:
                                    allowed_percentage = matching_line[0].allowed_percentage
                                    if rec.discount_per > allowed_percentage:
                                        if rec.discount_approved == False:
                                            rec.discount_approval_need = True
                                            rec.discount_approval_status = 'discount_approval'
                    if rec.discount_based_on == 'Payment_Plan':
                        if rec.payment_plan_id:
                            if rec.property_project_id.direct_payment_plan_ids:
                                matching_line = rec.property_project_id.direct_payment_plan_ids.filtered(
                                    lambda l: l.payment_plan_id == rec.payment_plan_id
                                )
                                if matching_line:
                                    allowed_percentage = matching_line[0].allowed_percentage
                                    if rec.discount_per > allowed_percentage:
                                        if rec.discount_approved == False:
                                            rec.discount_approval_need = True
                                            rec.discount_approval_status = 'discount_approval'
                if rec.client_type == 'indirect':
                    if rec.discount_based_on == 'down_payment':
                        plan_lines = rec.plan_lines_ids.filtered(lambda l: l.in_offer)
                        if plan_lines:
                            percentage = sum(plan_lines.mapped('percentage'))
                            if rec.property_project_id.in_direct_down_payment_ids:
                                matching_line = rec.property_project_id.in_direct_down_payment_ids.filtered(
                                    lambda l: float_compare(
                                        l.down_payment,
                                        percentage,
                                        precision_digits=2) == 0
                                )
                                if matching_line:
                                    allowed_percentage = matching_line[0].allowed_percentage
                                    if rec.discount_per > allowed_percentage:
                                        if rec.discount_approved == False:
                                            rec.discount_approval_need = True
                                            rec.discount_approval_status = 'discount_approval'
                    if rec.discount_based_on == 'Payment_Plan':
                        if rec.payment_plan_id:
                            if rec.property_project_id.in_direct_payment_plan_ids:
                                matching_line = rec.property_project_id.in_direct_payment_plan_ids.filtered(
                                    lambda l: l.payment_plan_id == rec.payment_plan_id
                                )
                                if matching_line:
                                    allowed_percentage = matching_line[0].allowed_percentage
                                    if rec.discount_per > allowed_percentage:
                                        if rec.discount_approved == False:
                                            rec.discount_approval_need = True
                                            rec.discount_approval_status = 'discount_approval'

    def action_request_for_discount_approval(self):
        if not self.generate_line:
            raise UserError(_("Please Generate Payment Lines First!!."))
        return {
            'type': 'ir.actions.act_window',
            'name': 'Discount Request',
            'res_model': 'discount.request.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_sale_order': self.id,
                'default_request_percentage': self.discount_per,
            }
        }

    def action_revise_sale_offer(self):
        self.state = 'draft'

    @api.depends('php','discount_per')
    def _compute_total_amount_unit(self):
        for rec in self:
            if rec.discount_per > 0:
                discount_amount = (rec.php * rec.discount_per)/100
                rec.total_amount_unit_price = rec.php - discount_amount
            else:
                rec.total_amount_unit_price = rec.php


    @api.depends('plan_lines_ids',
                 'plan_lines_ids.rounded_amount')
    def _compute_total_rounded_amount(self):
        for rec in self:
            rec.total_rounded_amount = sum(
                rec.plan_lines_ids.mapped('rounded_amount')
            )

    @api.onchange('partner_id')
    def _onchange_partner_id_set_client_type(self):
        if self.partner_id:
            self.client_type = self.partner_id.client_type

    @api.onchange('crm_lead_id')
    def _onchange_crm_lead(self):
        if self.crm_lead_id.property_project_id:
            self.property_project_id = self.crm_lead_id.property_project_id.id
            self.property_unit_id = self.crm_lead_id.property_unit_id.id
            self.lead_agent_id = self.crm_lead_id.lead_agent_id.id
            self.php = self.crm_lead_id.property_unit_id.php

    @api.onchange('property_unit_id')
    def _onchange_property_unit_value(self):
        if self.property_unit_id:
            self.php = self.property_unit_id.php


    @api.depends('property_project_id')
    def _compute_allowed_payment_plan_ids(self):
        for rec in self:
            if rec.property_project_id:
                payment_plan = self.env['property.payment.plan'].search([('property_project_id','=',rec.property_project_id.id)])
                if payment_plan:
                    rec.allowed_payment_plan_ids = payment_plan.ids
                else:
                    rec.allowed_payment_plan_ids =False
            else:
                rec.allowed_payment_plan_ids = False


    def action_quotation_send(self):
        if self.discount_approval_need ==True:
            if self.discount_approved == False:
                raise UserError(_("Sorry Please Take Discount Approval From Manager!!."))
        if self.discount_status == 'rejected':
            raise UserError(
                _("Please Click The CLear Button Clear The Discount And Generate LInes Again!!."))
        if not self.property_project_id.direct_down_payment_ids:
            raise UserError(
                _("Please Configure Direct Down Payment Discount Structure!!."))
        if not self.property_project_id.direct_payment_plan_ids:
            raise UserError(
                _("Please Configure Direct Payment Plan Discount Structure!!."))
        if not self.property_project_id.in_direct_payment_plan_ids:
            raise UserError(
                _("Please Configure In Direct Payment Plan Discount Structure!!."))

        if not self.property_project_id.in_direct_down_payment_ids:
            raise UserError(
                _("Please Configure In Direct  Down Payment  Discount Structure!!."))

        res = super(SaleOrder, self).action_quotation_send()
        if res.get('context') and len(self) == 1:
            template = self.env.ref('property_sales.custom_sale_order_mail_template', raise_if_not_found=False)
            self.print_reference = self.env['ir.sequence'].next_by_code('sale.offer.print')
            template = template.sudo()
            amount = 0.0
            if template:
                # Calculate total amount
                product_line = self.offer_quote_line_ids.filtered(
                    lambda l: l.product_line)
                if product_line:
                    product_line = product_line[0]
                    amount = (product_line.discounted_amount)
                formatted_amount = f"{amount:,.2f}"

                # Generate Accept/Decline URLs dynamically
                base_url = self.get_base_url()
                accept_url = f"{base_url}/sale/offer/accept?token={self.access_token}&id={self.id}"
                decline_url = f"{base_url}/sale/offer/decline?token={self.access_token}&id={self.id}"

                # Dynamic status-to-color mapping (like QWeb <t t-set>)
                status_colors = {
                    'needsAction': 'grey',
                    'accepted': 'green',
                    'tentative': '#FFFF00',
                    'declined': 'red',
                }

                # Assuming you have a field self.offer_status
                offer_status = getattr(self, 'offer_status', 'needsAction')
                status_color = status_colors.get(offer_status, 'black')  # default color

                # Update subject dynamically
                template.subject = f"Sale Offer {self.name} - ₹ {formatted_amount}"

                # Update body with Accept / Decline buttons and colored status
                template.body_html = f"""
                        <p>Hello {self.partner_id.name},</p>
                        <p>
                            We are pleased to share your <b>Sale Offer</b>
                            <b>{self.name}</b> amounting to
                            <b>₹ {formatted_amount}</b>.
                        </p>
                        <p>
                            Status: <span style="color:{status_color}; font-weight:bold;">{offer_status}</span>
                        </p>
                        <p>Please feel free to contact us if you have any questions.</p>
                        <div style="text-align: center; padding: 16px 0px;">
                            <a href="{accept_url}"
                               style="padding: 10px 20px; color: #FFFFFF; text-decoration: none;
                                      background-color: #28A745; border: 1px solid #28A745;
                                      border-radius: 6px; font-size: 14px; margin-right: 10px;">
                                ✅ Accept
                            </a>
                            <a href="{decline_url}"
                               style="padding: 10px 20px; color: #FFFFFF; text-decoration: none;
                                      background-color: #DC3545; border: 1px solid #DC3545;
                                      border-radius: 6px; font-size: 14px;">
                                ❌ Decline
                            </a>
                        </div>
                        <p>Thank you for considering us!</p>
                        <p>Best regards,<br/>{self.user_id.name or 'Sales Team'}</p>
                    """

                # Update the context to use this template
                res['context'].update({
                    'default_template_id': template.id,
                    'default_use_template': True
                })
        return res

    @api.onchange('php')
    def _onchange_php_amount_of_unit(self):
        if self.php < self.property_unit_id.php:
            raise UserError(_("Sorry Sale Price Is Less Than Unit final Sale Value!!."))
        # product_line = self.offer_quote_line_ids.filtered(lambda l: l.product_line)
        # product_line.basic_price = self.php

    def action_client_accept(self):
        self.state = 'accepted'

    def action_client_reject(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Reason',
            'res_model': 'client.rejection.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_sale_id': self.id,
            }
        }

    def action_sale_offer_pdf(self):
        """Trigger the custom report"""
        self.print_reference = self.env['ir.sequence'].next_by_code('sale.offer.print')
        return self.env.ref('property_sales.action_report_sale_offer_pdf').report_action(self)

    def _confirmation_error_message(self):
        self.ensure_one()
        # If state is accepted → skip default check
        if self.state == 'accepted':
            return False
        return super()._confirmation_error_message()

    def action_view_booking_invoice(self):
        return {
            'name': 'Invoices',
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form',
            'res_model': 'account.move',
            'context': "{'move_type':'out_invoice'}",
            'domain': [('sale_id', '=', self.id),('move_type','=','out_invoice')],
            'target': 'current',
        }

    def action_discount_request_view(self):
        return {
            'name': 'Discount Requests',
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form',
            'res_model': 'sale.discount.approval.request',
            'context': "{}",
            'domain': [('sale_order_id', '=', self.id)],
            'target': 'current',
        }

    # def count_installments(start, end, months_gap):
    #     count = 0
    #     current = start
    #     while current <= end:
    #         count += 1
    #         current += relativedelta(months=months_gap)
    #     return count

    def _custom_round(self, amount):
        """
        Round using last-two-digit rule:
        last two digits < 50 → round down
        last two digits ≥ 50 → round up
        """
        integer_part = int(amount)
        last_two = integer_part % 100
        if last_two < 50:
            rounded = integer_part - last_two
        else:
            rounded = integer_part + (100 - last_two)
        return float(rounded)

    def action_clear_lines(self):
        if self.offer_quote_line_ids:
            self.offer_quote_line_ids.unlink()
        if self.payment_plan_summary_ids:
            self.payment_plan_summary_ids.unlink()
        if self.plan_lines_ids:
            self.plan_lines_ids.unlink()
        self.payment_plan_id = False
        self.start_date = False
        self.period_of_installment = False
        self.discount_per = 0.0
        self.discount_based_on =False
        self.discount_approved =False
        self.request_for_approval =False
        self.discount_status =False
        self.discount_approved_percentage =0.0


    def on_generate_lines(self):
        if self.discount_status == 'rejected':
            raise UserError(
                _("Please clear the discount first using clear button  then generate!!"))
        if self.discount_status == 'approved':
            if self.discount_per > self.discount_approved_percentage:
                raise UserError(
                    _("You are trying to modify the approved discount !!"))
        if not self.payment_plan_id:
            raise UserError(
                _("Please Choose A Payment Plan!!."))
        if not self.payment_plan_id.payment_line_ids:
            raise UserError(
                _("Payment Plan Lines Missing In Payment Plan !!."))
        if not self.start_date:
            raise UserError(
                _("Please Choose Start Date !!."))
        if not self.period_of_installment:
            raise UserError(
                _("Please Choose Period Of Installment !!."))
        if self.start_date and self.payment_plan_id.payment_line_ids:
            end_dates = [line.end_date for line in
                         self.payment_plan_id.payment_line_ids if
                         line.end_date]
            if end_dates:
                last_end_date = max(
                    end_dates)
                if self.start_date > last_end_date:
                    raise UserError(
                        _("The Start Date (%s) cannot be after the last payment line end date (%s).") % (
                            self.start_date, last_end_date
                        )
                    )
        if self.property_unit_id:
            temp_id = self.env['product.template'].sudo().search(
                [('sale_property', '=', True)])
            if not temp_id:
                raise UserError(
                    _("Please Configure A Sales Property Product!!."))
            if self.offer_quote_line_ids:
                self.offer_quote_line_ids.unlink()
            self.env['offer.quote.line'].sudo().create({
                'product_id': temp_id.product_variant_id.id,
                'name': 'Basic Price - ' + str(self.property_unit_id.name),
                'basic_price': self.total_amount_unit_price,
                'sale_order': self.id,
                'product_line': True,
            })
            if self.property_project_id.other_fees_line_ids:
                for line in self.property_project_id.other_fees_line_ids:
                    if line.percentage > 0:
                        amount = (self.total_amount_unit_price * line.percentage)/100
                    else:
                        amount = line.fixed_amount
                    self.env['offer.quote.line'].sudo().create({
                        'product_id': line.product_id.id,
                        'name': line.name,
                        'basic_price': amount,
                        'sale_order': self.id,
                    })
        if not self.property_unit_id and self.property_project_id and self.payment_plan_id:
            raise UserError(_("Please Choose A unit!!."))
        if self.payment_plan_summary_ids:
            self.payment_plan_summary_ids.unlink()
        if self.payment_plan_id.payment_line_ids:
            sequence = 1
            for pline in self.payment_plan_id.payment_line_ids:
                self.env['payment.plan.summary'].sudo().create({
                    'name': pline.description,
                    'installment_month': pline.installment_month,
                    'percentage': pline.percentage,
                    'period_covered': pline.period_covered,
                    'start_date': pline.start_date,
                    'end_date': pline.end_date,
                    'sale_order': self.id,
                    'sequence': sequence,
                    'payment_id': self.payment_plan_id.id,
                })
                sequence = sequence + 1
        if self.plan_lines_ids:
            self.plan_lines_ids.unlink()
        unit_price = self.total_amount_unit_price
        so_start = self.start_date
        months_gap = {'monthly': 1, 'quarterly': 3, 'half_year': 6,
                      'yearly': 12}.get(self.period_of_installment, 1)
        lines = []
        total_rounded = 0.0

        for plan_line in self.payment_plan_id.payment_line_ids:
            if plan_line.percentage <= 0:
                raise UserError(
                    _("Payment line %s has invalid percentage.") % plan_line.description)
            if plan_line.period_covered != 'on_booking' and (
                    not plan_line.start_date or not plan_line.end_date):
                raise UserError(
                    _("Payment line %s must have start and end date.") % plan_line.description)
            if plan_line.period_covered == 'on_booking':
                raw = unit_price * plan_line.percentage / 100
                rounded = self._custom_round(raw)
                lines.append((0, 0, {
                    'name': plan_line.description,
                    'payment_id': self.payment_plan_id.id,
                    'percentage': plan_line.percentage,
                    'plan_date': fields.Date.today(),
                    'actual_amount': raw,
                    'rounded_amount': rounded,
                    'in_offer': True,
                }))
                total_rounded += rounded
                continue

            effective_start = max(plan_line.start_date, so_start)
            effective_end = plan_line.end_date

            if effective_start > effective_end:
                raise UserError(
                    _("Payment line %s has start date after end date.") % plan_line.description)
            duration_months = (
                    (effective_end.year - effective_start.year) * 12
                    + (effective_end.month - effective_start.month)
            )
            min_months = {
                'monthly': 1,
                'quarterly': 3,
                'half_year': 6,
                'yearly': 12,
            }.get(self.period_of_installment, 1)

            if duration_months < min_months - 1:
                raise UserError(_(
                    "The selected start date (%s) does not match the chosen payment plan\n\n"
                    "Please choose a proper payment plan or adjust the start date."
                ) % effective_start)

            # Determine number of installments
            count = 0
            temp_date = effective_start
            while temp_date <= effective_end:
                count += 1
                temp_date += relativedelta(months=months_gap)

            if count == 0:
                raise UserError(
                    _("Payment line %s has zero installments for given dates.") % plan_line.description)

            per_inst_pct = plan_line.percentage / count
            current_date = effective_start

            for i in range(count):
                raw = unit_price * per_inst_pct / 100
                rounded = self._custom_round(raw)
                lines.append((0, 0, {
                    'name': plan_line.description,
                    'payment_id': self.payment_plan_id.id,
                    'percentage': per_inst_pct,
                    'plan_date': current_date,
                    'actual_amount': raw,
                    'rounded_amount': rounded,
                }))
                total_rounded += rounded
                current_date += relativedelta(months=months_gap)

        # Adjust last line to match total sale price
        diff = unit_price - total_rounded
        if diff != 0 and lines:
            lines[-1][2]['rounded_amount'] += diff

        self.plan_lines_ids = lines
        line_count =1
        for line in self.plan_lines_ids.sorted(key=lambda l: l.id):
            line.name = 'installment ' + str(line_count)
            line_count = line_count +1
        self.generate_line = True

    def action_export_plan_lines(self):
        if not self.generate_line:
            raise UserError(_("Please Generate Payment Lines First!!."))
        self.ensure_one()
        wb = Workbook()
        ws = wb.active
        ws.title = "Payment Plan Lines"
        ws.append(['Name', 'Date(YYYY-MM-DD)', 'Percentage'])
        if self.plan_lines_ids:
            for line in self.plan_lines_ids.sorted(key=lambda l: l.id):
                ws.append([
                    line.name or '',
                    line.plan_date,
                    line.percentage or 0.0
                ])

        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        attachment = self.env['ir.attachment'].create({
            'name': 'payment_plan_lines.xlsx',
            'type': 'binary',
            'datas': base64.b64encode(buffer.read()),
            'res_model': 'sale.order',
            'res_id': self.id,
        })
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }

    def action_import_plan_lines(self):
        if not self.generate_line:
            raise UserError(_("Please Generate Payment Lines First!!."))
        return {
            'name': 'Import Payment Plans',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            "view_type": "form",
            'res_model': 'import.payment.plan.lines',
            'target': 'new',
            'context': {
                'active_id': self.id,
            }
        }

    def action_verify_lines(self):
        if self.discount_approval_need ==True:
            if self.discount_approved == False:
                raise UserError(_("Sorry Please Take Discount Approval From Manager!!."))
        if self.discount_status == 'rejected':
            raise UserError(
                _("Please Click The CLear Button Clear The Discount And Generate LInes Again!!."))
        if not self.offer_quote_line_ids:
            raise UserError(
                _("Please Add The Offer Line!!."))
        invoice_line = self.plan_lines_ids.filtered(
            lambda l: l.in_offer)
        if not invoice_line:
            raise UserError(
                _("Please Mark In Booking Lines In Payment Lines!!."))
        product_line = self.offer_quote_line_ids.filtered(
            lambda l: l.product_line)
        if not product_line:
            raise UserError(
                _("Please Add the Sale Product on Offer line!!."))
        product_line = product_line[0]
        self.env['sale.order.line'].sudo().create({
            'order_id':self.id,
            'product_id':product_line.product_id.id,
            'name':product_line.name,
            'price_unit':product_line.discounted_amount,
            'product_uom_qty':1
        })
        self.verify_line = True

    def action_edit_lines_offer(self):
        self.ensure_one()
        if not self.generate_line:
            raise UserError(_("Please Generate Payment Lines First!!."))
        sales_amount = 0.0
        product_line = self.offer_quote_line_ids.filtered(
            lambda l: l.product_line)
        if product_line:
            product_line = product_line[0]
            sales_amount = product_line.discounted_amount
        return {
            'type': 'ir.actions.act_window',
            'name': 'Edit Payment Schedule',
            'res_model': 'offer.payment.update.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_sale_order': self.id,
                'default_final_total_property_value': sales_amount,
            }
        }

    def action_confirm(self):
        if self.property_type == 'broker' and not self.verify_line:
            raise UserError(
                _("Verify The offer First Then Confirm!!."))
        if self.offer_quote_line_ids:
            order_lines = []
            invoice_line = self.plan_lines_ids.filtered(
                lambda l: l.in_offer)
            if invoice_line:
               amount =  sum(invoice_line.mapped('rounded_amount'))
               sale_line = self.offer_quote_line_ids.filtered(
                   lambda l: l.product_line)
               sale_line = sale_line[0]
               name = "Property Offer Booking Payment of - "+str(self.property_project_id.name)+" - " +str(self.property_unit_id.name)
               order_lines.append((0, 0, {
                   'product_id': sale_line.product_id.id,
                   'name': name,
                   'quantity': 1,
                   'price_unit': amount,
                   'analytic_distribution': {
                       self.property_unit_id.analytic_account_id.id: 100,
                   },
               }))
               product_line = self.offer_quote_line_ids.filtered(
                   lambda l: not l.product_line)
               if product_line:
                   for line in product_line:
                       order_lines.append((0, 0, {
                           'product_id': line.product_id.id,
                           'name': line.name,
                           'quantity': 1,
                           'price_unit': line.discounted_amount,
                           'analytic_distribution': {
                               self.property_unit_id.analytic_account_id.id: 100,
                           },
                       }))
               invoice = self.env['account.move'].sudo().create({
                   'move_type': 'out_invoice',
                   'property_type': 'sale',
                   'partner_id': self.partner_id.id,
                   'invoice_origin': self.name,
                   'invoice_line_ids': order_lines,
                   'property_project_id': self.property_project_id.id,
                   'property_unit_id': self.property_unit_id.id,
                   'sale_id': self.id,
               })
               for in_line in invoice_line:
                   in_line.invoice_id = invoice.id
                   in_line.inv_created = True
            else:
                raise UserError(_("Please Mark In Booking Lines In Payment Lines!!."))
        else:
            raise UserError(_("Offer Line Is Missing Generate It!!."))
        return super(SaleOrder, self).action_confirm()

    def action_sale_property_reservation(self):
        block_request = self.env['blocking.request'].search(
            [('sale_order', '=', self.id), ('status', '=', 'draft')])
        if block_request:
            raise UserError(_('Already Have A Pending Request !!'))
        if not self.property_type == 'broker':
            raise UserError(_('Please choose selling type property !!'))
        else:
            if not self.property_project_id:
                raise UserError(_('Please choose a Property Project!!'))
            if not self.property_unit_id:
                raise UserError(
                    _('Please Choose A Property Unit !!'))
            return {
                'name': _('Property Blocking'),
                'type': 'ir.actions.act_window',
                'res_model': 'property.blocking.request',
                'view_mode': 'form',
                "view_type": "form",
                'target': 'new',
                'context': {
                    'active_id': self.id,
                    'default_crm_id': self.crm_lead_id.id,
                    'default_sale_order': self.id,
                    'default_property_project_id': self.property_project_id.id,
                    'default_property_unit_id': self.property_unit_id.id,
                    'default_user_id': self.user_id.id,
                    'default_partner_id': self.partner_id.id,
                }

            }

    @api.constrains('plan_lines_ids', 'plan_lines_ids.percentage')
    def _check_total_plan_percentage(self):
        for order in self:
            total_percentage = sum(
                order.plan_lines_ids.mapped('percentage')
            )
            if order.plan_lines_ids and round(total_percentage, 2) != 100.0:
                raise UserError(_(
                    "The total Payment Plan percentage must be 100%%.\n"
                    "Current total: %.2f%%"
                ) % total_percentage)

    def action_book_offer(self):
        if self.property_unit_id.status not in  ['available']:
            raise UserError(
                _('Property is not available now !!'))
        amount = 0.0
        other_gov_line_ids = []
        payment_schedule_ids = []
        property_buyer_ids = []
        product_line = self.offer_quote_line_ids.filtered(
            lambda l: l.product_line)
        if product_line:
            product_line = product_line[0]
            amount = product_line.discounted_amount
        if self.offer_quote_line_ids:
            product_line = self.offer_quote_line_ids.filtered(
                lambda l: not l.product_line)
            if product_line:
                for line in product_line:
                    other_gov_line_ids.append((0, 0, {
                        'name': line.name,
                        'amount': line.discounted_amount,
                    }))
        if self.plan_lines_ids:
            for line in self.plan_lines_ids.sorted(key=lambda l: l.plan_date or fields.Date.today()):
                payment_schedule_ids.append((0, 0, {
                    'name': line.name,
                    'payment_id': line.payment_id.id,
                    'buyer_id': self.partner_id.id,
                    'percentage': line.percentage,
                    'property_project_id': self.property_project_id.id,
                    'property_unit_id':self.property_unit_id.id,
                    'sale_order': self.id,
                    'offer_id': self.id,
                    'plan_date': line.plan_date if line.plan_date else False,
                    'amount': line.amount,
                    'rounded_amount': line.rounded_amount,
                    'invoice_id': line.invoice_id.id if line.invoice_id else False,
                    'inv_created':line.inv_created,
                    'is_booking':line.in_offer,
                }))
        property_buyer_ids.append(
            (0, 0, {
                'buyer_id':self.partner_id.id,
                'owner_share':100.0,
                'relationship':'self',
            })
        )
        booking =self.env['offer.booking'].create({
            'user_id':self.user_id.id,
            'sale_id':self.id,
            'partner_id':self.partner_id.id,
            'crm_id':self.crm_lead_id.id,
            'property_project_id':self.property_project_id.id,
            'property_unit_id':self.property_unit_id.id,
            'payment_plan_id':self.payment_plan_id.id,
            'lead_agent_id':self.lead_agent_id.id,
            'final_sale_value':self.amount_total,
            'final_total_property_value':amount,
            'payment_schedule_ids':payment_schedule_ids,
            'property_buyer_ids':property_buyer_ids,
            'other_gov_line_ids':other_gov_line_ids,
            'company_id': self.company_id.id if self.company_id else self.env.company.id,
        })
        self.booking_id = booking.id
        booking.generate_line = True
        invoice_line = self.plan_lines_ids.filtered(
            lambda l: l.in_offer)
        for line in invoice_line:
            booking.invoice_id = line.invoice_id.sudo().id
        self.booking = True
        return {
            'name': 'Bookings',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'offer.booking',
            'res_id': booking.id,
            'target': 'current',
        }


    # def action_eoi_offer(self):
    #     eoi =self.env['expression.interest'].sudo().create({
    #         'offer_id':self.id,
    #         'lead':self.crm_lead_id.id,
    #         'project':self.property_project_id.id,
    #         'owner':self.partner_id.id,
    #     })
    #     self.eoi = True
    #     self.eoi_id = eoi.id
    #     return {
    #         'name': 'EOI',
    #         'type': 'ir.actions.act_window',
    #         'view_mode': 'form',
    #         'res_model': 'expression.interest',
    #         'res_id': eoi.id,
    #         'target': 'current',
    #     }

class PaymentPlanSummary(models.Model):
    _name = 'payment.plan.summary'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _description = 'Payment Plan Summary'
    _order = 'sequence desc'

    sequence = fields.Integer(
        string="Sequence"
    )

    sale_order = fields.Many2one(
        'sale.order',
        string="sale Order"
    )

    name = fields.Char(
        string="Milestone"
    )

    installment_month = fields.Integer(
        string="Installments month",
        tracking=True
    )

    percentage = fields.Float(
        string="Percentage(%)",
        tracking=True
    )

    payment_id = fields.Many2one(
        'property.payment.plan',
        string="Payment"
    )

    period_covered = fields.Selection([
        ('on_booking', 'On Booking'),
        ('before', 'Before Completion'),
        ('after', 'After Completion')],
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

    amount = fields.Float(
        string="Amount",
        compute='_compute_total_amount'
    )

    @api.depends('percentage', 'sale_order')
    def _compute_total_amount(self):
        for rec in self:
            rec.amount = 0.0
            if rec.sale_order.offer_quote_line_ids:
                product_line = rec.sale_order.offer_quote_line_ids.filtered(
                    lambda l: l.product_line)
                if product_line:
                    product_line = product_line[0]
                    amount = (product_line.discounted_amount * rec.percentage) / 100
                    rec.amount = amount


class PaymentPlanLineOffer(models.Model):
    _name = 'payment.plan.offer.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _description = 'Payment Plan Lines'
    _order = 'sequence desc'

    sequence = fields.Integer(
        string="Sequence"
    )
    in_offer = fields.Boolean(
        string="In Booking",
        default=False
    )

    sale_order = fields.Many2one(
        'sale.order',
        string="sale Order"
    )

    name = fields.Char(
        string="Name"
    )

    plan_date = fields.Date(
        string="Date (YYYY-MM-DD)"
    )

    payment_id = fields.Many2one(
        'property.payment.plan',
        string="Payment"
    )

    percentage = fields.Float(
        string="Percentage(%)"
    )

    amount = fields.Float(
        string="Amount",
        compute='_compute_total_amount'
    )

    actual_amount = fields.Float(
        string="Actual Amount"
    )

    rounded_amount = fields.Float(
        string="Rounded Amount",
    )

    invoice_id = fields.Many2one(
        'account.move',
        string="Invoice"
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='invoice_id.currency_id'
    )
    inv_status = fields.Selection(
        related='invoice_id.state',
        string="Invoice Status"
    )
    pay_status = fields.Selection(
        related='invoice_id.payment_state',
        string="Payment Status"
    )
    amount_residual = fields.Monetary(
        string="Amount Due",
        related='invoice_id.amount_residual',
        currency_field='currency_id',
    )

    inv_created = fields.Boolean(
        string="Invoice Created",
        default=False
    )

    @api.depends('percentage','amount')
    def _compute_total_amount(self):
        for rec in self:
            rec.amount = 0.0
            if rec.sale_order.offer_quote_line_ids:
                product_line = rec.sale_order.offer_quote_line_ids.filtered(lambda l: l.product_line)
                if product_line:
                    product_line = product_line[0]
                    amount = (product_line.discounted_amount * rec.percentage)/100
                    rec.amount = amount

    def unlink(self):
        for record in self:
            if record.inv_created:
                raise UserError(
                    _("You Can't delete payment lines already invoiced !!"))
            return super(PaymentPlanLineOffer, self).unlink()

    @api.depends('actual_amount','amount','percentage')
    def _compute_rounded_amount(self):
        """
        Rounds the actual_amount using the rule:
        last two digits < 50 → round down
        last two digits ≥ 50 → round up
        """
        for rec in self:
            if rec.amount:
                last_line = rec.sale_order.plan_lines_ids.sorted(
                    lambda l: (l.plan_date or fields.Date.today()),
                )[-1]
                if last_line and rec.id == last_line.id:
                    if rec.sale_order.offer_quote_line_ids:
                        product_line = rec.sale_order.offer_quote_line_ids.filtered(
                            lambda l: l.product_line)
                        if product_line:
                            product_line = product_line[0]
                            sales_amount = product_line.discounted_amount
                            other_lines = rec.sale_order.plan_lines_ids.filtered(
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
                                rounded = integer_part + (
                                            100 - last_two_digits)

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
                    integer_part = int(rec.amount)
                    last_two_digits = integer_part % 100
                    if last_two_digits < 50:
                        rounded = integer_part - last_two_digits
                    else:
                        rounded = integer_part + (100 - last_two_digits)

                    rec.rounded_amount = float(rounded)
            else:
                rec.rounded_amount = 0.0


class OfferQuoteLine(models.Model):
    _name = 'offer.quote.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _description = 'Offer Quote Lines'
    _order = 'sequence desc'

    sequence = fields.Integer(
        string="Sequence"
    )
    product_id = fields.Many2one(
        'product.product',
        string="Name",
        domain=['|',('other_fee_property', '=', True),('sale_property', '=', True)]
    )
    name = fields.Char(
        string="Name",
    )
    basic_price = fields.Float(
        string="Basic Price",
        default=0.0

    )
    sale_order = fields.Many2one(
        'sale.order',
        string="sale Order"
    )

    discount = fields.Float(
        string="Special Discount (%)",
        default=0.0
    )

    discounted_amount = fields.Float(
        string="Total Amount",
        default=0.0,
        compute='_compute_total_amount'
    )

    product_line = fields.Boolean(
        string="Product Line",
        default=False
    )
    @api.depends('basic_price', 'discount')
    def _compute_total_amount(self):
        for rec in self:
            rec.discounted_amount = rec.basic_price
            if rec.discount > 0 and rec.basic_price > 0:
                discounted_amount = (rec.basic_price * rec.discount) / 100
                rec.discounted_amount = (rec.basic_price - discounted_amount)


    # def unlink(self):
    #     for record in self:
    #         if record.product_line:
    #             raise UserError(_("You Can Not Have The Access To Delete The Line !!"))
    #         return super(OfferQuoteLine, self).unlink()

    @api.constrains('product_id', 'sale_order')
    def _check_duplicate_product(self):
        for rec in self:
            if not rec.product_id or not rec.sale_order:
                continue

            domain = [
                ('sale_order', '=', rec.sale_order.id),
                ('product_id', '=', rec.product_id.id),
                ('id', '!=', rec.id),
            ]
            if self.search_count(domain):
                raise UserError(
                    _("The product '%s' is already added in this Sale Order.")
                    % rec.product_id.display_name
                )


