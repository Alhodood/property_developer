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
from odoo.exceptions import ValidationError

class KeyHandover(models.Model):
    _name = 'key.handover'
    _inherit = ['mail.thread','mail.activity.mixin']
    _rec_name = 'sequence'
    _description = 'KEY HANDOVER'
    _order = 'id desc'

    sequence = fields.Char(
        string="Sequence",
    )

    status = fields.Selection([
        ('draft', 'Draft'),
        ('initiated', 'Initiated'),
        ('completed', 'Completed'),],
        string="Status",
        default='draft',
        tracking=True,
    )

    snagging_id = fields.Many2one(
        'snagging.unit',
        string="Snagging",
        domain=[('status', '=', "general_manager_approved")],
    )

    oqood = fields.Many2one(
        'oqood.registration',
        string="Oqood Registration",

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
    property_project_id = fields.Many2one(
        'property.project',
        string="Project",
        tracking=True,
        related = 'spa_id.property_project_id',
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
        domain="[('project_id', '=', property_project_id),"
               "('snagging_completed','=',True),"
               "('handover_completed','=',False)]",
    )
    crm_user_id = fields.Many2one(
        'res.users',
        string="Crm User",
        default=lambda self: self.env.user,
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


    @api.onchange('snagging_id')
    def on_change_snagging(self):
        self.spa_id = self.snagging_id.spa_id.id

    def action_complete(self):
        self.status = "completed"

    def action_initiate_handover(self):
        self.status = 'initiated'

    @api.model
    def create(self, vals):
        res = super(KeyHandover, self).create(vals)
        seq = self.env['ir.sequence'].next_by_code('key.handover.sequence')
        res.sequence = seq
        return res

    @api.constrains('snagging_id')
    def _check_unique_key_per_snagging_id(self):
        """Ensure only one SPA exists per Booking"""
        for record in self:
            if record.snagging_id:
                existing_key = self.search([
                    ('snagging_id', '=', record.snagging_id.id),
                    ('id', '!=', record.id)
                ], limit=1)
                if existing_key:
                    raise ValidationError(
                        _("A Key Handover already exists for this Booking (%s). You cannot create more than one Key Handover for the same booking.")
                        % record.offer_booking.display_name
                    )