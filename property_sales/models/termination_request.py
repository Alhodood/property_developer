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
from odoo.exceptions import UserError
from odoo import fields, models, _, api


class TerminationRequest(models.Model):
    _name = 'termination.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'sequence'
    _description = 'Termination Request'
    _order = 'id desc'

    sequence = fields.Char(
        string="Sequence",

    )

    reason_for_termination = fields.Html(
        string="Reason for Termination"
    )

    project_progress_percentage = fields.Float(
        string="Project Progress Percentage",
        tracking=True
    )


    pending_progress_percentage = fields.Float(
        string="Pending Progress Percentage",
        tracking=True
    )


    termination_type = fields.Char(
        string="Termination type",
        tracking=True
    )

    request_date = fields.Date(
        string="Request Date",
        default=fields.Date.context_today,
        tracking=True
    )

    property_project_id = fields.Many2one(
        'property.project',
        string="Property Project",
        tracking=True
    )

    property_unit_id = fields.Many2one(
        'property.unit',
        string="Property Unit",
        domain='[("project_id", "=", property_project_id),("status","=","sold")]',
        tracking=True
    )

    spa_id = fields.Many2one(
        'spa.book',
        string="Spa",
        tracking=True,
        related='property_unit_id.spa_id'
    )

    user_id = fields.Many2one(
        'res.users',
        default=lambda self: self.env.user,
        tracking=True
    )

    status = fields.Selection(
        [('new','New'),
         ('under_review','Under Review'),
         ('review_completed','Review Completed'),
         ('terminate','Terminate'),
         ('cancel','Cancel')
         ],
        string="Status",
        default='new'
    )

    partner_id = fields.Many2one(
        'res.partner',
        string="Buyer",
        related='spa_id.partner_id',
        domain="[('par_type', '=', 'lead')]",
        store=True
    )

    company_id = fields.Many2one(
        'res.company',
        string="Company",
        tracking=True,
        related="spa_id.company_id",
    )

    @api.model
    def create(self, vals):
        res = super(TerminationRequest, self).create(vals)
        seq = self.env['ir.sequence'].next_by_code('property.termination.sequence')
        res.sequence = seq
        return res

    def action_under_review(self):
        self.write({'status': 'under_review'})

    def action_review_completed(self):
        self.write({'status': 'review_completed'})

    def action_terminate(self):
        self.write({'status': 'terminate'})
        self.property_unit_id.sudo().status = 'available'
        self.property_unit_id.sudo().spa_id = False
        self.property_unit_id.sudo().buyer_id = False

    def action_cancel(self):
        self.write({'status': 'cancel'})

    def action_notify_buyer(self):
        self.ensure_one()
        template = self.env.ref(
            'property_sales.email_template_termination_notify',
            raise_if_not_found=False
        )
        if not template:
            raise UserError(_('Email template not found'))

        compose_form_id = self.env.ref(
            'mail.email_compose_message_wizard_form'
        ).id

        return {
            'type': 'ir.actions.act_window',
            'name': _('Notify Termination'),
            'res_model': 'mail.compose.message',
            'view_mode': 'form',
            'target': 'new',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'context': {
                'default_model': 'termination.request',
                'default_res_ids': [self.id],
                'default_use_template': True,
                'default_template_id': template.id if template else False,
                'default_composition_mode': 'comment',
                'force_email': True,
                'mark_send_link_approved': True,
                'default_email_from': self.user_id.email or self.env.user.company_id.email,
                'default_partner_ids': [
                    self.partner_id.id] if self.partner_id else [],
            }
        }