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


class PropertyBlockingRequest(models.TransientModel):
    _name = 'property.blocking.request'
    _description = "Property Blocking"

    property_project_id = fields.Many2one(
        'property.project',
        string="Project",
        tracking=True
    )
    crm_id = fields.Many2one(
        'crm.lead',
        string="Crm",
        tracking=True,
    )

    sale_order = fields.Many2one(
        'sale.order',
        string="Sale Order"
    )

    property_unit_id = fields.Many2one(
        'property.unit',
        string="Unit",
        domain='[("project_id", "=", property_project_id),("status","=","available")]',
    )

    created_by = fields.Many2one(
        'res.users',
        string="Created By",
        tracking=True,
        default=lambda self: self.env.user,
    )

    user_id = fields.Many2one(
        'res.users',
        string="Sales Person",
        tracking=True,
        default=lambda self: self.env.user,
    )

    partner_id = fields.Many2one(
        'res.partner',
        string="Client",
        tracking=True,
    )

    request = fields.Text(
        string="Request",
        tracking=True,
    )

    def action_add_done(self):
        blocking_request = self.env['blocking.request'].sudo().create({
            'crm_id':self.crm_id.id,
            'sale_order':self.sale_order.id,
            'partner_id':self.partner_id.id,
            'property_project_id':self.property_project_id.id,
            'property_unit_id':self.property_unit_id.id,
            'user_id':self.user_id.id,
            'created_by':self.created_by.id,
            'request':self.request,
        })
        groups = [
            'property_sales.group_admin_blocking',
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
                record_url = f"{base_url}/web#id={blocking_request.id}&model={blocking_request._name}&view_type=form"
                body_html = f"""
                                <p>Dear {user.name},</p>
                                <p>
                                    A <strong>Property Unit Blocking Request</strong> has been created with the following details:
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
                                        Property Sales Team
                                    </p>
                                """
                subject = _('Unit Blocking Request-%s') % (self.property_unit_id.name)
                main_content = {
                    'subject': subject,
                    'author_id': self.env.user.partner_id.id,
                    'body_html': body_html,
                    'email_to': user.partner_id.email,
                }
                self.env['mail.mail'].sudo().create(main_content).send()






