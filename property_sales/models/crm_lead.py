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


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    property_type = fields.Selection(
        [
            ('sell', 'Sell')],
        string="Type",
        tracking=True
    )

    property_project_id = fields.Many2many(
        'property.project',
        'property_project_rel',
        'p_property_id',
        'p_lead_property_id',
        string="Property",
        tracking=True
    )

    property_unit_id = fields.Many2many(
        'property.unit',
        'property_uit_rel',
        'punit_id',
        'plead_id',
        string="Unit",
        domain='[("project_id", "in", property_project_id),("status","=","available")]',
    )


    client_budget = fields.Float(
        string="Client Budget"
    )

    client_budget_to = fields.Float(
        string="Client Budget To"
    )

    stage_type = fields.Selection(
        [('reserved', 'Reserved')],
        string="Type"
    )

    reserve_property = fields.Boolean(
        string="Reserve Property",
        default=False
    )

    crm_property_tagged_ids = fields.One2many(
        'crm.tagged.property',
        'crm_id',
        string="Property Tagged"
    )

    lead_agent_id = fields.Many2one(
        'res.partner',
        string="Agent",
        domain="[('par_type', '=', 'agent')]",
    )

    property_blocking_request_ids = fields.One2many(
        'blocking.request',
        'crm_id',
        string="Blocking Request"
    )

    quote_created = fields.Boolean(
        string="Quote Created",
        default=False
    )

    is_block_lead = fields.Boolean(
        string="Is Block Lead",
        default=False
    )

    block_type = fields.Selection(
        [('blocked','Unit Blocked')],
        string="Block Type"
    )

    def action_sale_order_creation(self):
        if self.property_unit_id:
            for unit in self.property_unit_id:
                sale_order = self.env['sale.order'].sudo().create({
                    'crm_lead_id': self.id,
                    'partner_id': self.partner_id.id,
                    'client_type': self.partner_id.client_type if self.partner_id.client_type else False,
                    'opportunity_id': self.id,
                    'campaign_id': self.campaign_id.id,
                    'medium_id': self.medium_id.id,
                    'origin': self.name,
                    'source_id': self.source_id.id,
                    'company_id': self.company_id.id or self.env.company.id,
                    'tag_ids': [(6, 0, self.tag_ids.ids)],
                    'property_project_id': unit.project_id.id,
                    'property_unit_id': unit.id,
                    'lead_agent_id': self.lead_agent_id.id,
                    'property_type':'broker',
                    'php':unit.php,
                })
                if self.team_id:
                    sale_order.sudo().team_id = self.team_id.id
                if self.user_id:
                    sale_order.sudo().user_id = self.user_id.id
            self.quote_created = True
            return {
                'name': 'Sales Offer',
                'type': 'ir.actions.act_window',
                'res_model': 'sale.order',
                'view_mode': 'list,form',
                'domain': [('crm_lead_id', '=', self.id)],
                'target': 'current',
                'context': {
                    'default_crm_lead_id': self.id,
                    'default_opportunity_id': self.id,
                    'default_partner_id': self.partner_id.id,
                }
            }
        else:
            sale_order = self.env['sale.order'].sudo().create({
                'crm_lead_id': self.id,
                'partner_id': self.partner_id.id,
                'client_type': self.partner_id.client_type if self.partner_id.client_type else False,
                'opportunity_id': self.id,
                'campaign_id': self.campaign_id.id,
                'medium_id': self.medium_id.id,
                'origin': self.name,
                'source_id': self.source_id.id,
                'company_id': self.company_id.id or self.env.company.id,
                'tag_ids': [(6, 0, self.tag_ids.ids)],
                'lead_agent_id': self.lead_agent_id.id,
                'property_type': 'broker',
            })
            if self.team_id:
                sale_order.sudo().team_id = self.team_id.id
            if self.user_id:
                sale_order.sudo().user_id = self.user_id.id
            self.quote_created = True
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'sale.order',
                'res_id': sale_order.id,
                'view_mode': 'form',
                'target': 'current',
            }


    @api.onchange('partner_id')
    def _onchange_partner(self):
        if self.partner_id.lead_agent_id:
            self.lead_agent_id = self.partner_id.lead_agent_id.id


    def action_property_reservation(self):
        block_request = self.env['blocking.request'].search([('crm_id','=',self.id),('status','=','draft')])
        if block_request:
            raise UserError(_('Already Have A Pending Request !!'))
        if not self.property_type == 'sell':
            raise UserError(_('Please choose sell property !!'))
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
                    'default_crm_id': self.id,
                    'default_property_project_id': self.property_project_id.id,
                    'default_property_unit_id': self.property_unit_id.id,
                    'default_user_id': self.user_id.id,
                    'default_partner_id': self.partner_id.id,
                            }

            }

    def action_view_booking_unit(self):
        booking_ids = self.env['offer.booking'].sudo().search(
            [('crm_id', '=', self.id)])
        if booking_ids:
            return {
                'name': 'Bookings',
                'view_type': 'list',
                'view_mode': 'list,form',
                'res_model': 'offer.booking',
                'domain': [('id', '=', booking_ids.ids)],
                'type': 'ir.actions.act_window',
                'context': {'default_crm_id': self.id,}
            }

    def action_view_blocking_request(self):
        blocking_ids = self.env['blocking.request'].sudo().search(
            [('crm_id', '=', self.id)])
        if blocking_ids:
            return {
                'name': 'Blocking Request',
                'view_type': 'list',
                'view_mode': 'list,form',
                'res_model': 'blocking.request',
                'domain': [('id', '=', blocking_ids.ids)],
                'type': 'ir.actions.act_window',
                'context': {'default_crm_id': self.id, }
            }




class CrmTaggedProperty(models.Model):
    _name = 'crm.tagged.property'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'property_unit_id'
    _description = 'Property Tagged'
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
        domain='[("project_id", "=", property_project_id),("status","=","available")]',
    )

    currency_id = fields.Many2one(
        'res.currency',
        string="Currency",
        tracking=True,
        related='property_unit_id.currency_id',
        readonly=True
    )

    type_id = fields.Many2one(
        'property.unit.type',
        string="Unit Type",
        tracking=True,
        related='property_unit_id.type_id',
    )

    total_size = fields.Float(
        string="Total Size (Sqft)",
        tracking=True,
        related='property_unit_id.total_size',
    )

    php = fields.Monetary(
        string="PHP",
        currency_field='currency_id',
        related='property_unit_id.php',
    )


