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
import uuid
import base64
from io import BytesIO
from odoo import fields, models, _, api
from odoo.exceptions import UserError
from openpyxl import Workbook




class OfferBooking(models.Model):
    _name = 'offer.booking'
    _inherit = ['mail.thread','mail.activity.mixin']
    _rec_name = 'sequence'
    _description = 'Booking'
    _order = 'id desc'

    sequence = fields.Char(
        string="Sequence",
    )

    date_booking = fields.Date(
        sting="Date",
        tracking=True,
        default=fields.Date.today
    )

    due_date = fields.Date(
        sting="Due Date",
        tracking=True,
    )
    user_id = fields.Many2one(
        'res.users',
        string="Sales Person",
        default=lambda self: self.env.user,
    )


    status = fields.Selection([
        ('draft', 'Draft'),
        ('dp_paid', 'DP Paid'),
        ('agreement_send', 'Agreement Send'),
        ('agreement_signed', 'Agreement Signed'),
        ('kyc_competed', 'KYC Completed'),
        ('on_hold', 'On Hold'),
        ('cancel', 'Cancelled')
    ],
        string="Status",
        default='draft',
        tracking=True,
    )


    company_id = fields.Many2one(
        'res.company',
        string="Company",
        tracking=True,
        default=lambda self: self.env.company.id
    )

    company_arabic = fields.Char(
        string="Company Arabic",
        related='company_id.name_arabic'
    )

    currency_id = fields.Many2one(
        'res.currency',
        string="Currency",
        tracking=True,
        default=lambda self: self.env.company.currency_id,
    )

    property_project_id = fields.Many2one(
        'property.project',
        string="Project",
        tracking=True
    )

    project_name_arabic = fields.Char(
        string="Project Name Ar(إســم الـمشروع)",
        tracking=True,
        related='property_project_id.project_name_arabic'

    )

    property_unit_id = fields.Many2one(
        'property.unit',
        string="Unit",
        tracking=True,
        domain='[("project_id", "=", property_project_id),'
               '("status","=","available")]',
    )

    net_area = fields.Float(
        string="Total Area (Sqft)",
        tracking=True,
        related='property_unit_id.total_size'
    )

    type_id = fields.Many2one(
        'property.unit.type',
        string="Unit Type",
        tracking=True,
        related='property_unit_id.type_id'
    )

    php = fields.Monetary(
        string="Unit Sale Price",
        tracking=True,
        currency_field='currency_id',
        related='property_unit_id.php'
    )

    booking_cost = fields.Float(
        string="Booking Cost",
        tracking=True,
    )

    allowed_payment_plan_ids = fields.Many2many(
        'property.payment.plan',
        compute='_compute_allowed_payment_plan_ids',
        readonly=True,
    )

    payment_plan_id = fields.Many2one(
        'property.payment.plan',
        string="Payment Plan",
        domain='[("id", "in", allowed_payment_plan_ids)]',
        tracking=True,
    )

    terms_and_condition = fields.Html(
        string="Terms And Conditions"
    )

    terms_and_condition_arabic = fields.Html(
        string="Terms And Conditions Arabic"
    )

    property_buyer_ids = fields.One2many(
        'property.buyer.detail',
        'offer_id',
        string="Buyer Lines"
    )
    payment_schedule_ids = fields.One2many(
        'payment.schedule.line',
        'offer_id',
        string="Payment Schedule Lines"
    )

    other_gov_line_ids = fields.One2many(
        'payment.other.charges',
        'offer_id',
        string="Other Gov Charges"
    )

    sale_id = fields.Many2one(
        'sale.order',
        string="Offer",
        domain='[("state", "=","sale")]',
        tracking=True,
    )

    # eoi_id = fields.Many2one(
    #     'expression.interest',
    #     string="EOI",
    # )

    crm_id = fields.Many2one(
        'crm.lead',
        string="Crm",
        tracking=True,
    )
    final_sale_value  = fields.Float(
        string="Final Sale Total Value",
        tracking=True,
    )
    final_total_property_value = fields.Float(
        string="Final Property Sale Value",
        tracking=True,
    )

    lead_agent_id = fields.Many2one(
        'res.partner',
        string="Agent",
        domain="[('par_type', '=', 'agent')]",
        tracking=True,
    )

    sales_approved = fields.Boolean(
        string="Sales Approved",
        default=False,
        tracking=True,
    )
    finance_approved = fields.Boolean(
        string="Finance Approved",
        default=False,
        tracking=True,
    )
    general_approved = fields.Boolean(
        string="General Manager Approved",
        default=False,
        tracking=True,
    )

    sales_approved_type = fields.Selection([
        ('waiting','Waiting'),
        ('approved','Approved')
    ],
        string='Sales Approval Status',
        tracking=True,

    )

    finance_approved_type = fields.Selection([
        ('waiting', 'Waiting'),
        ('approved', 'Approved')
    ],
        string='Finance Approval Status',
        tracking=True,
    )

    general_approved_type = fields.Selection([
        ('waiting', 'Waiting'),
        ('approved', 'Approved')
    ],
        string='General Manager Approval Status',
        tracking=True,

    )

    total_rounded_amount = fields.Monetary(
        string="Total Amount",
        compute="_compute_total_rounded_amount",
        currency_field='currency_id',
        store=True
    )

    days_since_booking = fields.Integer(
        string="Days Since Booking",
        compute="_compute_days_since_booking",
        store=True
    )

    days_since_booking_text = fields.Text(
        string="Due Date",
        compute="_compute_days_since_booking",
        store=True
    )

    kyc_warning_level = fields.Selection([
        ('none', 'None'),
        ('warning', '25 Days Warning'),
        ('critical', '60 Days Critical')
    ],
        compute="_compute_days_since_booking",
        string="KYC Warning"
    )

    # eoi_ids = fields.One2many(
    #     'expression.interest',
    #     'booking_id',
    #     string="EOIs"
    # )

    # spa_ids = fields.One2many(
    #     'spa.book',
    #     'offer_booking',
    #     string="SPAs"
    # )

    # oqood_ids = fields.One2many(
    #     'oqood.registration',
    #     'offer_booking',
    #     string="Oqoods"
    # )
    #
    # snagging_ids = fields.One2many(
    #     'snagging.unit',
    #     'offer_booking',
    #     string="snaggings"
    # )
    #
    # key_handover_ids = fields.One2many(
    #     'key.handover',
    #     'offer_booking',
    #     string="key handovers"
    # )

    partner_id = fields.Many2one(
        'res.partner',
        string="Buyer",
        domain="[('par_type', '=', 'lead')]",
    )

    generate_line = fields.Boolean(
        string="Generate Line",
        default=False
    )

    oqood_paid = fields.Selection([
        ('yes','Yes'),
        ('no','NO')],
        string="Oqood Paid",
        default='no'
    )

    dld_paid = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'NO')],
        string="DLD Paid",
        default='no'
    )

    invoice_id = fields.Many2one(
        'account.move',
        string="Invoice"
    )

    dp_status_text = fields.Char(
        compute="_compute_dp_status",
        string="Down Payment Status"
    )

    dp_completed = fields.Boolean(
        compute="_compute_dp_status",
        store=True
    )

    @api.depends('date_booking', 'status','due_date')
    def _compute_days_since_booking(self):
        today = fields.Date.today()
        for rec in self:
            if rec.date_booking:
                rec.days_since_booking = (today - rec.date_booking).days
            else:
                rec.days_since_booking = 0
            if rec.due_date:
                delta_days = (rec.due_date - today).days
                if rec.status == 'kyc_competed':
                    rec.days_since_booking_text = 'Booking KYC Completed'
                elif rec.status == 'cancel':
                    rec.days_since_booking_text = 'Booking Cancelled'
                else:
                    if delta_days > 0:
                        rec.days_since_booking_text = "Within " + str(delta_days) + " Days"
                    else:
                        rec.days_since_booking_text = "Booking Is Delayed in  " + str(
                            delta_days) + " Days"
            else:
                rec.days_since_booking_text = "No booking due date"
            if rec.status == 'kyc_competed':
                rec.kyc_warning_level = 'none'
            elif rec.days_since_booking >= 60:
                rec.kyc_warning_level = 'critical'
            elif rec.days_since_booking >= 25:
                rec.kyc_warning_level = 'warning'
            else:
                rec.kyc_warning_level = 'none'

    @api.depends('payment_schedule_ids',
                 'payment_schedule_ids.rounded_amount')
    def _compute_total_rounded_amount(self):
        for rec in self:
            rec.total_rounded_amount = sum(
                rec.payment_schedule_ids.mapped('rounded_amount')
            )

    @api.onchange('sale_id')
    def onchange_sale_order(self):
        if self.sale_id and self.sale_id.property_project_id:
            self.property_project_id = self.sale_id.property_project_id.id
        if self.sale_id.property_unit_id:
            self.property_unit_id = self.sale_id.property_unit_id.id
        if self.sale_id.payment_plan_id:
            self.payment_plan_id =  self.sale_id.payment_plan_id.id
        if self.sale_id.amount_total:
            self.final_sale_value = self.sale_id.amount_total
        if self.sale_id.offer_quote_line_ids:
            product_line = self.sale_id.offer_quote_line_ids.filtered(
                lambda l: l.product_line)
            if product_line:
                product_line = product_line[0]
                amount = product_line.discounted_amount
            self.final_total_property_value = amount
        if self.sale_id.user_id:
            self.user_id = self.sale_id.user_id.id
        if self.sale_id.lead_agent_id:
            self.lead_agent_id = self.sale_id.lead_agent_id.id
        if self.sale_id.partner_id:
            self.partner_id = self.sale_id.partner_id.id

    @api.depends('property_project_id')
    def _compute_allowed_payment_plan_ids(self):
        for rec in self:
            if rec.property_project_id:
                payment_plan = self.env['property.payment.plan'].search(
                    [('property_project_id', '=', rec.property_project_id.id)])
                if payment_plan:
                    rec.allowed_payment_plan_ids = payment_plan.ids
                else:
                    rec.allowed_payment_plan_ids = False
            else:
                rec.allowed_payment_plan_ids = False

    @api.model
    def create(self, vals):
        res = super(OfferBooking, self).create(vals)
        seq = self.env['ir.sequence'].next_by_code('property.booking.sequence')
        res.sequence = seq
        return res

    @api.constrains('payment_schedule_ids', 'payment_schedule_ids.percentage')
    def _check_total_plan_offer_percentage(self):
        for order in self:
            total_percentage = sum(
                order.payment_schedule_ids.mapped('percentage')
            )
            if order.payment_schedule_ids and round(total_percentage, 2) != 100.0:
                raise UserError(_(
                    "The total Payment Plan percentage must be 100%%.\n"
                    "Current total: %.2f%%"
                ) % total_percentage)

    @api.depends(
        'invoice_id.amount_total',
        'invoice_id.amount_residual',
        'invoice_id.state'
    )
    def _compute_dp_status(self):
        for rec in self:
            if rec.invoice_id and rec.invoice_id.state == 'posted':
                total = rec.invoice_id.amount_total
                paid = total - rec.invoice_id.amount_residual
                rec.dp_status_text = f"{paid:,.2f} / {total:,.2f}"
                if rec.invoice_id.amount_residual == 0:
                    rec.dp_completed = True
                    rec.dp_status_text = f"{paid:,.2f} / {total:,.2f}" +" "+ str("✅")
                else:
                    rec.dp_completed = False
            else:
                total = rec.invoice_id.amount_total
                paid = 0.0
                rec.dp_status_text = f"{paid:,.2f} / {total:,.2f}"
                rec.dp_completed = False

    def action_generate_payment_lines(self):
        if self.sale_id.plan_lines_ids:
            self.payment_schedule_ids.unlink()
            for line in self.sale_id.plan_lines_ids:
                self.env['payment.schedule.line'].sudo().create({
                    'name': line.name,
                    'payment_id': line.payment_id.id,
                    'buyer_id': self.partner_id.id,
                    'percentage': line.percentage,
                    'property_project_id': line.sale_order.property_project_id.id,
                    'property_unit_id': line.sale_order.property_unit_id.id,
                    'sale_order': line.sale_order.id,
                    'offer_id': self.id,
                    'plan_date': line.plan_date if line.plan_date else False,
                    'amount': line.amount,
                    'invoice_id': line.invoice_id.id,
                    'inv_created': True if line.invoice_id else False,
                })
        if self.sale_id.offer_quote_line_ids:
            product_line = self.sale_id.offer_quote_line_ids.filtered(
                lambda l: not l.product_line)
            if product_line:
                self.other_gov_line_ids.unlink()
                for line in product_line:
                    self.env['payment.other.charges'].sudo().create({
                        'name': line.name,
                        'offer_id': self.id,
                        'amount': line.discounted_amount,
                    })
        self.generate_line = True

    def cron_kyc_25_days_warning(self):
        records = self.search([
            ('status', 'not in', ['kyc_competed','on_hold','cancel']),
            ('days_since_booking', '=', 25),
        ])
        for rec in records:
            if rec.user_id and rec.user_id.email:
                base_url = self.env[
                    'ir.config_parameter'].sudo().get_param(
                    'web.base.url')
                record_url = f"{base_url}/web#id={rec.id}&model={rec._name}&view_type=form"
                body_html = f"""
                                    <p>Dear {rec.user_id.name},</p>
                                    <p><strong>Urgent Attention Required</strong></p>
                                      <p>
                                         KYC has not been completed for booking<strong>${rec.sequence}</strong> even after 25 days.
                                        </p>
                                      <p>
                                      Please resolve immediately.
                                      </p>
                                      <p>
                                           <a href="{record_url}"
                                              style="
                                                  background-color:#0a6ebd;
                                                  color:#ffffff;
                                                  padding:8px 14px;
                                                  text-decoration:none;
                                                  border-radius:4px;
                                                  display:inline-block;
                                              ">
                                              View Booking
                                           </a>
                                       </p>
                                       <p>
                                           Best regards,<br/>
                                           {self.env.user.name}
                                       </p>
                                """
                subject = _(
                    'URGENT: Booking %s Is Not Completed Yet') % (
                              rec.sequence)
                main_content = {
                    'subject': subject,
                    'author_id': self.env.user.partner_id.id,
                    'body_html': body_html,
                    'email_to': rec.user_id.partner_id.email,
                }
                self.env['mail.mail'].sudo().create(main_content).send()

    def cron_kyc_60_days_escalation(self):
        records = self.search([
            ('status', 'not in', ['kyc_competed','on_hold','cancel']),
            ('days_since_booking', '=', 60),
        ])
        for rec in records:
            if rec.user_id and rec.user_id.email:
                base_url = self.env[
                    'ir.config_parameter'].sudo().get_param(
                    'web.base.url')
                record_url = f"{base_url}/web#id={rec.id}&model={rec._name}&view_type=form"
                body_html = f"""
                                    <p>Dear {rec.user_id.name},</p>
                                    <p><strong>Urgent Attention Required</strong></p>
                                      <p>
                                         KYC has not been completed for booking<strong>${rec.sequence}</strong> even after 60 days.
                                        </p>
                                      <p>
                                      Please resolve immediately.
                                      </p>
                                      <p>
                                           <a href="{record_url}"
                                              style="
                                                  background-color:#0a6ebd;
                                                  color:#ffffff;
                                                  padding:8px 14px;
                                                  text-decoration:none;
                                                  border-radius:4px;
                                                  display:inline-block;
                                              ">
                                              View Booking
                                           </a>
                                       </p>
                                       <p>
                                           Best regards,<br/>
                                           {self.env.user.name}
                                       </p>
                                """
                subject = _(
                    'URGENT: Booking %s Is Not Completed Yet') % (
                              rec.sequence)
                main_content = {
                    'subject': subject,
                    'author_id': self.env.user.partner_id.id,
                    'body_html': body_html,
                    'email_to': rec.user_id.partner_id.email,
                }
                self.env['mail.mail'].sudo().create(main_content).send()


    def action_sales_manager_approval(self):
        if not self.user_id.partner_id.email:
            raise UserError(_("Please Configure Sales Person Email!!"))
        self.sales_approved = True
        self.sales_approved_type = 'approved'
        self.finance_approved_type = 'waiting'
        self.message_post(
            body=_(
                "The Sales Manager has approved this booking. \n"
                "Approved by: %s \n"
            ) % (
                     self.env.user.name,
                 ),
        )

        groups = [
            'property_sales.group_booking_finance_approval',
        ]
        users = self.env['res.users'].sudo().search([
            ('group_ids', 'in', [
                self.env.ref(group).id for group in groups
            ])
        ])
        for user in users:
            if user.partner_id.email:
                base_url = self.env['ir.config_parameter'].sudo().get_param(
                    'web.base.url')
                record_url = f"{base_url}/web#id={self.id}&model={self._name}&view_type=form"
                body_html = f"""
                                    <p>Dear {user.name},</p>
                                   <p>
                                      This is to inform you that the booking has been reviewed and approved by the Sales Manager, and the KYC process has been successfully completed.
                                   </p>
                                      Kindly review the booking details and proceed with the approval at your earliest convenience.
                                      <p>
                                        Please let us know if any additional documents or clarification are required from our side.
                                        </p>
                                      <p>
                                       Thank you for your support.
                                      </p>
                                      <p>
                                           <a href="{record_url}"
                                              style="
                                                  background-color:#0a6ebd;
                                                  color:#ffffff;
                                                  padding:8px 14px;
                                                  text-decoration:none;
                                                  border-radius:4px;
                                                  display:inline-block;
                                              ">
                                              View Booking
                                           </a>
                                       </p>
                                       <p>
                                           Best regards,<br/>
                                           {self.env.user.name}
                                       </p>
                                """
                subject = _(
                    'Booking %s Approved by Sales – Finance Approval Required') % (
                              self.sequence)
                main_content = {
                    'subject': subject,
                    'author_id': self.env.user.partner_id.id,
                    'body_html': body_html,
                    'email_to': user.partner_id.email,
                    'email_cc': self.user_id.partner_id.email,
                }
                self.env['mail.mail'].sudo().create(main_content).send()

    def action_finance_approval(self):
        self.finance_approved = True
        self.finance_approved_type = 'approved'
        self.general_approved_type = 'waiting'
        self.message_post(
            body=_(
                "The Finance Manager has approved this booking\n "
                "Approved by: %s \n"
            ) % (
                     self.env.user.name,
                 ),
        )
        groups = [
            'property_sales.group_booking_general_approval',
        ]
        users = self.env['res.users'].sudo().search([
            ('group_ids', 'in', [
                self.env.ref(group).id for group in groups
            ])
        ])
        for user in users:
            if user.partner_id.email:
                base_url = self.env['ir.config_parameter'].sudo().get_param(
                    'web.base.url')
                record_url = f"{base_url}/web#id={self.id}&model={self._name}&view_type=form"
                body_html = f"""
                                            <p>Dear {user.name},</p>
                                           <p>
                                              We would like to inform you that the booking has been reviewed and approved by the Finance team,and all required validations have been completed.
                                           </p>
                                              Kindly review the booking details and proceed with the final approval at your earliest convenience.
                                              <p>
                                                Please let us know if any additional information or clarification is required.
                                                </p>
                                              <p>
                                               Thank you for your support.
                                              </p>
                                              <p>
                                                   <a href="{record_url}"
                                                      style="
                                                          background-color:#0a6ebd;
                                                          color:#ffffff;
                                                          padding:8px 14px;
                                                          text-decoration:none;
                                                          border-radius:4px;
                                                          display:inline-block;
                                                      ">
                                                      View Booking
                                                   </a>
                                               </p>
                                               <p>
                                                   Best regards,<br/>
                                                   {self.env.user.name}
                                               </p>
                                        """
                subject = _(
                    'Booking %s Approved by Finance – General Manager Approval Required') % (
                              self.sequence)
                main_content = {
                    'subject': subject,
                    'author_id': self.env.user.partner_id.id,
                    'body_html': body_html,
                    'email_to': user.partner_id.email,
                    'email_cc': self.user_id.partner_id.email,
                }
                self.env['mail.mail'].sudo().create(main_content).send()

    def action_general_approval(self):
        self.general_approved = True
        self.general_approved_type = 'approved'
        self.message_post(
            body=_(
                "The General Manager has approved this booking \n"
                "Approved by: %s  \n"
            ) % (
                     self.env.user.name,
                 ),
        )
        if self.user_id.partner_id.email:
            base_url = self.env['ir.config_parameter'].sudo().get_param(
                'web.base.url')
            record_url = f"{base_url}/web#id={self.id}&model={self._name}&view_type=form"
            body_html = f"""
                                     <p>Dear {self.user_id.name},</p>
                                       <p>
                                       We are pleased to inform you that the booking has successfully completed all required approvals, including Sales Manager, Finance, and General Manager.
                                       </p>
                                          The booking is now fully approved and ready for further processing.
                                          <p>
                                           Thank you for your efforts in managing this booking.
                                            </p>
                                          <p>
                                               <a href="{record_url}"
                                                  style="
                                                      background-color:#0a6ebd;
                                                      color:#ffffff;
                                                      padding:8px 14px;
                                                      text-decoration:none;
                                                      border-radius:4px;
                                                      display:inline-block;
                                                  ">
                                                  View Booking
                                               </a>
                                           </p>
                                           <p>
                                               Best regards,<br/>
                                               {self.env.user.name}
                                           </p>
                                """
            subject = _(
                'Booking %s Fully Approved') % (
                          self.sequence)
            main_content = {
                'subject': subject,
                'author_id': self.env.user.partner_id.id,
                'body_html': body_html,
                'email_to':self.user_id.partner_id.email,
            }
            self.env['mail.mail'].sudo().create(main_content).send()

    def action_export_plan_lines(self):
        self.ensure_one()
        wb = Workbook()
        ws = wb.active
        ws.title = "Payment Plan Lines"
        ws.append(['Name', 'Date(YYYY-MM-DD)', 'Percentage'])
        if self.payment_schedule_ids:
            for line in self.payment_schedule_ids.sorted(key=lambda l: l.id):
                if not line.inv_created:
                    ws.append([
                        line.name or '',
                        line.plan_date,
                        line.percentage or 0.0
                    ])

        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        attachment = self.env['ir.attachment'].create({
            'name': 'payment_plan_booking_lines.xlsx',
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
        return {
            'name': 'Import Payment Plans',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            "view_type": "form",
            'res_model': 'import.payment.booking.plan.lines',
            'target': 'new',
            'context': {
                'active_id': self.id,
            }
        }

    def action_edit_lines_offer(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Edit Booking Payment Schedule',
            'res_model': 'booking.payment.update.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_booking_id': self.id,
                'default_final_total_property_value': self.final_total_property_value,
            }
        }

    def action_dp_paid(self):
        # if not self.generate_line:
        #     raise UserError(_("Please Generate Payment Lines!!"))
        if not self.partner_id.is_verified:
            raise UserError(_("Please Verify The Partner Before Booking!!"))
        self.property_unit_id.sudo().status = 'booked'
        self.status = 'dp_paid'

    def action_agreement_sent(self):
        self.status = 'agreement_send'

    def action_cancel(self):
        self.status = 'cancel'

    def action_agreement_signed(self):
        self.status = 'agreement_signed'

    def action_kyc_completed(self):
        self.status = 'kyc_competed'
        self.sales_approved_type = 'waiting'
        groups = [
            'property_sales.group_booking_sales_approval',
        ]
        users = self.env['res.users'].sudo().search([
            ('group_ids', 'in', [
                self.env.ref(group).id for group in groups
            ])
        ])
        for user in users:
            if user.partner_id.email:
                base_url = self.env['ir.config_parameter'].sudo().get_param(
                    'web.base.url')
                record_url = f"{base_url}/web#id={self.id}&model={self._name}&view_type=form"
                body_html = f"""
                                <p>Dear {user.name},</p>
                               <p>
                                   We would like to inform you that the KYC process for the booking has been successfully completed
                               </p>
                                  Kindly review the booking details and proceed with the approval at your earliest convenience.
                                  <p>
                                           Please let us know if any additional information or clarification is required.
                                    </p>
                                  <p>
                                   Thank you for your support.
                                  </p>
                                  <p>
                                       <a href="{record_url}"
                                          style="
                                              background-color:#0a6ebd;
                                              color:#ffffff;
                                              padding:8px 14px;
                                              text-decoration:none;
                                              border-radius:4px;
                                              display:inline-block;
                                          ">
                                          View Booking
                                       </a>
                                   </p>
                                   <p>
                                       Best regards,<br/>
                                       {self.env.user.name}
                                   </p>
                               """
                subject = _('Booking %s KYC Completed – Approval Required') % (
                    self.sequence)
                main_content = {
                    'subject': subject,
                    'author_id': self.env.user.partner_id.id,
                    'body_html': body_html,
                    'email_to': user.partner_id.email,
                }
                self.env['mail.mail'].sudo().create(main_content).send()

    def action_onhold(self):
        self.status = 'on_hold'

    def action_unhold(self):
        self.status = 'draft'

    def unlink(self):
        for record in self:
            if record.inv_created == True:
                raise UserError(_("Sorry Its Already Invoiced !!"))
            if record.offer_id.status != 'draft':
                raise UserError(_("Sorry Booking Is Not In Draft State !!"))
        return super().unlink()


class PropertyBuyerDetails(models.Model):
    _name = 'property.buyer.detail'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'owner_share'
    _description = 'Property Buyer'
    _order = 'id desc'

    offer_id = fields.Many2one(
        'offer.booking',
        string="Offer"
    )
    spa_id = fields.Many2one(
        'spa.book',
        string="SPA Booking",
        ondelete='cascade'
    )

    buyer_id = fields.Many2one(
        'res.partner',
        string="Buyer",
        domain='[("par_type", "=","lead")]',
    )


    owner_share = fields.Float(
        string="Owners Shares"
    )

    relationship = fields.Char(
        string="Relationships"
    )

    age = fields.Integer(
        string="Age",
       related='buyer_id.age'
    )
    date_of_birth = fields.Date(
        string="Date Of Birth",
        related='buyer_id.date_of_birth'
    )


class PaymentScheduleLine(models.Model):
    _name = 'payment.schedule.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _description = 'Payment Schedule Lines'
    _order = 'sequence desc'

    sequence = fields.Integer(
        string="Sequence"
    )

    offer_id = fields.Many2one(
        'offer.booking',
        string="Offer"
    )

    property_project_id = fields.Many2one(
        'property.project',
        string="Project",
        tracking=True
    )

    property_unit_id = fields.Many2one(
        'property.unit',
        string="Unit",
        tracking=True,
        domain='[("project_id", "=", property_project_id),'
               '("status","=","available")]',
    )

    spa_id = fields.Many2one(
        'spa.book',
        string="SPA"
    )

    buyer_id = fields.Many2one(
        'res.partner',
        string="Buyer"
    )

    sale_order = fields.Many2one(
        'sale.order',
        string="sale Order"
    )

    name = fields.Char(
        string="Name"
    )

    plan_date = fields.Date(
        string="Date"
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
        string="Invoice Status",
        store=True,
    )
    pay_status = fields.Selection(
        related='invoice_id.payment_state',
        string="Payment Status",
        store=True,
    )
    amount_residual = fields.Monetary(
        string="Amount Due",
        related='invoice_id.amount_residual',
        currency_field='currency_id',
        store=True,
    )
    inv_created = fields.Boolean(
        string="Invoice Created",
        default=False
    )
    active = fields.Boolean(string='Active', default=True)
    is_booking = fields.Boolean(
        string="Is Booking",
        default=False
    )

    @api.depends('percentage', 'amount')
    def _compute_total_amount(self):
        for rec in self:
            rec.amount = 0.0
            if rec.offer_id.final_total_property_value:
                    amount = (rec.offer_id.final_total_property_value * rec.percentage) / 100
                    rec.amount = amount

    @api.depends('percentage', 'amount','offer_id')
    def _compute_rounded_amount(self):
        """
        Rounds the actual_amount using the rule:
        last two digits < 50 → round down
        last two digits ≥ 50 → round up
        """
        for rec in self:
            if rec.amount:
                last_line = rec.offer_id.payment_schedule_ids.filtered(
                    lambda l: l.active
                ).sorted(
                    key=lambda l: (l.plan_date or fields.Date.today())
                )[-1]
                if last_line and rec.id == last_line.id:
                    if rec.offer_id.final_total_property_value:
                        sales_amount = rec.offer_id.final_total_property_value
                        other_lines = rec.offer_id.payment_schedule_ids.filtered(
                            lambda l: l.id != rec.id and l.active
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

    def action_create_invoice(self):
        order_lines = []
        order_lines.append((0, 0, {
            'name': self.name,
            'quantity': 1,
            'price_unit': self.amount,
            'analytic_distribution': {
                self.offer_id.property_unit_id.analytic_account_id.id: 100,
            },
        }))
        invoice = self.env['account.move'].sudo().create({
            'move_type': 'out_invoice',
            'property_type': 'sale',
            'partner_id': self.offer_id.sale_id.partner_id.id,
            'invoice_origin': self.offer_id.sale_id.name,
            'invoice_line_ids': order_lines,
            'property_project_id': self.offer_id.property_project_id.id,
            'property_unit_id': self.offer_id.property_unit_id.id,
            'sale_id': self.offer_id.sale_id.id,
        })
        self.invoice_id = invoice.id
        self.inv_created = True

    # def _create_installment_payment_schedular(self):
    #     payment_lines = self.env['payment.schedule.line'].sudo().search([('plan_date','=',fields.Date.today()),('inv_created','=',False)])
    #     if payment_lines:
    #         for pay_line in payment_lines:
    #             order_lines = []
    #             order_lines.append((0, 0, {
    #                 'name': pay_line.name,
    #                 'quantity': 1,
    #                 'price_unit': pay_line.amount,
    #                 'analytic_distribution': {
    #                     pay_line.offer_id.property_unit_id.analytic_account_id.id: 100,
    #                 },
    #             }))
    #             invoice = self.env['account.move'].sudo().create({
    #                 'move_type': 'out_invoice',
    #                 'property_type': 'sale',
    #                 'partner_id': pay_line.offer_id.sale_id.partner_id.id,
    #                 'invoice_origin': pay_line.offer_id.sale_id.name,
    #                 'invoice_line_ids': order_lines,
    #                 'property_project_id': pay_line.offer_id.property_project_id.id,
    #                 'property_unit_id': pay_line.offer_id.property_unit_id.id,
    #                 'sale_id': pay_line.offer_id.sale_id.id,
    #             })
    #             pay_line.invoice_id = invoice.id
    #             pay_line.inv_created = True

    def unlink(self):
        for record in self:
            if record.inv_created:
                raise UserError(
                    _("You Can't delete payment lines already invoiced !!"))
            return super(PaymentScheduleLine, self).unlink()


class PaymentOtherCharges(models.Model):
    _name = 'payment.other.charges'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _description = 'Payment Other Charges'
    _order = 'sequence desc'

    sequence = fields.Integer(
        string="Sequence"
    )

    offer_id = fields.Many2one(
        'offer.booking',
        string="Offer"
    )

    spa_id = fields.Many2one(
        'spa.book',
        string="SPA"
    )

    name = fields.Char(
        string="Name"
    )

    amount = fields.Float(
        string="Amount"
    )
