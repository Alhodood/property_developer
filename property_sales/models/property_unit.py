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
import base64

class PropertyUnit(models.Model):
    _name = 'property.unit'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _rec_names_search = ['name', 'unit_code']
    _description = 'Property Unit'
    _order = 'id desc'

    name = fields.Char(
        string="Unit name",
        tracking=True,
    )

    unit_code = fields.Char(
        string="Unit Code",
        tracking=True
    )

    status = fields.Selection([
        ('draft', 'Draft'),
        ('available', 'Available'),
        ('reserved', 'Blocked'),
        ('booked', 'Booked'),
        ('sold', 'Sold'),
        ('on_hold', 'On Hold')],
        string="Status",
        default='draft',
        tracking=True,
        copy=False
    )

    project_id = fields.Many2one(
        'property.project',
        string="Project",
        tracking=True
    )

    property_type_id = fields.Many2one(
        comodel_name='property.project.type',
        string="Property Type",
        tracking=True,
        related='project_id.property_type_id'
    )

    company_id = fields.Many2one(
        'res.company',
        string="Company",
        tracking=True,
        default=lambda self: self.env.company,
        readonly=True
    )

    currency_id = fields.Many2one(
        'res.currency',
        string="Currency",
        tracking=True,
        related='company_id.currency_id',
        readonly=True
    )

    final_sale_value = fields.Monetary(
        string="Sale Value",
        currency_field='currency_id',
        tracking=True,
    )

    total_area = fields.Float(
        string="Total Area(m2)",
        tracking=True,
    )

    price_per_sqft = fields.Float(
        string="Price Per Sqft",
        tracking=True,
    )

    floor_no = fields.Integer(
        string="Floor No",
        tracking=True,
    )

    area_sqft = fields.Float(
        string="Area Square Feet",
        tracking=True,
    )

    parking_space = fields.Integer(
        string="Parking Space",
        tracking=True,
    )

    price_psf = fields.Monetary(
        string="Price PSF",
        currency_field='currency_id',
        tracking=True,
    )

    net_price_psf = fields.Monetary(
        string="Net Price PSF",
        currency_field='currency_id',
        tracking=True,
    )

    permitted_use = fields.Char(
        string="Permitted Use",
        tracking=True,
    )

    owner_id = fields.Many2one(
        'res.users',
        string="Property Owner User",
        tracking=True,
    )

    property_owner_partner_id = fields.Many2one(
        'res.partner',
        string="Property Owner",
    )

    no_of_bedrooms = fields.Integer(
        string="No Of Bedrooms",
        tracking=True,
    )

    type_id = fields.Many2one(
        'property.unit.type',
        string="Unit Type",
        tracking=True,
    )
    type_unit = fields.Char(
        string="Type",
        tracking=True,
    )

    type_unit_arabic = fields.Char(
        string="Type Arabic",
        tracking=True,
    )

    internal_area = fields.Float(
        string="Internal Area(Sqft)",
        tracking=True,
    )
    external_area = fields.Float(
        string="External Area(Sqft)",
        tracking=True,
    )
    sellable_area = fields.Float(
        string="Sellable Area(Sqft)",
        tracking=True,
    )

    apartment_area = fields.Float(
        string="Apartment Area(Sqft)",
        tracking=True,
    )

    balcony_area = fields.Float(
        string="Balcony Area(Sqft)",
        tracking=True,
    )

    total_size = fields.Float(
        string="Total Area (Sqft)",
        tracking=True,
    )

    php = fields.Monetary(
        string="Final Sale Value",
        currency_field='currency_id',
        tracking=True,
    )

    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string="Analytic Account",
        tracking=True,
    )

    property_reservation_ids = fields.One2many(
        'property.reservation.line',
        'property_unit_id',
        string="Property Reservation Line"
    )
    floor_plan = fields.Binary(
        string="Floor Plan",
        tracking=True,
    )

    latest_blocked_date = fields.Datetime(
        string="Block Date",
        tracking=True,
    )
    invoices_ids = fields.One2many(
        'account.move',
        'property_unit_id',
        string="Invoices",
        domain="[('move_type', '=', 'out_invoice')]",
    )

    crm_lead_ids = fields.One2many(
        'crm.lead',
        'property_unit_id',
        string="Leads"
    )

    property_blocking_request_ids = fields.One2many(
        'blocking.request',
        'property_unit_id',
        string="Blocking Request"
    )

    payment_ids = fields.One2many(
        'account.payment',
        'property_unit_id',
        string="Payments",
    )

    latest_block_lead_id = fields.Many2one(
        'crm.lead',
        string="Last Block Lead",
        tracking=True,
    )
    latest_block_sale_id = fields.Many2one(
        'sale.order',
        string="Last Block Sales",
        tracking=True,
    )

    media_ids = fields.One2many(
        'property.unit.media',
        'unit_id',
        string="Media Gallery",
        tracking=True,
    )

    view_unit = fields.Text(
        string="View",
        tracking=True,
        copy=False,
    )

    last_hold_date = fields.Date(
        string="Last Hold Date",
        tracking=True,
        copy=False,
    )

    last_hold_by= fields.Many2one(
        'res.users',
        string="Last Hold By",
        tracking=True,
        copy=False,
    )

    hold_reason = fields.Text(
        string="Last Hold Reason",
        tracking=True,
        copy=False,
    )

    title_deed_value = fields.Float(
        string="Title Deed Value",
        compute='_compute_title_deed_value',
        tracking=True,
    )

    oqood_value = fields.Float(
        string="Oqood Value",
        compute='_compute_oqood_value',
        tracking=True,
    )

    total_purchase_value = fields.Float(
        string="Total Purchase Value",
        compute='_compute_total_purchase_value'
    )

    unit_folder_id = fields.Integer(
        default=False)

    agent_commission = fields.Float(
        string="Agent Commission (%)",
        tracking=True,
    )

    sales_commission = fields.Float(
        string="Sales Commission (%)",
        tracking=True,
    )

    snagging_completed = fields.Boolean(
        string="Snagging Completed",
        default=False,
        tracking=True,
    )

    handover_completed = fields.Boolean(
        string="HandOver Completed",
        default=False,
        tracking=True,
    )

    project_con_id = fields.Many2one(
        'project.project',
        string="Project",
        related='project_id.project_con_id'
    )

    price_update_unit_ids = fields.One2many(
        'property.price.unit.history',
        'property_unit_id',
        string="Price Update"
    )

    amenity_ids = fields.Many2many(
        'project.unit.amenity',
        'unit_amenity_rel',  # relation table
        'unit_id',  # column 1
        'amenity_id',  # column 2
        string='Amenities'
    )

    booking_offer_ids = fields.One2many(
        'offer.booking',
        'property_unit_id',
        string="Offer Booking"
    )

    spa_ids = fields.One2many(
        'spa.book',
        'property_unit_id',
        string="Spa"
    )

    oqood_ids = fields.One2many('oqood.registration',
                                'property_unit_id',
                                string="Oqood"
                                )

    snagging_ids = fields.One2many('snagging.unit',
                                   'property_unit_id',
                                   string="Snaggings"
                                   )
    key_handover_ids = fields.One2many('key.handover',
                                       'property_unit_id',
                                       string="Key Handovers"
                                       )

    document_count = fields.Integer(
        compute='_compute_document_count',
        string='Documents',
        help='Count of documents.',
    )

    spa_id = fields.Many2one(
        'spa.book',
        string="Spa",
        tracking=True
    )

    buyer_id = fields.Many2one(
        'res.partner',
        string="Buyer",
        tracking=True,
    )

    def action_send_available_unit_report(self):
        if not self:
            raise UserError("No property units selected.")
        # Report action
        invalid = self.filtered(lambda r: r.status != 'available')
        if invalid:
            raise UserError(
                "Only Available property units can be printed."
            )
        pdf_content, _ = self.env['ir.actions.report'].with_context(
            allowed_company_ids=[self.company_id.id]
        )._render_qweb_pdf('property_sales.action_report_property_unit', res_ids=self.ids)

        # Create attachment
        attachment = self.env['ir.attachment'].create({
            'name': 'Available Unit Report.pdf',
            'type': 'binary',
            'datas': base64.b64encode(pdf_content),
            'mimetype': 'application/pdf',
        })

        # Dynamic subject & body
        subject = "Available Property Units Report"

        body = f"""
            <p>Dear,</p>

            <p>Please find attached the <strong>Available Property Units Report</strong>
            for the selected units.</p>

            <p>Total Units: <strong>{len(self)}</strong></p>

            <p>Regards,<br/>
            {self.env.user.name}</p>
        """

        # Open mail composer
        return {
            'type': 'ir.actions.act_window',
            'name': 'Send Available Unit Report',
            'res_model': 'mail.compose.message',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_model': 'property.unit',
                'default_res_ids': self.ids,
                'default_attachment_ids': [(6, 0, [attachment.id])],
                'default_composition_mode': 'comment',

                # 👇 NEW
                'default_subject': subject,
                'default_body': body,
            }
        }

    def _compute_document_count(self):
        """Get count of documents."""
        for rec in self:
            rec.document_count = self.env['property.sales.unit.document'].sudo().search_count(
                [('property_unit_id', '=', rec.id)])

    def action_document_view(self):
        self.ensure_one()
        return {
            'name': _('Documents'),
            'domain': [('property_unit_id', '=', self.id)],
            'res_model': 'property.sales.unit.document',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'list,form',
            'limit': 80,
            'context': "{'default_property_unit_id': %s}" % self.id
        }


    @api.onchange('project_id')
    def _on_change_property(self):
        if self.project_id:
            self.agent_commission = self.project_id.agent_commission
            self.sales_commission = self.project_id.sales_commission


    def action_unblock_block_property(self):
        """ Unblock the property Unit - In the block state """
        self.status = 'available'
        self.latest_block_sale_id.is_block_lead = False
        self.latest_block_sale_id.block_type = False
        self.latest_blocked_date = False
        if self.latest_block_sale_id.user_id.email:
            base_url = self.env['ir.config_parameter'].sudo().get_param(
                'web.base.url')
            record_url = f"{base_url}/web#id={self.latest_block_sale_id.id}&model={self.latest_block_sale_id._name}&view_type=form"
            body_html = f"""
                    <p>Dear {self.latest_block_sale_id.user_id.name},</p>
                    <p>
                        Please note that the unit [{self.name}/{self.project_id.name}] previously blocked has been unblocked following management approval, in accordance with sales policy.
                    </p>
                       <p>
                              The unit status has been updated in the system.For any clarification, please feel free to reach out.
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
                            View Offer
                            </a>
                        </p>

                    <p>
                        Best regards,<br/>
                      {self.env.user.name}<br/>
                    </p>
              """
            subject = _('Unit Unblocked %s-%s') % (
                self.unit_code,self.name)
            main_content = {
                'subject': subject,
                'author_id': self.env.user.partner_id.id,
                'body_html': body_html,
                'email_to': self.latest_block_sale_id.user_id.email,
            }
            self.env['mail.mail'].sudo().create(main_content).send()

    @api.depends('project_id','name','php')
    def _compute_title_deed_value(self):
        for rec in self:
            if rec.project_id.other_fees_line_ids:
                fees = rec.project_id.other_fees_line_ids.filtered(
                    lambda f: f.is_title_deed)
                if fees:
                    if fees.percentage > 0 and rec.php:
                        total = (fees.percentage / 100.0) * rec.php
                    else:
                        total = fees.fixed_amount
                    rec.title_deed_value = total
                else:
                    rec.title_deed_value = 0.0
            else:
                rec.title_deed_value = 0.0

    @api.depends('project_id', 'name','php')
    def _compute_oqood_value(self):
        for rec in self:
            if rec.project_id.other_fees_line_ids:
                fees = rec.project_id.other_fees_line_ids.filtered(
                    lambda f: f.is_oqood)
                if fees:
                    if fees.percentage > 0 and rec.php:
                        total = (fees.percentage / 100.0) * rec.php
                    else:
                        total = fees.fixed_amount
                    rec.oqood_value = total
                else:
                    rec.oqood_value = 0.0
            else:
                rec.oqood_value = 0.0

    @api.depends('project_id', 'title_deed_value','oqood_value','php')
    def _compute_total_purchase_value(self):
        for rec in self:
            if rec.title_deed_value and rec.oqood_value and rec.php:
                rec.total_purchase_value = rec.title_deed_value + rec.oqood_value + rec.php
            else:
                rec.total_purchase_value =0.0


    def cron_unblock_units(self):
        """Unblock property units whose block date is expired"""
        now = fields.Datetime.now()
        expired_units = self.env['property.unit'].sudo().search([
            ('status', '=', 'reserved'),
            ('latest_blocked_date', '<', now)
        ])
        for unit in expired_units:
            unit.status = 'available'
            unit.latest_blocked_date = False
            unit.latest_block_sale_id.is_block_lead = False
            unit.latest_block_sale_id.block_type = False
            if unit.latest_block_sale_id.user_id.email:
                base_url = unit.env['ir.config_parameter'].sudo().get_param(
                    'web.base.url')
                record_url = f"{base_url}/web#id={unit.latest_block_sale_id.id}&model={unit.latest_block_sale_id._name}&view_type=form"
                body_html = f"""
                        <p>Dear {unit.latest_block_sale_id.user_id.name},</p>
                        <p>
                            Please note that the unit [{unit.name}/{unit.project_id.name}] previously blocked has been unblocked following management approval, in accordance with sales policy.
                        </p>
                           <p>
                                  The unit status has been updated in the system.For any clarification, please feel free to reach out.
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
                                 View Offer
                                </a>
                            </p>

                        <p>
                            Best regards,<br/>
                          {self.env.user.name}<br/>
                        </p>
                  """
                subject = _('Unit Unblocked %s-%s') % (
                    unit.unit_code, unit.name)
                main_content = {
                    'subject': subject,
                    'author_id': self.env.user.partner_id.id,
                    'body_html': body_html,
                    'email_to': unit.latest_block_sale_id.user_id.email,
                }
                self.env['mail.mail'].sudo().create(main_content).send()

    @api.model
    def create(self, vals):
        """ OverRide The Create Function For Propery Unit Analytic Creation"""
        res = super(PropertyUnit, self).create(vals)
        seq = self.env['ir.sequence'].next_by_code(
            'property.unit.sequence')
        res.unit_code = seq
        if res.name:
            analytic_name =  res.name
        else:
            analytic_name = res.unit_code
        if res.project_id.analytic_account_id:
            analytic_account_id = self.env['account.analytic.account'].sudo().create({
                'name': analytic_name,
                'plan_id': res.project_id.analytic_account_id.plan_id.id,
                'parent_id': res.project_id.analytic_account_id.id
            })
            res.analytic_account_id = analytic_account_id.id

        unit_folder = self.env['documents.document'].sudo().search([
            ('name', '=', res.name),
            ('type', '=', 'folder'),
            ('owner_id', '=', False),
            ('folder_id', '=', res.project_id.property_folder_id),
        ], limit=1)
        if not unit_folder:
            unit_folder = self.env['documents.document'].sudo().create({
                'name': res.name,
                'type': 'folder',
                'owner_id': False,
                'access_internal': 'view',
                'folder_id':res.project_id.property_folder_id
            })

        res.unit_folder_id = unit_folder.id
        return res

    @api.onchange('name')
    def _onchange_name(self):
        """ Change the name of analytic account """
        if self.analytic_account_id:
            self.analytic_account_id.name = self.name
        if self.unit_folder_id:
            folder = self.env['documents.document'].sudo().search([('id','=',self.unit_folder_id)])
            if folder:
                folder.name = self.name

    def write(self, vals):
        res = super(PropertyUnit, self).write(vals)
        if 'name' in vals:
            for record in self:
                if record.analytic_account_id:
                    record.analytic_account_id.name = record.name
                if record.unit_folder_id:
                    folder = self.env['documents.document'].sudo().search([('id','=',record.unit_folder_id)])
                    if folder:
                        folder.name = self.name   
        return res

    def action_view_units(self):
        """ View All  Property Units"""
        return {
            'name': 'Property Units',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'property.unit',
            'res_id': self.id,
            'target': 'current',
        }


    def action_view_property__unit_offer(self):
        offer_ids = self.env['sale.order'].sudo().search(
            [('property_unit_id', '=', self.id)])
        if offer_ids:
            return {
                'name': 'Offer',
                'view_type': 'list',
                'view_mode': 'list,form',
                'res_model': 'sale.order',
                'domain': [('id', 'in', offer_ids.ids)],
                'type': 'ir.actions.act_window',
                'context': {'default_property_unit_id': self.id, }
            }

    def action_view_property_unit_leads(self):
        offer_ids = self.env['crm.lead'].sudo().search(
            [('property_unit_id', 'in', self.id)])
        if offer_ids:
            return {
                'name': 'Leads',
                'view_type': 'list',
                'view_mode': 'list,form',
                'res_model': 'crm.lead',
                'domain': [('id', 'in', offer_ids.ids)],
                'type': 'ir.actions.act_window',
                'context': {

                }
            }


    def action_make_available_in_draft(self):
        """ Make The Status As Available """
        self.status = 'available'

    def action_put_on_hold(self):
        """Set status to On Hold"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Hold Property Units',
            'res_model': 'property.unit.hold.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'active_ids': self.ids,
                'default_unit_ids': self.ids,
            }
        }

    def action_make_available(self):
        """Set status to Available"""
        for rec in self:
            rec.status = "available"

    def action_hold_property_unit(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Hold Property Units',
            'res_model': 'property.unit.hold.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'active_ids': self.ids,
                'default_unit_ids': self.ids,
            }
        }

    def action_make_available_unit_list(self):
        for rec in self:
            if rec.status in ['on_hold','draft']:
                rec.status = "available"

    def action_print_available_unit_list(self):
        if not self:
            raise UserError("No property units selected.")
        invalid = self.filtered(lambda r: r.status != 'available')
        if invalid:
            raise UserError(
                "Only Available property units can be printed."
            )
        return self.env.ref(
            'property_sales.action_report_property_unit'
        ).report_action(self)


    def action_create_offer_in_unit(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Sales Order',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_property_project_id': self.project_id.id,
                'default_property_unit_id': self.id,
                'default_property_type': 'broker',
                'default_php': self.php,
            }
        }


class PropertyUnitType(models.Model):
    _name = 'property.unit.type'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _description = 'Property Unit'
    _order = 'sequence desc'

    sequence = fields.Integer(
        string="Sequence"
    )
    name = fields.Char(
        string="Name"
    )

    color = fields.Char(
        string="Row Color",
        help="HEX color code for reports (example: #e6f7d9)"
    )


class PropertyReservation(models.Model):
    _name = 'property.reservation.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'property_unit_id'
    _description = 'Property Reservation'
    _order = 'id desc'


    crm_id = fields.Many2one(
        'crm.lead',
        string="Crm",
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
    )

    start_date = fields.Datetime(
        string="Start Date",
    )

    end_date = fields.Datetime(
        string="End Date",
    )

    no_of_days = fields.Float(
        string="No Of Days"
    )

    sales_person = fields.Many2one(
        'res.users',
        string="Sales Person"
    )

    partner_id = fields.Many2one(
        'res.partner',
        string="Partner"
    )


class PropertyUnitMedia(models.Model):
    _name = 'property.unit.media'
    _description = 'Property Unit Media'
    _order = 'sequence, id'

    name = fields.Char(string="Title")
    sequence = fields.Integer(default=10)

    unit_id = fields.Many2one(
        'property.unit',
        string="Property Unit",
        required=True,
        ondelete='cascade'
    )

    media_type = fields.Selection([
        ('image', 'Image'),
        ('video', 'Video'),
        ('virtual', 'Virtual Tour'),
        ('floor_plan', '3D Floor Plan'),
    ], required=True, default='image')

    image = fields.Image(
        string="Image",
        max_width=1920,
        max_height=1920
    )

    video_file = fields.Html(string="Video File")

    embed_url = fields.Char(
        string="Embed URL",
        help="YouTube / Matterport embed URL"
    )

    document_file = fields.Html(
        string="3D / Floor Plan File"
    )
    document_filename = fields.Char(string="Filename")

    preview_image = fields.Image(
        string="Preview",
        compute="_compute_preview",
        store=False
    )

    @api.depends('media_type', 'image')
    def _compute_preview(self):
        for rec in self:
            rec.preview_image = rec.image if rec.media_type == 'image' else False