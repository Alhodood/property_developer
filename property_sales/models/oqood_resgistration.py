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

class OqoodRegistration(models.Model):
    _name = 'oqood.registration'
    _inherit = ['mail.thread','mail.activity.mixin']
    _rec_name = 'sequence'
    _description = 'Oqood Registration'
    _order = 'id desc'

    sequence = fields.Char(
        string="Sequence",
    )

    spa_id = fields.Many2one(
        'spa.book',
        string="SPA",
        domain=[('status', '=', "general_manager_approved")],
    )

    offer_booking = fields.Many2one(
        'offer.booking',
        string="Booking",
        related='spa_id.offer_booking',
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
    partner_id = fields.Many2one(
        'res.partner',
        string="Buyer",
        related='spa_id.partner_id',
        domain="[('par_type', '=', 'lead')]",
    )

    lead_agent_id = fields.Many2one(
        'res.partner',
        string="Agent",
        related="offer_booking.lead_agent_id",
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

    # eoi_id = fields.Many2one(
    #     'expression.interest',
    #     string="EOI",
    #     related="offer_booking.eoi_id"
    # )

    crm_user_id = fields.Many2one(
        'res.users',
        string="Crm User",
        default=lambda self: self.env.user,
    )

    spa_sign_date = fields.Date(
        string="Spa Sign Date",
        related='spa_id.spa_sign_date'
    )

    journal_id = fields.Many2one(
        'account.move',
        domain='[("move_type", "=", "entry")]'
    )


    status = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_for_finance_approval', 'Waiting Finance Approval'),
        ('finance_approve', 'Finance Approved'),
        ('completed', 'Completed')],
        string="Status",
        default='draft',
        tracking=True,
    )

    booking_id = fields.Many2one(
        'offer.booking',
        string="Offer Booking"
    )

    oqood_dead_line = fields.Datetime(
        string="Oqood Deadline"
    )
    initiate_oqood = fields.Boolean(
        string="Oqood Initiated",
        default=False
    )

    registration_date = fields.Date(
        string="Registration Date",
        tracking=True
    )

    reference_no = fields.Char(
        string="Reference No",
        tracking=True
    )
    oqood_status = fields.Selection([
        ('fee_paid','Fee Paid'),
        ('pending','Pending')
    ],
        string="Status",
        tracking=True

    )

    client_sign_date = fields.Date(
        string="Client Sign Date",
        tracking=True
    )

    chairman_sign_date = fields.Date(
        string="Chair Man Sign Date",
        tracking=True
    )

    dsr_status = fields.Selection(
        [
            ('waiting_for_client','Waiting for Client signature'),
            ('waiting_for_chairman','Waiting for Chair signature'),
            ('upload','Upload Signed DSR to DLD'),
            ('issue_title_deed','Issue Title/Certificate'),
         ],
        sting="DSR Status"
    )


    def action_waiting_for_finance_approval(self):
        self.status = 'waiting_for_finance_approval'
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
                                               The following Oqood has been is now awaiting Finance approval:
                                               </p>
                                                  Kindly review the oqood details and proceed with the approval at your earliest convenience.
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
                                                          View Oqood
                                                       </a>
                                                   </p>
                                                   <p>
                                                       Best regards,<br/>
                                                       {self.env.user.name}
                                                   </p>
                                            """
                subject = _(
                    'Oqood -  %s Awaiting Finance Approval') % (
                              self.sequence)
                main_content = {
                    'subject': subject,
                    'author_id': self.env.user.partner_id.id,
                    'body_html': body_html,
                    'email_to': user.partner_id.email,
                }
                self.env['mail.mail'].sudo().create(main_content).send()


    @api.constrains('spa_id')
    def _check_unique_oqood_per_booking(self):
        """Ensure only one SPA exists per Booking"""
        for record in self:
            if record.spa_id:
                existing_spa = self.search([
                    ('spa_id', '=', record.spa_id.id),
                    ('id', '!=', record.id)
                ], limit=1)
                if existing_spa:
                    raise UserError(
                        _("A OQOOD already exists for this SPA (%s). You cannot create more than one OQOOD for the same SPA")
                        % record.spa_id.display_name
                    )


    @api.model
    def create(self, vals):
        res = super(OqoodRegistration, self).create(vals)
        seq = self.env['ir.sequence'].next_by_code('property.oqood.sequence')
        res.sequence = seq
        return res

    def action_approve_finance(self):
        self.status = 'finance_approve'
        if self.crm_user_id.partner_id.email:
            base_url = self.env['ir.config_parameter'].sudo().get_param(
                'web.base.url')
            record_url = f"{base_url}/web#id={self.id}&model={self._name}&view_type=form"
            body_html = f"""
                                        <p>Dear {self.crm_user_id.name},</p>
                                           <p>
                                           The following Oqood has been Approved By Finance:
                                           </p>
                                              Kindly review the Oqood details and proceed with the approval at your earliest convenience.
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
                                                      View Oqood
                                                   </a>
                                               </p>
                                               <p>
                                                   Best regards,<br/>
                                                   {self.env.user.name}
                                               </p>
                                        """
            subject = _(
                'Oqood -  %s Awaiting Finance Approval') % (
                          self.sequence)
            main_content = {
                'subject': subject,
                'author_id': self.env.user.partner_id.id,
                'body_html': body_html,
                'email_to': self.crm_user_id.partner_id.email,
            }
            self.env['mail.mail'].sudo().create(main_content).send()

    def action_complete_oqood(self):
        self.status= 'completed'

    def action_initiate_oqood(self):
        if not self.oqood_dead_line:
            raise UserError("Please Choose A Deadline !!")
        if not self.property_project_id.project_con_id:
            raise UserError("Project Not Found !!")
        if self.property_project_id.project_con_id:
            task = self.env['project.task'].sudo().create({
                'name': f"Oqood Initiation - {self.sequence}",
                'project_id': self.property_project_id.project_con_id.id,
                'user_ids': [(6, 0, [self.crm_user_id.id])],
                'date_deadline':self.oqood_dead_line,
                'is_oqood':True,
                'oqood_id':self.id,
                'description': _(
                    "Initiate Oqood process for SPA:\n"
                    f"SPA: {self.spa_id.sequence}\n"
                    f"Project: {self.property_project_id.name}\n"
                    f"Unit: {self.property_unit_id.name}"
                ),
            })
        self.initiate_oqood =True

    def action_open_my_task(self):
        invoices = self.env['project.task'].sudo().search(
            [('oqood_id', '=', self.id)])
        if invoices:
            return {
                'name': 'Oqood Task',
                'type': 'ir.actions.act_window',
                'view_mode': 'list,form',
                'res_model': 'project.task',
                'context': {
                    'default_oqood_id': self.id,
                    'create': False,
                    'delete': False,
                },
                'domain': [('id', 'in', invoices.ids)],
                'target': 'current',
            }

