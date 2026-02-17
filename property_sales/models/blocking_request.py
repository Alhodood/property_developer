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


class BlockingRequest(models.Model):
    _name = 'blocking.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'sequence_code'
    _description = 'Property Blocking Request'
    _order = 'id desc'

    sequence_code = fields.Char(
        string="Sequence",
        tracking=True,
    )

    crm_id = fields.Many2one(
        'crm.lead',
        string="Crm",
        tracking=True,
    )

    partner_id = fields.Many2one(
        'res.partner',
        string="Client",
        tracking=True,
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

    user_id = fields.Many2one(
        'res.users',
        string="Sales Person",
        tracking=True,
        default=lambda self: self.env.user,
    )

    created_by = fields.Many2one(
        'res.users',
        string="Created By",
        tracking=True,
        default=lambda self: self.env.user,
    )

    create_date = fields.Datetime(
        string="Create Date",
        default=fields.Datetime.now,
        tracking=True,

    )

    start_date = fields.Datetime(
        string="Start Date",
        tracking=True,
    )

    end_date = fields.Datetime(
        string="Block End Date",
        tracking=True,
    )

    status = fields.Selection([
        ('draft', 'Draft'),
        ('admin_approved', 'Admin Approved'),
        ('finance_approved', 'Finance Approved'),
        ('refused', 'Refused'),
    ],
        string="Status",
        tracking=True,
        default='draft',
    )

    payment_required = fields.Boolean(
        string="Payment Required",
        default=False,
        tracking=True,
    )

    payment_amount = fields.Float(
        string="Payment Amount",
        tracking=True,
    )

    fst_approval_date = fields.Datetime(
        string="1st Approval Date",
        tracking=True,
    )

    fst_approval_user = fields.Many2one(
        'res.users',
        string="1st Approved User",
        tracking=True,
    )

    fst_approver_comment = fields.Char(
        string="1st Approver Comment",
        tracking=True,
    )
    scnd_approval_date = fields.Datetime(
        string="2nd Approval Date",
        tracking=True,
    )

    scnd_approval_user = fields.Many2one(
        'res.users',
        string="2nd Approved User",
        tracking=True,
    )

    snd_approver_comment = fields.Char(
        string="2nd Approver Comment",
        tracking=True,
    )

    refuse_date = fields.Datetime(
        string="Refuse Date",
        tracking=True,
    )

    refuse_comment = fields.Char(
        string="Refuse Reason",
        tracking=True,
    )

    refuse_user = fields.Many2one(
        'res.users',
        string="Refused User",
        tracking=True,
    )

    blocking_payment_lines_ids = fields.One2many(
        'blocking.payment.lines',
        'blocking_request_id'
    )

    no_of_days = fields.Integer(
        string="No. of Days",
        compute="_compute_no_of_days",
        store=True,
        tracking=True,
    )
    request = fields.Text(
        string="Request",
        tracking=True,
    )

    sale_order = fields.Many2one(
        'sale.order',
        string="Sale Order"
    )

    company_id = fields.Many2one(
        'res.company',
        string="Company",
        tracking=True,
        default=lambda self: self.env.company,
        readonly=True
    )


    @api.depends('start_date', 'end_date')
    def _compute_no_of_days(self):
        for rec in self:
            if rec.start_date and rec.end_date:
                delta = rec.end_date.date() - rec.start_date.date()
                rec.no_of_days = delta.days
            else:
                rec.no_of_days = 0

    def action_approve_fst(self):
        if not self.fst_approver_comment:
            raise UserError(_("Please Add Your Comment."))
        if not self.end_date:
            raise UserError(_("Please Add Block End Date !!."))
        self.fst_approval_date = fields.Datetime.now()
        self.fst_approval_user = self.env.user.id
        self.status = 'admin_approved'
        groups = [
            'property_sales.group_property_blocking',
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
                                        A <strong>Property Unit Blocking Request</strong> has been Approved By {self.env.user.name}:
                                    </p>
                                       <ul>
                                            <li><strong>Customer:</strong> {self.partner_id.name}</li>
                                            <li><strong>Project:</strong> {self.property_project_id.name}</li>
                                            <li><strong>Unit:</strong> {self.property_unit_id.name}</li>
                                            <li><strong>Requested By:</strong> {self.created_by.name}</li>
                                            <li><strong>Offer:</strong> {self.sale_order.name}</li>
                                        </ul>

                                       <p>
                                                Kindly review the blocking request and take the necessary action.
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
                                               View Blocking Request
                                            </a>
                                        </p>
                                       <p>
                                        Please contact the sales team if additional clarification is required.
                                       </p>
                                        <p>
                                            Best regards,<br/>
                                            {self.env.user.name}
                                        </p>
                                """
                subject = _('Unit Blocking Request-%s Admin Approved') % (
                    self.sequence_code)
                main_content = {
                    'subject': subject,
                    'author_id': self.env.user.partner_id.id,
                    'body_html': body_html,
                    'email_to': user.partner_id.email,
                    'email_cc': self.created_by.partner_id.email,
                }
                self.env['mail.mail'].sudo().create(main_content).send()

    def action_approve_scnd(self):
        if self.payment_required and not self.blocking_payment_lines_ids:
            raise UserError(_("Please Add Payment Lines !!"))
        if not self.snd_approver_comment:
            raise UserError(_("Please Add Your Comment."))
        if self.end_date < fields.Datetime.now():
            raise UserError(_("Please Choose Proper End Date"))
        if self.property_unit_id.status != 'available':
            raise UserError(_("The Unit Is Not Available Now"))
        self.start_date = fields.Datetime.now()
        self.scnd_approval_date = fields.Datetime.now()
        self.scnd_approval_user = self.env.user.id
        self.property_unit_id.latest_blocked_date = self.end_date
        self.property_unit_id.latest_block_lead_id = self.crm_id.id
        self.property_unit_id.latest_block_sale_id = self.sale_order.id
        self.sale_order.is_block_lead = True
        self.sale_order.block_type = 'blocked'
        # self.crm_id.is_block_lead = True
        self.property_unit_id.status = 'reserved'
        self.status = 'finance_approved'
        if self.created_by.partner_id.email:
            base_url = self.env['ir.config_parameter'].sudo().get_param(
                'web.base.url')
            record_url = f"{base_url}/web#id={self.id}&model={self._name}&view_type=form"
            body_html = f"""
                    <p>Dear {self.created_by.name},</p>
                    <p>
                        The <strong>Property Unit Blocking Request</strong> has been
                           <strong>approved by {self.env.user.name} </strong>.
                    </p>
                      <ul>
                            <li><strong>Customer:</strong> {self.partner_id.name}</li>
                            <li><strong>Project:</strong> {self.property_project_id.name}</li>
                            <li><strong>Unit:</strong> {self.property_unit_id.name}</li>
                            <li><strong>Blocking Period:</strong> {self.start_date} to {self.end_date}</li>
                            <li><strong>Requested By:</strong> {self.created_by.name}</li>
                            <li><strong>Finance Comment:</strong> {self.snd_approver_comment}</li>
                     </ul>

                       <p>
                              The unit status has now been updated to <strong>Reserved</strong>.
                         </p>
                         <p>
                                Please review the approved blocking request and proceed with the
                                next required action.
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
                            View Blocking Request
                            </a>
                        </p>


                      <p>
                        If further clarification is required, please coordinate with the
                        sales or finance team.
                    </p>

                    <p>
                        Best regards,<br/>
                      {self.env.user.name}<br/>
                    </p>
              """
            subject = _('Unit Blocking Approved (Finance)-%s') % (
                self.sequence_code)
            main_content = {
                'subject': subject,
                'author_id': self.env.user.partner_id.id,
                'body_html': body_html,
                'email_to': self.created_by.partner_id.email,
            }
            self.env['mail.mail'].sudo().create(main_content).send()

    def action_approve_refuse(self):
        if not self.refuse_comment:
            raise UserError(_("Please Add Refuse Reason."))
        self.refuse_date = fields.Datetime.now()
        self.refuse_user = self.env.user.id
        self.status = 'refused'
        if self.created_by.partner_id.email:
            base_url = self.env['ir.config_parameter'].sudo().get_param(
                'web.base.url')
            record_url = f"{base_url}/web#id={self.id}&model={self._name}&view_type=form"
            body_html = f"""
                    <p>Dear {self.created_by.name},</p>
                    <p>
                        The <strong>Property Unit Blocking Request</strong> has been
                           <strong>Rejected by {self.env.user.name}</strong>.
                    </p>
                      <ul>
                            <li><strong>Customer:</strong> {self.partner_id.name}</li>
                            <li><strong>Project:</strong> {self.property_project_id.name}</li>
                            <li><strong>Unit:</strong> {self.property_unit_id.name}</li>
                            <li><strong>Offer:</strong> {self.sale_order.name}</li>
                            <li><strong>Refuse Reason:</strong> {self.refuse_comment}</li>
                     </ul>

                      <p>
                               Kindly review the rejection reason and take the necessary action.
                               You may submit a new blocking request if required.
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
                           View Blocking Request
                        </a>
                        </p>
                    <p>
                        Best regards,<br/>
                      {self.env.user.name}<br/>
                    </p>
              """
            subject = _('Unit Blocking Request Rejected-%s') % (
                self.sequence_code)
            main_content = {
                'subject': subject,
                'author_id': self.env.user.partner_id.id,
                'body_html': body_html,
                'email_to': self.created_by.partner_id.email,
            }
            self.env['mail.mail'].sudo().create(main_content).send()


    @api.model
    def create(self, vals):
        res = super(BlockingRequest, self).create(vals)
        seq = self.env['ir.sequence'].next_by_code(
            'property.blocking.sequence')
        res.sequence_code = seq
        return res

    @api.onchange('crm_id','sale_order')
    def _onchange_crm_enquiry(self):
        if self.sale_order:
            self.partcrm_idner_id = self.sale_order.crm_lead_id.id,
            self.partner_id = self.sale_order.partner_id.id,
            self.property_project_id = self.sale_order.property_project_id.id,
            self.property_unit_id = self.sale_order.property_unit_id.id,
            self.user_id = self.sale_order.user_id.id,


class BlockingPaymentLines(models.Model):
    _name = 'blocking.payment.lines'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'payment_id'
    _description = 'Blocking Payment Lines'
    _order = 'id desc'

    blocking_request_id = fields.Many2one(
        'blocking.request',
        string="Blocking Request"
    )

    payment_id = fields.Many2one(
        'account.payment',
        string="Payment"
    )

    partner_id = fields.Many2one(
        'res.partner',
        string="Partner",
        related="payment_id.partner_id"
    )

    currency_id = fields.Many2one(
        'res.currency',
        string="Currency",
        tracking=True,
        related='payment_id.currency_id',
        readonly=True
    )

    amount = fields.Monetary(
        string="Amount",
        currency_field='currency_id',
        related='payment_id.amount',
    )

    payment_date = fields.Date(
        string="Date",
        related='payment_id.date',
    )

    state = fields.Selection(
        related='payment_id.state'
    )
