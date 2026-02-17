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
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import uuid

class RegAgent(models.Model):
    _name = 'reg.agent'
    _rec_name = 'sequence_code'
    _description = 'Agent Registration'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    sequence_code = fields.Char(string="Sequence", readonly=True)
    agent_reference =  fields.Char(string='Agent Ref',required=False)
    name = fields.Char(string='Agent Name', tracking=True)
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')

    registration_type = fields.Selection(
        [
            ('manual', 'Manual'),
            ('link', 'Link'),
        ],
        string='Registration Type',
        default='manual',
        tracking=True,
        required=True
    )

    status = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], default='draft', tracking=True)

    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)

    salesman_id = fields.Many2one('res.users', string='Salesman')
    registration_token = fields.Char(string='Registration Token', copy=False)

    # uploaded documents
    document_ids = fields.One2many('reg.agent.document', 'agent_id', string='Documents')

    documents_cont = fields.Integer(default=0,compute="_compute_doc_count")

    agent_description = fields.Text("Agent Description")

    reject_reason = fields.Text('Reject Reason')

    is_company = fields.Boolean(default=False)

    street = fields.Char(string="Street")
    street2 = fields.Char(string="Street 2")
    city = fields.Char(string="City")
    country_id = fields.Many2one('res.country', string="Country")
    state_id = fields.Many2one(
        'res.country.state',
        string="State",
        domain="[('country_id', '=', country_id)]"
    )

    person_company_id = fields.Many2one(
        'res.partner',
        string='Person Company',
        domain=lambda self: self._get_person_company_domain()
    )

    @api.model
    def _get_person_company_domain(self):
        """
        Returns a domain for person_company_id to:
        - Include partners that are companies
        - Exclude partners linked to res.company
        """
        # Get all partners linked to res.company
        res_company_partners = self.env['res.company'].sudo().search([])
        res_company_partners = res_company_partners.mapped('partner_id.id')
        # Return domain
        return [
            ('is_company', '=', True),
            ('id', 'not in', res_company_partners),
        ]

    zip = fields.Char(string="ZIP")

    def _compute_doc_count(self):
        self.documents_cont = len(self.document_ids)


    reject_reason = fields.Text(string='Reject Reason')

    def action_view_documents(self):
        return {
            'name': 'Documents',
            'type': 'ir.actions.act_window',
            'res_model': 'reg.agent.document',
            'view_mode': 'list,form',
            'domain': [('agent_id', '=', self.id)],
            'target': 'current',
        }

    @api.model
    def create(self, vals):
        rec = super().create(vals)
        rec.sequence_code = self.env['ir.sequence'].next_by_code('reg.agent')
        rec._generate_token()
        return rec

    def _generate_token(self):
        for rec in self:
            if not rec.registration_token:
                rec.registration_token = str(uuid.uuid4())

    def action_send_registration_link(self):
        """Open email wizard with registration link template."""
        self.ensure_one()

        template = self.env.ref(
            'time_agent_broker_reg.mail_template_agent_registration',
            raise_if_not_found=False
        )
        if not template:
            raise UserError(_('Email template not found'))

        compose_form_id = self.env.ref(
            'mail.email_compose_message_wizard_form'
        ).id

        ctx = {
            'default_model': 'reg.agent',
            'default_res_ids': [self.id],
            'default_use_template': True,
            'default_template_id': template.id,
            'default_composition_mode': 'comment',
            'force_email': True,
            'default_email_from': self.salesman_id.email or self.env.user.company_id.email,
            'mark_send_link_approved':True
        }
        return {
            'type': 'ir.actions.act_window',
            'name': _('Send Registration Email'),
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    def action_receive_submission(self):
        """Called when agent submits via portal: notify salesman (mail template triggers)."""
        for rec in self:
            rec.status = 'submitted'
            # send notification to salesman
            template = self.env.ref('time_agent_broker_reg.mail_template_submission_notify_salesman',
                                    raise_if_not_found=False)
            group = self.env.ref('time_agent_broker_reg.group_agent_reg')
            users = group.user_ids.filtered(lambda u: u.email)

            if template and users:
                email_to = ','.join(users.mapped('email'))

                template.send_mail(
                    rec.id,
                    force_send=True,
                    email_values={
                        'email_to': email_to,
                        'email_from': self.env.company.email or 'no-reply@example.com',
                    }
                )

    def action_approve(self):
        """Approve: create vendor (res.partner) and notify agent."""
        if not self.salesman_id or not self.agent_reference:
            missing_fields = []
            if not self.salesman_id:
                missing_fields.append('Salesman')
            if not self.agent_reference:
                missing_fields.append('Agent Ref')
            raise UserError("Missing Required Fields: %s" % ', '.join(missing_fields))

        required_docs = self.env['reg.document.type'].filtered('required')

        uploaded_doc_types = self.document_ids.mapped('doc_type_id')

        missing_docs = required_docs - uploaded_doc_types

        if missing_docs:
            raise UserError(
                "Missing required documents: %s"
                % ", ".join(missing_docs.mapped('name'))
            )
        partner_obj = self.env['res.partner']
        mail_tmpl = self.env.ref('time_agent_broker_reg.mail_template_agent_approved', raise_if_not_found=False)
        for rec in self:
            unverified = rec.document_ids.filtered(lambda d: d.verified != 'verified')
            if unverified:
                raise UserError("Some documents are not verified.")
            # create partner if not exists with same email
            partner = partner_obj.search([('email','=',rec.email)], limit=1)
            if not partner:
                partner = partner_obj.create({
                    'name': rec.name,
                    'phone': rec.phone,
                    'email': rec.email,
                    'user_id':self.salesman_id.id,
                    'par_type':'agent',
                    'company_type': 'company' if self.is_company else 'person',

                    'street': rec.street,
                    'street2': rec.street2,
                    'city': rec.city,
                    'state_id': rec.state_id.id if rec.state_id else False,
                    'zip': rec.zip,
                    'country_id': rec.country_id.id if rec.country_id else False,
                    'parent_id': rec.person_company_id.id if rec.person_company_id else False,
                })
            # mark as vendor (supplier)
            partner.write({'supplier_rank': 1})
            rec.status = 'approved'
            if mail_tmpl:
                mail_tmpl.send_mail(rec.id, force_send=True)

    def action_reject(self, reason=False):
        """Reject and notify."""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Reject Reason',
            'res_model': 'agent.document.reject.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_agent_id': self.id
            }
        }
