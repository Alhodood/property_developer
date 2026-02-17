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
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta


class SpaBook(models.Model):
    _name = 'spa.book'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'sequence'
    _description = 'SPA'
    _order = 'id desc'

    sequence = fields.Char(
        string="Sequence",
    )

    status = fields.Selection([
        ('draft', 'Draft'),
        ('legal_review', 'Legal Review'),
        ('waiting_for_client_acceptance', 'Waiting for client acceptance'),
        ('client_accept', 'Client Accept'),
        ('sales_manager_approved', 'CRM Manager Approved'),
        ('finance_manager_approved', 'Finance Manager Approved'),
        ('general_manager_approved', 'General Manager Approved'),
    ],
        string="Status",
        default='draft',
        tracking=True,
    )

    terms_description = fields.Html('Description')

    terms_description_second_section = fields.Html('Second Section Description')


    offer_booking = fields.Many2one(
        'offer.booking',
        string="Booking",
        required=True,
        domain="[('general_approved', '=', True)]",
    )
    crm_id = fields.Many2one(
        'crm.lead',
        string="Crm",
        related='offer_booking.crm_id'
    )

    sale_id = fields.Many2one(
        'sale.order',
        string="Offer",
        domain='[("state", "=","sale")]',
        related='offer_booking.sale_id'
    )

    company_id = fields.Many2one(
        'res.company',
        string="Company",
        tracking=True,
        related="offer_booking.company_id",
    )

    company_arabic = fields.Char(
        string="Company Arabic",
        related='offer_booking.company_id.name_arabic'
    )

    currency_id = fields.Many2one(
        'res.currency',
        string="Currency",
        tracking=True,
        related="offer_booking.company_id.currency_id",
    )

    property_project_id = fields.Many2one(
        'property.project',
        string="Project",
        related="offer_booking.property_project_id",
        tracking=True
    )

    project_name_arabic = fields.Char(
        string="Project Name Ar(إســم الـمشروع)",
        tracking=True,
        related='property_project_id.project_name_arabic'

    )

    date_booking = fields.Date(
        sting="Date",
        tracking=True,
        related="offer_booking.date_booking"
    )
    lead_agent_id = fields.Many2one(
        'res.partner',
        string="Agent",
        related="offer_booking.lead_agent_id",
    )

    final_total_property_value = fields.Float(
        string="Final Property Sale Value",
        related="offer_booking.final_total_property_value"
    )

    final_sale_value = fields.Float(
        string="Final Sale Total Value",
        related="offer_booking.final_sale_value"
    )

    crm_user_id = fields.Many2one(
        'res.users',
        string="Crm User",
        default=lambda self: self.env.user,
    )

    user_id = fields.Many2one(
        'res.users',
        string="Sales Person",
        related="offer_booking.user_id"
    )

    property_unit_id = fields.Many2one(
        'property.unit',
        string="Unit",
        tracking=True,
        related="offer_booking.property_unit_id"
    )

    net_area = fields.Float(
        string="Net Area (Sqft)",
        tracking=True,
        related='property_unit_id.total_size'
    )

    allowed_payment_plan_ids = fields.Many2many(
        'property.payment.plan',
        compute='_compute_allowed_payment_plan_ids',
        readonly=True,
    )

    payment_plan_id = fields.Many2one(
        'property.payment.plan',
        string="Payment Plan",
    )

    type_id = fields.Many2one(
        'property.unit.type',
        string="Unit Type",
        tracking=True,
        related='property_unit_id.type_id'
    )

    php = fields.Monetary(
        string="PHP",
        tracking=True,
        currency_field='currency_id',
        related='property_unit_id.php'
    )

    booking_cost = fields.Float(
        string="Booking Cost",
        tracking=True,
        related="offer_booking.booking_cost"
    )

    property_buyer_ids = fields.One2many(
        'property.buyer.detail',
        'spa_id',
        string="Buyer Lines"
    )

    payment_schedule_ids = fields.One2many(
        'payment.schedule.line',
        'spa_id',
        string="Payment Schedule Lines"
    )

    payment_plan_ids = fields.One2many(
        'payment.schedule.spa.line',
        'spa_id',
        string="Payment Lines",
    )

    other_gov_line_ids = fields.One2many(
        'payment.other.charges',
        'spa_id',
        string="Other Gov Charges"
    )

    is_verified = fields.Boolean(default=False)

    spa_sign_date = fields.Date(
        string="Spa Sign Date"
    )
    booking_id = fields.Many2one(
        'offer.booking',
        string="Offer Booking"
    )

    oqood_ids = fields.One2many('oqood.registration',
              'spa_id',
              string="Oqoods"
              )
    snagging_ids = fields.One2many('snagging.unit',
                                'spa_id',
                                string="Snaggings"
                                )
    key_handover_ids = fields.One2many('key.handover',
                                   'spa_id',
                                   string="Key Handovers"
                                   )

    payment_ids = fields.One2many(
        'account.payment',
        compute="_compute_payment_ids",
        string="Payments",
    )

    partner_id = fields.Many2one(
        'res.partner',
        string="Buyer",
        related='offer_booking.partner_id',
        domain="[('par_type', '=', 'lead')]",
    )

    courier_name = fields.Char(
        string="Courier Name",
    )

    dispatch_date = fields.Date(
        string="Dispatch Date",
    )

    tracking_no = fields.Char(
        string="Tracking No"
    )

    delivery_confirmation = fields.Char(
        string='Delivery Confirmation'
    )

    chair_man_sign_date = fields.Date(
        string="Chairman Sign Date"
    )

    plan_updated = fields.Boolean(
        string="Plan Updated",
        default=False
    )

    inv_created = fields.Boolean(
        string="Invoice Created",
        default=False
    )

    generate_commission = fields.Boolean(
        string="Generate Commission",
        default=False
    )

    payment_term_id = fields.Many2one(
        'account.payment.term',
        string="Payment Term"
    )

    @api.onchange('property_project_id')
    def _onchange_terms_description(self):
        self.terms_description = self.property_project_id.terms_description
        self.terms_description_second_section = self.property_project_id.terms_description_second_section

    @api.depends('property_unit_id','sequence')
    def _compute_payment_ids(self):
        for rec in self:
            if rec.property_unit_id:
                payments = self.env['account.payment'].sudo().search([
                    ('property_unit_id', '=', rec.property_unit_id.id),
                ])
                rec.payment_ids = payments
            else:
                rec.payment_ids = False

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

    @api.constrains('offer_booking')
    def _check_unique_spa_per_booking(self):
        """Ensure only one SPA exists per Booking"""
        for record in self:
            if record.offer_booking:
                existing_spa = self.search([
                    ('offer_booking', '=', record.offer_booking.id),
                    ('id', '!=', record.id)
                ], limit=1)
                if existing_spa:
                    raise ValidationError(
                        _("A SPA already exists for this Booking (%s). You cannot create more than one SPA for the same booking.")
                        % record.offer_booking.display_name
                    )
    @api.onchange('offer_booking')
    def _onchange_offer_booking(self):
        for rec in self:
            if rec.offer_booking:
                rec.payment_plan_id = rec.offer_booking.payment_plan_id.id

    @api.model
    def create(self, vals):
        res = super(SpaBook, self).create(vals)
        seq = self.env['ir.sequence'].next_by_code('spa.book.sequence')
        res.sequence = seq
        return res

    def spa_verify(self):
        for rec in self:
            if not rec.offer_booking:
                raise UserError(_('Please choose a approved offer !!'))
            for line in self.offer_booking.payment_schedule_ids:
                line.spa_id = self.id
            for lines in self.offer_booking.other_gov_line_ids:
                lines.spa_id = self.id
            for lines in self.offer_booking.property_buyer_ids:
                lines.spa_id = self.id
            sequence = 1
            for line in self.offer_booking.payment_schedule_ids.sorted(key=lambda l: l.id):
                self.env['payment.schedule.spa.line'].create({
                    'sequence':sequence,
                    'spa_id':self.id,
                    'name':line.name,
                    'plan_date':line.plan_date,
                    'percentage':line.percentage,
                    'amount':line.amount,
                    'rounded_amount':line.rounded_amount,
                    'invoice_id':line.invoice_id.id if line.invoice_id else False,
                    'inv_created':line.inv_created if line.inv_created else False,
                    'is_booking':line.is_booking if line.is_booking else False,
                })
                sequence = sequence + 1
        self.is_verified = True

    def action_waiting_client(self):
        if self.is_verified == False:
            raise UserError(_("Please Verify The Spa First!!"))
        self.status = 'waiting_for_client_acceptance'

    def action_accept_client(self):
        self.status = 'client_accept'
        groups = [
            'property_sales.group_property_sales_crm_manager',
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
                               The following SPA has been accepted by the client and is now awaiting your approval:
                               </p>
                                  Kindly review the spa details and proceed with the approval at your earliest convenience.
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
                                          View SPA
                                       </a>
                                   </p>
                                   <p>
                                       Best regards,<br/>
                                       {self.env.user.name}
                                   </p>
                            """
                subject = _(
                    'SPA  - %s Accepted By Client  – Awaiting CRM Approval') % (
                              self.sequence)
                main_content = {
                    'subject': subject,
                    'author_id': self.env.user.partner_id.id,
                    'body_html': body_html,
                    'email_to': user.partner_id.email,
                }
                self.env['mail.mail'].sudo().create(main_content).send()


    def action_sales_manager_approval(self):
        self.status = 'sales_manager_approved'
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
                                       The following SPA has been accepted by the client and is now awaiting Finance approval:
                                       </p>
                                          Kindly review the spa details and proceed with the approval at your earliest convenience.
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
                                                  View SPA
                                               </a>
                                           </p>
                                           <p>
                                               Best regards,<br/>
                                               {self.env.user.name}
                                           </p>
                                    """
                subject = _(
                    'SPA -  %s Accepted – Awaiting Finance Approval') % (
                              self.sequence)
                main_content = {
                    'subject': subject,
                    'author_id': self.env.user.partner_id.id,
                    'body_html': body_html,
                    'email_to': user.partner_id.email,
                    'email_cc': self.crm_user_id.partner_id.email,
                }
                self.env['mail.mail'].sudo().create(main_content).send()

    def action_finance_approval(self):
        self.status = 'finance_manager_approved'
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
                                   The following SPA has been accepted by the client and is now awaiting GM approval:
                                   </p>
                                      Kindly review the spa details and proceed with the approval at your earliest convenience.
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
                                              View SPA
                                           </a>
                                       </p>
                                       <p>
                                           Best regards,<br/>
                                           {self.env.user.name}
                                           </p>
                                    """
                subject = _(
                    'SPA -  %s Accepted – Awaiting GM Approval') % (
                              self.sequence)
                main_content = {
                    'subject': subject,
                    'author_id': self.env.user.partner_id.id,
                    'body_html': body_html,
                    'email_to': user.partner_id.email,
                    'email_cc': self.crm_user_id.partner_id.email,
                }
                self.env['mail.mail'].sudo().create(main_content).send()

    def action_general_approval(self):
        self.property_unit_id.sudo().status = 'sold'
        self.property_unit_id.sudo().spa_id = self.id
        self.property_unit_id.sudo().buyer_id = self.partner_id.id
        self.status = 'general_manager_approved'
        if self.crm_user_id.partner_id.email:
            base_url = self.env['ir.config_parameter'].sudo().get_param(
                'web.base.url')
            record_url = f"{base_url}/web#id={self.id}&model={self._name}&view_type=form"
            body_html = f"""
                                     <p>Dear {self.crm_user_id.name},</p>
                                       <p>
                                       We are pleased to inform you that the SPA has successfully completed all required approvals, including CRM Manager, Finance, and General Manager.
                                       </p>
                                          The SPA is now fully approved and ready for further processing.
                                          <p>
                                           Thank you for your efforts in managing this SPA.
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
                                                  View SPA
                                               </a>
                                           </p>
                                           <p>
                                               Best regards,<br/>
                                               {self.env.user.name}
                                           </p>
                                """
            subject = _(
                'SPA %s Fully Approved') % (
                          self.sequence)
            main_content = {
                'subject': subject,
                'author_id': self.env.user.partner_id.id,
                'body_html': body_html,
                'email_to':self.user_id.partner_id.email,
            }
            self.env['mail.mail'].sudo().create(main_content).send()

    def action_legal_review(self):
        self.status ='legal_review'

    def _cron_check_spa_oqood_reminders(self):
        spa_ids = self.env['spa.book'].sudo().search([('status','not in',['draft','waiting_for_client_acceptance'])])
        for rec in spa_ids:
            if rec.spa_sign_date:
                remind = rec.spa_sign_date
                reminder_date = remind + timedelta(days=42)
                today = fields.date.today()
                if today == reminder_date:
                    oqood = rec.env['oqood.registration'].sudo().search([('spa_id', '=', rec.id)])
                    if not oqood:
                        subject = f"OQOOD Registration - Reminder ❗️"
                        body = f"""<p>Dear<strong> {rec.crm_user_id.name}</strong>, </p>
                                                     <p>OQOOD Registration Of  <b>{rec.property_unit_id.name}</b> with spa {rec.sequence} is pending<b></p>
        
                                                    <pPlease take necessary action .</p>
                                                    <p>Regards,<br/>
                                                        Odoo System<</p>"""
                        mail_values = {
                            'subject': subject,
                            'body_html': body,
                            'email_to': rec.crm_user_id.email,
                        }
                        rec.env['mail.mail'].create(mail_values).send()

    def action_open_update_payment_wizard(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Update Payment Schedule',
            'res_model': 'spa.payment.update.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_spa_id': self.id,
            }
        }

    def action_view_collected_pdc(self):
        pdc_ids = self.env['pdc.payment.received'].sudo().search(
            [('spa_id', '=', self.id)])
        if pdc_ids:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Collected PDC',
                'res_model': 'pdc.payment.received',
                'view_mode': 'list',
                'domain': [('id', 'in', pdc_ids.ids)],
                'target': 'current',
                'context': {
                    'default_spa_id': self.id,
                }
            }

    def action_open_invoice_created(self):
        invoices = self.env['account.move'].sudo().search([('spa_id','=',self.id)])
        if invoices:
            return {
                'name': 'Invoices',
                'type': 'ir.actions.act_window',
                'view_mode': 'list',
                'res_model': 'account.move',
                'context': "{'move_type':'out_invoice'}",
                'domain': [('spa_id', '=', self.id),
                           ('move_type', '=', 'out_invoice')],
                'target': 'current',
            }

    @api.constrains('payment_plan_ids', 'payment_plan_ids.percentage')
    def _check_total_plan_spa_percentage(self):
        for order in self:
            total_percentage = sum(
                order.payment_plan_ids.mapped('percentage')
            )
            if order.payment_plan_ids and round(total_percentage, 2) != 100.0:
                raise UserError(_(
                    "The total Payment Plan percentage must be 100%%.\n"
                    "Current total: %.2f%%"
                ) % total_percentage)

    def action_create_invoice(self):
        if not self.payment_term_id:
            raise UserError(_('Please Choose the payment term!!'))
        order_lines = []
        lines = self.payment_plan_ids.filtered(
                lambda l: not l.inv_created)
        amount_total = sum(lines.mapped('rounded_amount'))
        name = "Purchase Invoice For - " + str(
            self.property_project_id.name) + " - " + str(
            self.property_unit_id.name)
        order_lines.append((0, 0, {
            'name': name,
            'quantity': 1,
            'price_unit': amount_total,
            'analytic_distribution': {
                self.property_unit_id.analytic_account_id.id: 100,
            },
        }))
        invoice = self.env['account.move'].sudo().create({
            'move_type': 'out_invoice',
            'property_type': 'sale',
            'partner_id': self.partner_id.id,
            'invoice_origin': self.sale_id.name,
            'invoice_line_ids': order_lines,
            'property_project_id': self.property_project_id.id,
            'property_unit_id': self.property_unit_id.id,
            'sale_id': self.sale_id.id,
            'spa_id': self.id,
            'invoice_payment_term_id': self.payment_term_id.id,
        })
        for line in lines:
            line.invoice_id = invoice.id
            line.inv_created = True
        self.inv_created = True

    def action_collect_pdc(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Collect Pdc',
            'res_model': 'spa.add.pdc.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_spa_id': self.id,
                'create': False,
                'delete': False,
            }
        }

    def action_generate_commission(self):
        if self.user_id:
            if self.property_unit_id.sales_commission == 0.0:
                raise UserError(_('Please Add Sales Commission in unit!!'))
            sales_commission_amount = (self.final_total_property_value * self.property_unit_id.sales_commission)/100
            sale_commission = self.env['sale.commission.to.be.paid'].create({
                'date_created': fields.Date.today(),
                'commission_amount': sales_commission_amount,
                'sales_person_id': self.user_id.id,
                'created_by': self.env.user.id,
                'property_project_id': self.property_project_id.id,
                'property_unit_id': self.property_unit_id.id,
                'final_total_property_value': self.final_total_property_value,
                'spa_id': self.id,
            })
            sale_bill = self.env['account.move'].sudo().create({
                'move_type': 'in_invoice',
                'partner_id': self.user_id.partner_id.id,
                'invoice_date': fields.Date.today(),
                'sale_property_commission_id':sale_commission.id,
                'invoice_line_ids': [(0, 0, {
                    'name': 'Sales Commission - ' + str(
                        self.property_project_id.name) + ' - ' + str(
                        self.property_unit_id.name),
                    'quantity': 1,
                    'price_unit': sales_commission_amount,
                })],
            })
        if self.lead_agent_id:
            if self.property_unit_id.agent_commission == 0.0:
                raise UserError(_('Please Add Agent Commission in unit!!'))
            agent_commission_amount = (self.final_total_property_value * self.property_unit_id.agent_commission) / 100
            agent_commission = self.env['agent.commission.to.be.paid'].create({
                'date_created': fields.Date.today(),
                'commission_amount': agent_commission_amount,
                'agent': self.lead_agent_id.id,
                'created_by': self.env.user.id,
                'property_project_id': self.property_project_id.id,
                'property_unit_id': self.property_unit_id.id,
                'final_total_property_value': self.final_total_property_value,
                'spa_id': self.id,
            })
            sale_bill = self.env['account.move'].sudo().create({
                'move_type': 'in_invoice',
                'partner_id': self.user_id.partner_id.id,
                'invoice_date': fields.Date.today(),
                'agent_sale_commission_id':agent_commission.id,
                'invoice_line_ids': [(0, 0, {
                    'name': 'Agent Commission - ' + str(
                        self.property_project_id.name) + ' - ' + str(
                        self.property_unit_id.name),
                    'quantity': 1,
                    'price_unit': agent_commission_amount,
                })],
            })
        self.generate_commission = True
        if self.user_id and sale_commission:
            base_url = self.env['ir.config_parameter'].sudo().get_param(
                'web.base.url')
            record_url = f"{base_url}/web#id={sale_commission.id}&model={sale_commission._name}&view_type=form"
            body_html = f"""
                                <p>Dear {self.user_id.name},</p>
                                  <p>
                                  We would like to inform you that your sales commission has been successfully generated for the following booking {self.offer_booking.sequence}.
                                  </p>
                                    The commission entry has been created in the system and the corresponding vendor bill has also been generated for further processing.
                                     <p>
                                      If you have any questions or require clarification, please feel free to contact the CRM or Accounts team.
                                       </p>
                                       <p>
                                       Thank you for your continued efforts and contribution.
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
                                             View Commission
                                          </a>
                                      </p>
                                      <p>
                                          Best regards,<br/>
                                          {self.env.company.name}
                                      </p>
                              """
            subject = _(
                'Sales Commission Generated for Your Booking %s ') % (
                          self.offer_booking.sequence)
            main_content = {
                'subject': subject,
                'author_id': self.env.user.partner_id.id,
                'body_html': body_html,
                'email_to': self.user_id.partner_id.email,
            }
            self.env['mail.mail'].sudo().create(main_content).send()


class PaymentScheduleSpaLine(models.Model):
    _name = 'payment.schedule.spa.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _description = 'Payment Lines'
    _order = 'sequence desc'

    sequence = fields.Integer(
        string="Sequence"
    )

    spa_id = fields.Many2one(
        'spa.book',
        string="SPA"
    )

    property_project_id = fields.Many2one(
        'property.project',
        string="Project",
        tracking=True,
        related='spa_id.property_project_id'
    )

    property_unit_id = fields.Many2one(
        'property.unit',
        string="Unit",
        tracking=True,
        domain='[("project_id", "=", property_project_id),'
               '("status","=","available")]',
        related='spa_id.property_unit_id'
    )

    partner_id = fields.Many2one(
        'res.partner',
        string="Buyer",
        related='spa_id.partner_id',
    )

    sale_order = fields.Many2one(
        'sale.order',
        string="sale Order",
        related='spa_id.sale_id'
    )

    company_id = fields.Many2one(
        'res.company',
        string="Company",
        tracking=True,
        related="spa_id.company_id",
    )

    crm_id = fields.Many2one(
        'crm.lead',
        string="Crm",
        related='spa_id.crm_id'
    )

    name = fields.Char(
        string="Name"
    )

    plan_date = fields.Date(
        string="Date"
    )

    payment_id = fields.Many2one(
        'property.payment.plan',
        string="Payment",
        related='spa_id.payment_plan_id'
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
        string="Invoice Amount Due",
        related='invoice_id.amount_residual',
        currency_field='currency_id',
        store=True,
    )
    inv_created = fields.Boolean(
        string="Invoice Created",
        default=False
    )

    is_booking = fields.Boolean(
        string="Is Booking",
        default=False
    )

    @api.depends('percentage', 'amount')
    def _compute_total_amount(self):
        for rec in self:
            rec.amount = 0.0
            if rec.spa_id.final_total_property_value:
                    amount = (rec.spa_id.final_total_property_value * rec.percentage) / 100
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
                last_line = rec.spa_id.payment_plan_ids.sorted(
                    lambda l: (l.plan_date or fields.Date.today()),
                )[-1]
                if last_line and rec.id == last_line.id:
                    if rec.spa_id.final_total_property_value:
                        sales_amount = rec.spa_id.final_total_property_value
                        other_lines = rec.spa_id.payment_plan_ids.filtered(
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

    def action_create_invoice(self):
        order_lines = []
        order_lines.append((0, 0, {
            'name': self.name,
            'quantity': 1,
            'price_unit': self.amount,
            'analytic_distribution': {
                self.spa_id.property_unit_id.analytic_account_id.id: 100,
            },
        }))
        invoice = self.env['account.move'].sudo().create({
            'move_type': 'out_invoice',
            'property_type': 'sale',
            'partner_id': self.spa_id.partner_id.id,
            'invoice_origin': self.spa_id.sale_id.name,
            'invoice_line_ids': order_lines,
            'property_project_id': self.spa_id.property_project_id.id,
            'property_unit_id': self.spa_id.property_unit_id.id,
            'sale_id': self.spa_id.sale_id.id,
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
