from email.policy import default

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
import base64
from odoo import fields, models, _, api
from odoo.exceptions import UserError ,ValidationError


class SnaggingUnit(models.Model):
    _name = 'snagging.unit'
    _inherit = ['mail.thread','mail.activity.mixin']
    _rec_name = 'sequence'
    _description = 'Snagging Unit'
    _order = 'id desc'

    sequence = fields.Char(
        string="Sequence",
    )

    oqood = fields.Many2one(
        'oqood.registration',
        string="Oqood Registration",
        domain=[('status', '=', "completed")],
    )

    offer_booking = fields.Many2one(
        'offer.booking',
        string="Booking",
        related='spa_id.offer_booking',
    )

    spa_id = fields.Many2one(
        'spa.book',
        string="SPA",
        domain=[('status', '=', "general_manager_approved")],
    )

    property_project_id = fields.Many2one(
        'property.project',
        string="Project",
        tracking=True
    )
    lead_agent_id = fields.Many2one(
        'res.partner',
        string="Agent",
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
        domain='[("project_id", "=", property_project_id),'
               '("status","=","sold")]',
    )

    company_id = fields.Many2one(
        'res.company',
        string="Company",
        tracking=True,
        related="property_project_id.company_id",
    )

    company_arabic = fields.Char(
        string="Company Arabic",
        related='property_project_id.company_id.name_arabic'
    )

    project_name_arabic = fields.Char(
        string="Project Name Ar(إســم الـمشروع)",
        tracking=True,
        related='property_project_id.project_name_arabic'

    )

    currency_id = fields.Many2one(
        'res.currency',
        string="Currency",
        tracking=True,
        related="property_project_id.currency_id",
    )

    # eoi_id = fields.Many2one(
    #     'expression.interest',
    #     string="EOI",
    #     related="offer_booking.eoi_id"
    # )
    snagging_date = fields.Date(
        string="Snagging Date",
        default=fields.Date.today()
    )

    status = fields.Selection([
        ('draft', 'Draft'),
        ('assign_snagging', 'Assign Snagging'),
        ('review_snagging', 'Review Requested'),
        ('review_completed', 'Review Completed'),
        ('snagging_completed', 'Snagging Completed'),
        ('revisit', 'Revisit'),
        ],
        string="Status",
        default='draft',
        tracking=True,
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

    key_created = fields.Boolean(
        string="Key Created",
        default=False
    )

    property_owner = fields.Many2one(
        'res.partner',
        string="Property Owner",
        related='property_project_id.property_owner_partner_id'
    )
    property_manager_id = fields.Many2one(
        'res.users',
        string="Property Manager",
        tracking=True,
        related='property_project_id.property_manager_id'
    )


    snagging_towards = fields.Many2one(
        'res.partner',
        string="Snagging Towards"
    )

    partner_id = fields.Many2one(
        'res.partner',
        string="Customer"
    )

    allocated_person = fields.Many2one(
        'res.users',
        string="Allocated Person"
    )

    crm_user_id = fields.Many2one(
        'res.users',
        string="Crm User",
        default=lambda self: self.env.user,
    )

    snagging_attachment_ids = fields.One2many(
        'snagging.unit.line',
        'snagging_id',
        string="Snagging Lines",
        copy=False
    )

    maintenance_id = fields.Many2one(
        'maintenance.request',
        string="Maintenance"
    )
    maintenance_create = fields.Boolean(
        string="Maintenance Created",
        default=False
    )

    is_manager = fields.Boolean(
        string="Is Manager",
        compute='_compute_is_manger'
    )

    @api.depends('oqood', 'sequence','status')
    def _compute_is_manger(self):
        for rec in self:
            rec.is_manager = False
            if self.env.user.id == rec.property_manager_id.id:
                rec.is_manager = True

    @api.onchange('oqood')
    def _ooqood_onchange(self):
        if self.oqood and self.oqood.spa_id:
            self.spa_id = self.oqood.spa_id.id

    # @api.constrains('oqood')
    # def _check_unique_snagging_per_booking(self):
    #     """Ensure only one SPA exists per Booking"""
    #     for record in self:
    #         if record.oqood:
    #             existing_spa = self.search([
    #                 ('oqood', '=', record.oqood.id),
    #                 ('id', '!=', record.id)
    #             ], limit=1)
    #             if existing_spa:
    #                 raise ValidationError(
    #                     _("A Snagging already exists for this OQOOD (%s). You cannot create more than one Snagging for the same OQOOD")
    #                     % record.oqood.display_name
    #                 )

    @api.model
    def create(self, vals):
        res = super(SnaggingUnit, self).create(vals)
        seq = self.env['ir.sequence'].next_by_code('property.snagging.sequence')
        res.sequence = seq
        return res

    def action_assign_snagging(self):
        self.status='assign_snagging'
        if self.allocated_person.partner_id.email:
            base_url = self.env['ir.config_parameter'].sudo().get_param(
                'web.base.url')
            record_url = f"{base_url}/web#id={self.id}&model={self._name}&view_type=form"
            body_html = f"""
                            <p>Dear {self.allocated_person.name},</p>
                           <p>
                           We hope this message finds you well.
                            This is to formally inform you that a Snagging Unit has been assigned to you.
                           </p>
                              You are requested to proceed with the snagging process as per the defined guidelines and complete the assigned task within the stipulated timeframe. Should any clarification or additional support be required, please feel free to coordinate with the Crm Team.
                              <p>
                                Please let us know if any additional documents or clarification are required from our side.
                                </p>
                              <p>
                              Thank you for your cooperation and continued support.
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
                                      View Snagging
                                   </a>
                               </p>
                               <p>
                                   Best regards,<br/>
                                   {self.env.user.name}
                               </p>
                        """
            subject = _(
                'Snagging Assignment Notification - %s') % (
                          self.sequence)
            main_content = {
                'subject': subject,
                'author_id': self.env.user.partner_id.id,
                'body_html': body_html,
                'email_to': self.allocated_person.partner_id.email,
            }
            self.env['mail.mail'].sudo().create(main_content).send()

    def action_review_snagging(self):
        if not self.snagging_attachment_ids:
            raise UserError(
                _("PLease Add snagging lines !!."))
        self.status = 'review_snagging'
        if self.property_manager_id.partner_id.email:
            base_url = self.env['ir.config_parameter'].sudo().get_param(
                'web.base.url')
            record_url = f"{base_url}/web#id={self.id}&model={self._name}&view_type=form"
            body_html = f"""
                                    <p>Dear {self.property_manager_id.name},</p>
                                   <p>
                                   We hope this email finds you well.
                                    This is to inform you that the snagging process has been initiated for the below-mentioned unit and is now submitted for your review and oversight.
                                   </p>
                                      <p>
                                      Kindly review the snagging details, observations, and related attachments in the system. Your verification and guidance are requested to ensure that the snagging activities are completed in accordance with project standards and requirements.

                                          Should any revisions, clarifications, or further actions be required, please advise accordingly so the concerned team may proceed without delay.
                                        </p>
                                      <p>
                                      Thank you for your continued support and supervision.
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
                                              View Snagging
                                           </a>
                                       </p>
                                       <p>
                                           Best regards,<br/>
                                           {self.env.user.name}
                                       </p>
                                """
            subject = _(
                'Snagging Review Notification - %s') % (
                          self.sequence)
            main_content = {
                'subject': subject,
                'author_id': self.env.user.partner_id.id,
                'body_html': body_html,
                'email_to': self.property_manager_id.partner_id.email,
            }
            self.env['mail.mail'].sudo().create(main_content).send()

    def action_complete_reviewing(self):
        self.status ='review_completed'
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
                                       We hope this email finds you well.
                                       </p>
                                          <p>
                                            This is to formally inform you that the snagging review process has been completed for the below-mentioned unit.
                                            </p>
                                          <p>
                                          All observations and remarks have been reviewed and updated in the system accordingly. You may now proceed with the next steps as per the defined CRM and handover process.
                                          Should you require any additional information or clarification, please feel free to reach out.
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
                                                  View Snagging
                                               </a>
                                           </p>
                                           <p>
                                               Best regards,<br/>
                                               {self.env.user.name}
                                           </p>
                                    """
                subject = _(
                    'Snagging Review Completed - %s') % (
                              self.sequence)
                main_content = {
                    'subject': subject,
                    'author_id': self.env.user.partner_id.id,
                    'body_html': body_html,
                    'email_to': self.property_manager_id.partner_id.email,
                }
                self.env['mail.mail'].sudo().create(main_content).send()

    def action_revisit(self):
        vals = {
            'oqood': self.oqood.id,
            'spa_id': self.spa_id.id,
            'property_project_id': self.property_project_id.id,
            'lead_agent_id': self.lead_agent_id.id,
            'user_id': self.user_id.id,
            'property_unit_id': self.property_unit_id.id,
            'company_id': self.company_id.id,
            'property_manager_id': self.property_manager_id.id,
            'snagging_towards': self.snagging_towards.id,
            'partner_id': self.partner_id.id,
            'allocated_person': self.allocated_person.id,
            'crm_user_id': self.crm_user_id.id,
        }
        new_snagging = self.env['snagging.unit'].create(vals)
        self.status = 'revisit'
        return {
            'type': 'ir.actions.act_window',
            'name': 'Snagging Unit Revisit',
            'res_model': 'snagging.unit',
            'view_mode': 'form',
            'res_id': new_snagging.id,
            'target': 'current',
        }

    def action_create_maintenance(self):
        report = self.env.ref('property_sales.action_report_snagging_unit')
        pdf_content, _ =  self.env['ir.actions.report'].sudo()._render_qweb_pdf(report, self.id)
        pdf_base64 = base64.b64encode(pdf_content)
        maintenance = self.env['maintenance.request'].sudo().create({
            'name': f"Snagging Maintenance - {self.sequence}",
            'property_type': 'sale',
            'property_project_id': self.property_project_id.id,
            'property_unit_id': self.property_unit_id.id,
            'snagging_unit': self.id,
            'instruction_type':'pdf',
            'instruction_pdf':pdf_base64,
        })
        self.maintenance_id = maintenance.id
        self.maintenance_create = True

    def action_complete_snagging(self):
        self.status = 'snagging_completed'
        self.property_unit_id.sudo().snagging_completed = True
        if self.crm_user_id.partner_id.email:
            base_url = self.env['ir.config_parameter'].sudo().get_param(
                'web.base.url')
            record_url = f"{base_url}/web#id={self.id}&model={self._name}&view_type=form"
            body_html = f"""
                                    <p>Dear {self.crm_user_id.name},</p>
                                   <p>
                                   We hope this email finds you well.
                                    This is to inform you that the snagging process has been completed Please Check The Snagging
                                   </p>
                                     <p>
                                      Thank you for your continued support and supervision.
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
                                              View Snagging
                                           </a>
                                       </p>
                                       <p>
                                           Best regards,<br/>
                                           {self.env.user.name}
                                       </p>
                                """
            subject = _(
                'Snagging Completed - %s') % (
                          self.sequence)
            main_content = {
                'subject': subject,
                'author_id': self.env.user.partner_id.id,
                'body_html': body_html,
                'email_to': self.property_manager_id.partner_id.email,
            }
            self.env['mail.mail'].sudo().create(main_content).send()



    def action_create_key_handover(self):
        key_handover = self.env['key.handover'].sudo().create({
            'snagging_id': self.id,
        })
        self.key_created = True
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'key.handover',
            'res_id': key_handover.id,
            'view_mode': 'form',
            'target': 'current',
        }

class SnaggingUnitLine(models.Model):
    _name = 'snagging.unit.line'
    _inherit = ['mail.thread','mail.activity.mixin']
    _rec_name = 'description'
    _description = 'Snagging Unit Inspection'
    _order = 'id desc'

    snagging_id = fields.Many2one(
        'snagging.unit',
        string="Snagging Line",
    )

    description = fields.Text(
        string="Description"
    )

    images = fields.Binary(
        string="Images"
    )

    status = fields.Selection(
        [('approved','Approved'),
         ('rejected','Rejected'),
         ('pending','Pending')
         ],
        string="Status",
        default='pending'
    )

    reviewed_by = fields.Many2one(
        'res.users',
        string="Reviewed By"
    )

    reviewed_on = fields.Date(
        string="Reviewed On"
    )

    is_manager = fields.Boolean(
        string="Is Manager",
        compute='_compute_is_manger'
    )
    reject_reason = fields.Text(string="Reject Reason")

    def action_approve(self):
        self.status = 'approved'
        self.reviewed_by = self.env.user.id
        self.reviewed_on = fields.Date.today()

    def action_reject(self):
        return {
            'name': 'Reject Reason',
            'type': 'ir.actions.act_window',
            'res_model': 'snagging.reject.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_line_id': self.id},
        }

    @api.depends('snagging_id','description')
    def _compute_is_manger(self):
        for rec in self:
            rec.is_manager = False
            if self.env.user.id == rec.snagging_id.property_manager_id.id:
                rec.is_manager =True
