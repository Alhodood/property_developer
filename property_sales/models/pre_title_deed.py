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


class PreTitleDeed(models.Model):
    _name = 'pre.title.deed'
    _inherit = ['mail.thread','mail.activity.mixin']
    _rec_name = 'sequence'
    _description = 'Pre Title Deed'
    _order = 'id desc'

    sequence = fields.Char(
        string="Sequence",
    )

    state = fields.Selection(
        selection=[
            ('not_applied', 'Not Applied'),
            ('in_progress', 'In Progress'),
            ('issued', 'Issued'),
        ],
        string="Status",
        default='not_applied',
        tracking=True
    )

    dld_reference_no = fields.Char(
        string="DLD Reference Number",
        tracking=True
    )

    issue_date = fields.Date(
        string="Issue Date",
        tracking=True
    )

    oqood_id = fields.Many2one(
        'oqood.registration',
        string="Oqood",
        tracking=True
    )

    client_id = fields.Char(
        string="Client ID",
        tracking=True
    )

    spa_id = fields.Many2one(
        'spa.book',
        string="SPA",
        domain=[('status', '=', "general_manager_approved")],
        related='oqood_id.spa_id'
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

    crm_user_id = fields.Many2one(
        'res.users',
        string="Crm User",
        default=lambda self: self.env.user,
    )

    partner_id = fields.Many2one(
        'res.partner',
        string="Buyer",
        related='spa_id.partner_id',
        domain="[('par_type', '=', 'lead')]",
    )

    client_sign_date = fields.Date(
        string="Client Sign Date",
        tracking=True
    )

    chairman_sign_date = fields.Date(
        string="Chair Man Sign Date",
        tracking=True
    )

    @api.model
    def create(self, vals):
        res = super(PreTitleDeed, self).create(vals)
        seq = self.env['ir.sequence'].next_by_code('pre.title.deed.sequence')
        res.sequence = seq
        return res

    def action_set_in_progress(self):
        for rec in self:
            rec.state = 'in_progress'

    def action_set_issued(self):
        for rec in self:
            rec.state = 'issued'



