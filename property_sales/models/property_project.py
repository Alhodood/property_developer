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
from odoo import api, fields, models, modules, _
from odoo.exceptions import UserError
from translate import Translator

class PropertyNearBy(models.Model):
    _name = 'property.near.by'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Property Near By'
    _order = 'name'

    name = fields.Char(
        string='Name'
    )

    image = fields.Image(
        string="Image"
    )


class PropertySaleDetails(models.Model):
    _name = 'property.sale.details'

    description = fields.Text(
        string="Title"
    )

    images = fields.Binary(
        string="Images"
    )
    property_id = fields.Many2one(
        comodel_name='property.project',
        string='Property'
    )

class NearPropertySalesLines(models.Model):
    _name = 'property.near.by.sales.line'

    description = fields.Text(
        string="Title"
    )
    nearby = fields.Many2one(
        comodel_name='property.near.by',
        string="Near By"
    )

    images = fields.Image(
        string="Images",
        related='nearby.image'
    )

    property_id = fields.Many2one(
        comodel_name='property.project',
        string='Property'
    )

    distance = fields.Char(
        string="Distance"
    )



class PropertyProject(models.Model):
    _name = 'property.project'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _rec_names_search = ['name', 'project_sequence', 'project_name_arabic']
    _description = 'Property Project'
    _order = 'id desc'

    name = fields.Char(
        string="Name",
        tracking=True,

    )

    is_created_from_pr = fields.Boolean(
        string="Is Created From Pr",
        default=False
    )

    project_name_arabic = fields.Char(
        string="Project Name Arabic",
        tracking=True,

    )
    project_sequence = fields.Char(
        string='Sequence',
        tracking=True
    )
    street1 = fields.Char(
        string="Street1",
        tracking=True
    )
    street2 = fields.Char(
        string="Street2",
        tracking=True
    )
    town_ship = fields.Char(
        string="Township",
        tracking=True
    )
    city = fields.Char(
        string="City",
        tracking=True
    )
    country_id = fields.Many2one(
        'res.country',
        string="Country",
        tracking=True
    )
    state_id = fields.Many2one(
        'res.country.state',
        string="State",
        domain="[('country_id', '=', country_id)]",
        tracking=True
    )

    zip = fields.Char(
        string="Zip",
        tracking=True
    )
    latitude = fields.Float(
        string="Latitude",
        digits=(16, 8),
        tracking=True
    )
    longitude = fields.Float(
        string="Longitude",
        digits=(16, 8),
        tracking=True
    )
    location_url = fields.Char(
        string="Location Url",
        tracking=True
    )
    expected_hand_over_date = fields.Date(
        string="Expected Hand Over Date",
        tracking=True
    )

    property_owner_id = fields.Many2one(
        'res.users',
        string="Property Owners User",
        tracking=True
    )
    property_owner_partner_id = fields.Many2one(
        'res.partner',
        string="Property Owner",
    )
    property_manager_id = fields.Many2one(
        'res.users',
        string="Property Manager",
        tracking=True
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
    property_type_id = fields.Many2one(
        comodel_name='property.project.type',
        string="Property Type",
        tracking=True
    )

    property_image = fields.Binary(
        string='property image',
    )

    state = fields.Many2one(
        comodel_name='project.property.state',
        string="State",
        tracking=True,
        group_expand='_read_group_stage_ids',
    )

    escrow_acc_name = fields.Char(
        string="Escrow Account Name",
        tracking=True,
    )

    escrow_acc_number = fields.Char(
        string="Escrow Account Number",
        tracking=True,
    )

    bank_name = fields.Char(
        string="Bank Name",
        tracking=True
    )

    bank_name_escrow = fields.Char(
        string="Bank Name Escrow",
        tracking=True
    )

    iban_number = fields.Char(
        string="IBAN Number",
        tracking=True,
    )

    iban_number_escrow = fields.Char(
        string="IBAN Number escrow",
        tracking=True,
    )

    swift = fields.Char(
        string="SWIFT ",
        tracking=True,
    )

    swift_escrow = fields.Char(
        string="SWIFT Escrow",
        tracking=True,
    )

    account_no = fields.Char('Account Number')

    account_no_escrow = fields.Char('Account Number Escrow')

    branch = fields.Char(
        string="Branch",
        tracking=True,
    )
    branch_escrow = fields.Char(
        string="Branch Escrow",
        tracking=True,
    )

    account_name = fields.Char(
        string="Account Name",
        tracking=True,
    )

    bank_address = fields.Text(
        string="Bank Address",
        tracking=True,
    )
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string="Analytic Account",
        tracking=True,
    )

    plot_size = fields.Char(
        string="Plot Size"
    )


    map_html = fields.Html(
        string="Map",
        compute="_compute_map_html",
        sanitize=False
    )


    about = fields.Html(
        string="About The Project"
    )

    property_unit_summary_ids = fields.One2many(
        'property.unit.available',
        'project_id',
        string="Unit Summary"
    )

    property_unit_ids = fields.One2many(
        'property.unit',
        'project_id',
        string="Units"
    )

    property_blocking_request_ids = fields.One2many(
        'blocking.request',
        'property_project_id',
        string="Blocking Request"
    )

    sale_offer_ids = fields.One2many(
        'sale.order',
        'property_project_id',
        string="Offers"
    )

    invoices_ids = fields.One2many(
        'account.move',
        'property_project_id',
        string="Invoices",
        domain="[('move_type', '=', 'out_invoice')]",
    )

    payment_ids = fields.One2many(
        'account.payment',
        'property_project_id',
        string="Payments",
    )

    property_details_ids = fields.One2many(
        comodel_name='property.sale.details',
        inverse_name='property_id',
        string="Property Details"
    )

    nearby_property_line_ids = fields.One2many(
        comodel_name='property.near.by.sales.line',
        inverse_name='property_id',
        string="Near BY"
    )

    other_fees_line_ids = fields.One2many(
        comodel_name='property.other.fees',
        inverse_name='property_id',
        string="Other Fees"
    )

    project_register_name = fields.Char(
        string="RERA Project Reg. No."
    )

    plot_no = fields.Char(
        string="Plot Number"
    )

    master_develop_name = fields.Char(
        string="Master Developer Name"
    )

    master_develop_name_arabic = fields.Char(
        string="Master Developer Name Arabic"
    )

    master_community = fields.Char(
        string="Master Community"
    )

    master_community_arabic = fields.Char(
        string="Master Community Arabic"
    )

    register_type = fields.Char(
        string="Registration Type"
    )

    document_count = fields.Integer(
        compute='_compute_document_count',
        string='Documents',
        help='Count of documents.'
    )

    project_con_id = fields.Many2one(
        'project.project',
        string="Project"
    )

    payment_plan_ids = fields.One2many(
        'property.payment.plan',
        'property_project_id',
        string="Property Payment Plan",
    )

    property_folder_id = fields.Integer(default=False)

    agent_commission = fields.Float(
        string="Agent Commission (%)"
    )

    sales_commission = fields.Float(
        string="Sales Commission (%)"
    )

    price_update_ids = fields.One2many(
        'property.price.update',
        'project_id',
        string="Price Update History"
    )

    terms_description = fields.Html('Description')

    terms_description_second_section = fields.Html('Second Section Description')


    amenity_ids = fields.Many2many(
        'project.amenity',
        'project_amenity_rel',      # relation table
        'project_id',               # column 1
        'amenity_id',               # column 2
        string='Amenities'
    )

    booking_offer_ids = fields.One2many(
        'offer.booking',
        'property_project_id',
        string="Offer Booking"
    )

    spa_ids = fields.One2many(
        'spa.book',
        'property_project_id',
        string="Spa"
    )

    oqood_ids = fields.One2many('oqood.registration',
                                'property_project_id',
                                string="Oqood"
                                )
    snagging_ids = fields.One2many('snagging.unit',
                                   'property_project_id',
                                   string="Snaggings"
                                   )
    key_handover_ids = fields.One2many('key.handover',
                                       'property_project_id',
                                       string="Key Handovers"
                                       )

    direct_down_payment_ids = fields.One2many(
        'property.discount.direct.down.payment',
        'property_project_id',
        string="Direct Down Payment"
    )

    direct_payment_plan_ids = fields.One2many(
        'property.discount.direct.payment.plan',
        'property_project_id',
        string="Direct Payment Plan Discount"
    )

    in_direct_payment_plan_ids = fields.One2many(
        'property.discount.indirect.payment.plan',
        'property_project_id',
        string="In Direct Payment Plan Discount"
    )

    in_direct_down_payment_ids = fields.One2many(
        'property.discount.indirect.down.payment',
        'property_project_id',
        string="In Direct Down Payment Discount"
    )

    discount_approvers_ids = fields.Many2many(
        'res.users',
        string="Discount Approvers",
        domain=lambda self: [('all_group_ids', 'in',[
            self.env.ref('property_sales.group_discount_approver').id,
            self.env.ref('property_sales.group_discount_manager').id
        ])]
    )



    @api.model
    def _read_group_stage_ids(self, stages, domain):
        return self.env['project.property.state'].search([],
                                                         order='sequence,id')

    def _compute_document_count(self):
        """Get count of documents."""
        for rec in self:
            rec.document_count = self.env['property.sales.document'].sudo().search_count(
                [('property_id', '=', rec.id)])

    def action_document_view(self):
        self.ensure_one()
        return {
            'name': _('Documents'),
            'domain': [('property_id', '=', self.id)],
            'res_model': 'property.sales.document',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'list,form',
            'limit': 80,
            'context': "{'default_property_id': %s}" % self.id
        }

    def action_open_price_update_wizard(self):
        self.ensure_one()
        return {
            'name': 'Price Update',
            'type': 'ir.actions.act_window',
            'res_model': 'property.price.update.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_project_id': self.id,
            }
        }

    @api.depends('name')
    def _compute_crm_leads(self):
        Lead = self.env['crm.lead']
        for project in self:
            project.crm_lead_ids = Lead.sudo().search([
                ('property_project_id', 'in', project.id)
            ])

    @api.depends('latitude', 'longitude')
    def _compute_map_html(self):
        for rec in self:
            if rec.latitude and rec.longitude:
                rec.map_html = f'''
                       <iframe
                           width="100%"
                           height="400"
                           style="border:0;"
                           loading="lazy"
                           allowfullscreen
                           src="https://maps.google.com/maps?q=loc:{rec.latitude},{rec.longitude}&output=embed">
                       </iframe>
                   '''
            else:
                rec.map_html = "<p>No location set</p>"

    @api.model
    def create(self, vals):
        if not self.env.user.has_group('property_sales.group_property_sales_manager'):
            raise UserError("You Did not Have The Rights To Create The Property")
        res = super(PropertyProject, self).create(vals)
        seq = self.env['ir.sequence'].next_by_code(
            'property.project.sequence')
        if not res.analytic_account_id:
            project_plan_id = int(
                self.env['ir.config_parameter'].sudo().get_param(
                    'analytic.analytic_plan_projects'))
            if not project_plan_id:
                project_plan, _other_plans = self.env[
                    'account.analytic.plan']._get_all_plans()
                project_plan_id = project_plan.id
            if not project_plan_id:
                analytic_plan = self.env['account.analytic.plan'].create({
                    'name': res.name,
                })
                project_plan_id = analytic_plan.id
            analytic_account_id = self.env['account.analytic.account'].create({
                'name': res.name,
                'plan_id': project_plan_id,
            })
            res.analytic_account_id = analytic_account_id.id
        res.project_sequence = seq

        company = res.env.company
        property_folder = self.env['documents.document'].sudo().search([
            ('name', '=', res.name),
            ('type', '=', 'folder'),
            ('owner_id', '=', False),
        ], limit=1)
        if not property_folder:
            property_folder = self.env['documents.document'].sudo().create({
                'name': res.name,
                'type': 'folder',
                'owner_id': False,
                'company_id': company.id,
                'access_internal': 'view',
            })

        res.property_folder_id = property_folder.id
        return res

    @api.onchange('name')
    def _onchange_name(self):
        """Auto-translate English name to Arabic"""
        if self.name:
            translator = Translator(to_lang="ar")
            text = self.name
            translation = translator.translate(text)
            self.project_name_arabic = translation
        if self.analytic_account_id:
            self.analytic_account_id.name = self.name

    def action_map_location(self):
        if self.longitude and self.latitude:
            longitude = self.longitude
            latitude = self.latitude
            http_url = 'https://maps.google.com/maps?q=loc:' + str(
                latitude) + ',' + str(longitude)
            return {
                'type': 'ir.actions.act_url',
                'target': 'new',
                'url': http_url,
            }
        else:
            raise UserError("! Enter Proper Longitude and Latitude Values")


    def action_view_blocking_request(self):
        blocking_ids = self.env['blocking.request'].sudo().search(
            [('property_project_id', '=', self.id)])
        if blocking_ids:
            return {
                'name': 'Blocking Request',
                'view_type': 'list',
                'view_mode': 'list,form',
                'res_model': 'blocking.request',
                'domain': [('id', '=', blocking_ids.ids)],
                'type': 'ir.actions.act_window',
                'context': {'default_property_project_id': self.id, }
            }

    def action_view_property_offer(self):
        offer_ids = self.env['sale.order'].sudo().search(
            [('property_project_id', '=', self.id)])
        if offer_ids:
            return {
                'name': 'Offer',
                'view_type': 'list',
                'view_mode': 'list,form',
                'res_model': 'sale.order',
                'domain': [('id', 'in', offer_ids.ids)],
                'type': 'ir.actions.act_window',
                'context': {'default_property_project_id': self.id, }
            }

    def action_view_property_leads(self):
        offer_ids = self.env['crm.lead'].sudo().search(
            [('property_project_id', 'in', self.id)])
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

    def action_view_add_payment_plan(self):
        return {
            'name': 'Payment Plan',
            'view_type': 'list',
            'view_mode': 'list,form',
            'res_model': 'property.payment.plan',
            'domain': [('property_project_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'context': {
                'default_property_project_id': self.id,
            }
        }

    def geo_localize(self):
        # We need country names in English below
        if not self.env.context.get('force_geo_localize') and (
            self.env.context.get('import_file')
            or modules.module.current_test
            or not self.env.registry.ready
        ):
            return False
        partner = self.env['res.partner']
        partners_not_geo_localized = self.env['property.project']
        for property in self.with_context(lang='en_US'):
            result = partner._geo_localize(property.street1,
                                        property.zip,
                                        property.city,
                                        property.state_id.name,
                                        property.country_id.name)

            if result:
                property.write({
                    'latitude': result[0],
                    'longitude': result[1],
                    # 'date_localization': fields.Date.context_today(property)
                })
            else:
                partners_not_geo_localized |= property
        if partners_not_geo_localized:
            self.env.user._bus_send("simple_notification", {
                'type': 'danger',
                'title': _("Warning"),
                'message': _('No match found for %(property_name)s address(es).',
                             property_name=', '.join(partners_not_geo_localized.mapped('display_name')))
            })
        return True


class PropertyProjectState(models.Model):
    _name = 'project.property.state'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _description = 'Property Stage'
    _order = 'sequence desc'

    sequence = fields.Integer(
        string="Sequence"
    )
    name = fields.Char(
        string="Name"
    )


class PropertyUnitAvailable(models.Model):
    _name = 'property.unit.available'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'type_id'
    _description = 'Property Unit Available'
    _order = 'id desc'

    type_id = fields.Many2one(
        'property.unit.type',
        string="Type"
    )

    number_of_unit = fields.Integer(
        string="Number Of Unit"
    )

    area_sqft = fields.Float(
        string="Area(Sqft)"
    )

    creation_done = fields.Boolean(
        string="Creation Done",
        default=False
    )

    total_property_units = fields.Integer(
        string="Total Units",
        compute='_compute_total_property_units'
    )

    available_units = fields.Integer(
        string="Available Units",
        compute='_compute_total_units'
    )

    total_area = fields.Float(
        string="Total Area Available(Sqft)",
        compute='_compute_total_area'
    )

    project_id = fields.Many2one(
        'property.project',
        string="Project",
        tracking=True
    )


    def action_create_units(self):
        if self.number_of_unit:
            for i in range(int(self.number_of_unit)):
                self.env['property.unit'].sudo().create({
                    'project_id': self.project_id.id,
                    'area_sqft': self.area_sqft,
                    'owner_id': self.project_id.property_owner_id.id,
                    'property_owner_partner_id': self.project_id.property_owner_partner_id.id,
                    'type_id': self.type_id.id,
                    'agent_commission': self.project_id.agent_commission,
                    'sales_commission': self.project_id.sales_commission,

                })
        self.creation_done =True

    def action_view_units(self):
        return {
            'name': 'Property Units',
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form',
            'view_type': 'list',
            'res_model': 'property.unit',
            'domain': [('project_id', '=', self.project_id.id),('type_id','=',self.type_id.id)],
        }

    def _compute_total_units(self):
        for rec in self:
            units = self.env['property.unit'].sudo().search(
                [('project_id', '=', rec.project_id.id),('type_id','=',rec.type_id.id),('status','=','available')])
            if units:
                rec.available_units = len(units)
            else:
                rec.available_units = 0

    def _compute_total_property_units(self):
        for rec in self:
            units = self.env['property.unit'].sudo().search(
                [('project_id', '=', rec.project_id.id),('type_id','=',rec.type_id.id)])
            if units:
                rec.total_property_units = len(units)
            else:
                rec.total_property_units = 0

    def _compute_total_area(self):
        for rec in self:
            units = self.env['property.unit'].sudo().search(
                [('project_id', '=', rec.project_id.id),('status','=','available'),
                 ('type_id', '=', rec.type_id.id)])
            if units:
                rec.total_area = sum(units.mapped('total_area'))
            else:
                rec.total_area = 0.0


class PropertyProjectType(models.Model):
    _name = 'property.project.type'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _description = 'Property Type'
    _order = 'sequence desc'

    sequence = fields.Integer(
        string="Sequence"
    )
    name = fields.Char(
        string="Name",
        tracking=True
    )

    category_id = fields.Selection([
        ('residential','Residential'),
        ('commercial','Commercial'),
        ('industrial', 'Industrial')],
        string="Category",
        default='residential',
        tracking=True
    )


class PropertyOtherFees(models.Model):
    _name = 'property.other.fees'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _description = 'Other Fees'
    _order = 'sequence desc'

    sequence = fields.Integer(
        string="Sequence"
    )

    name = fields.Char(
        string="Name"
    )
    product_id = fields.Many2one(
        'product.product',
        string="Product",
        domain=[('other_fee_property', '=', True)]
    )

    percentage = fields.Float(
        string="Percentage"
    )

    fixed_amount =fields.Float(
        string="Fixed Amount"
    )

    property_id = fields.Many2one(
        'property.project',
        string="Project",
        tracking=True
    )

    is_oqood = fields.Boolean(
        string="Is Oqood",
        default=False,
    )

    is_title_deed = fields.Boolean(
        string="Is Title Deed",
        default=False,
    )


    @api.onchange('percentage')
    def _on_change_percentage(self):
        if self.fixed_amount > 0.0 and self.percentage>0.0:
            self.fixed_amount = 0.0

    @api.onchange('fixed_amount')
    def _on_change_fixed_amount(self):
        if self.percentage > 0.0 and self.fixed_amount >0.0:
            self.percentage = 0.0



class PropertyPriceUpdate(models.Model):
    _name = 'property.price.update'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'project_id'
    _description = 'Price Update'
    _order = 'sequence desc'

    sequence = fields.Integer(
        string="Sequence"
    )

    project_id = fields.Many2one(
        'property.project',
        string="Project",
        required=True,
        readonly=True
    )

    user_id = fields.Many2one(
        'res.users',
        string="User",
        default=lambda self: self.env.user,
        tracking=True
    )

    date_updated = fields.Date(
        string="Update Date",
        default=fields.Date.context_today,

    )

    property_unit_ids = fields.Many2many(
        'property.unit',
        string="Units"
    )
    price_type = fields.Selection([
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount')
    ], required=True,
        default='percentage')

    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id
    )

    percentage_value = fields.Float("Percentage (%)")
    fixed_value = fields.Monetary("Fixed Amount")
    type_percentage = fields.Selection(
        [('decrease', 'Decrease'),
         ('increase', 'Increase')
         ],
        string="Percentage Type"
    )

    property_unit_price = fields.One2many(
        'property.price.unit.history',
        'price_update_id',
        string="Price Unit Updated",
    )

class PropertyUnitPriceHistory(models.Model):
    _name = 'property.price.unit.history'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'property_unit_id'
    _description = 'Price History'
    _order = 'sequence desc'

    sequence = fields.Integer(
        string="Sequence"
    )

    price_update_id = fields.Many2one(
        'property.price.update',
        string="Price Update"
    )

    project_id = fields.Many2one(
        'property.project',
        string="Project",
        required=True,
        readonly=True
    )

    property_unit_id = fields.Many2one(
        'property.unit',
        string="Unit"
    )

    user_id = fields.Many2one(
        'res.users',
        string="User",
        default=lambda self: self.env.user,
        tracking=True
    )

    date_updated = fields.Date(
        string="Update Date",
        default=fields.Date.context_today,
    )

    old_value = fields.Float(
        string="Old Value"
    )

    current_value = fields.Float(
        string="Current Value"
    )

class PropertyDiscountDirectDownPayment(models.Model):
    _name = 'property.discount.direct.down.payment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'down_payment'
    _description = 'Direct Down Payment Discount'

    property_project_id = fields.Many2one(
        'property.project',
        string="Project",
        tracking=True
    )
    sequence = fields.Integer(
        string="Sequence"
    )

    down_payment = fields.Float(
        string="Down Payment",
        default=0.0
    )

    allowed_percentage = fields.Float(
        string="Discount Percentage",
        default=0.0
    )

class PropertyDiscountDirectPaymentPlan(models.Model):
    _name = 'property.discount.direct.payment.plan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'payment_plan_id'
    _description = 'Direct Payment Plan Discount'

    property_project_id = fields.Many2one(
        'property.project',
        string="Project",
        tracking=True
    )
    sequence = fields.Integer(
        string="Sequence"
    )

    allowed_payment_plan_ids = fields.Many2many(
        'property.payment.plan',
        readonly=True,
        compute='_compute_allowed_payment_plan_ids'
    )

    payment_plan_id = fields.Many2one(
        'property.payment.plan',
        string="Payment Plan",
        domain='[("property_project_id", "in", property_project_id)]',
    )

    allowed_percentage = fields.Float(
        string="Discount Percentage",
        default=0.0
    )

    @api.depends('property_project_id','payment_plan_id','allowed_percentage','sequence')
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

class PropertyDiscountInDirectPaymentPlan(models.Model):
    _name = 'property.discount.indirect.payment.plan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'payment_plan_id'
    _description = 'In Direct Payment Plan Discount'

    property_project_id = fields.Many2one(
        'property.project',
        string="Project",
        tracking=True
    )

    sequence = fields.Integer(
        string="Sequence"
    )

    allowed_payment_plan_ids = fields.Many2many(
        'property.payment.plan',
        readonly=True,
        compute='_compute_allowed_payment_plan_ids'
    )

    payment_plan_id = fields.Many2one(
        'property.payment.plan',
        string="Payment Plan",
        domain='[("property_project_id", "in", property_project_id)]',
    )

    allowed_percentage = fields.Float(
        string="Discount Percentage",
        default=0.0
    )

    @api.depends('property_project_id','payment_plan_id','allowed_percentage','sequence')
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



class PropertyDiscountInDirectDownPayment(models.Model):
    _name = 'property.discount.indirect.down.payment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'down_payment'
    _description = 'In Direct Down Payment Discount'

    property_project_id = fields.Many2one(
        'property.project',
        string="Project",
        tracking=True
    )

    sequence = fields.Integer(
        string="Sequence"
    )

    down_payment = fields.Float(
        string="Down Payment",
        default=0.0
    )

    allowed_percentage = fields.Float(
        string="Discount Percentage",
        default=0.0
    )