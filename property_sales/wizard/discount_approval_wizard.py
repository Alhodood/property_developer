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
from odoo import models, fields,_
from odoo.exceptions import UserError

class DiscountRequestWizard(models.TransientModel):
    _name = 'discount.request.wizard'
    _description = "Discount Request Wizard"

    sale_order = fields.Many2one(
        'sale.order',
        string="Sales Offer",
        readonly=True
    )

    reason_for_request = fields.Text(
        string="Reason For Request"
    )

    request_percentage = fields.Float(
        string="Request Percentage"
    )

    def action_request_for_discount(self):
        discount_request = self.env['sale.discount.approval.request'].create({
            'sale_order_id':self.sale_order.id,
            'approval_user_ids':self.sale_order.property_project_id.discount_approvers_ids.ids,
            'discount_percent':self.request_percentage,
            'reason_for_request':self.reason_for_request,
        })
        self.sale_order.request_for_approval =True
        self.sale_order.discount_status ='waiting'
        approvers = self.sale_order.property_project_id.discount_approvers_ids.filtered(
            lambda u: u.partner_id.email
        )

        if self.env.user.partner_id.email and approvers:
            base_url = self.env['ir.config_parameter'].sudo().get_param(
                'web.base.url')
            record_url = f"{base_url}/web#id={discount_request.id}&model={discount_request._name}&view_type=form"
            email_to = ",".join(approvers.mapped('partner_id.email'))
            body_html = f"""
                    <p>Hi,</p>
                    <p>
                        The <strong>Discount Approval Request</strong> has been submitted
                      for the following offer by  {self.env.user.name}.
                    </p>
                      <ul>
                            <li><strong>Customer:</strong> {self.sale_order.partner_id.name}</li>
                            <li><strong>Property:</strong> {self.sale_order.property_project_id.name}</li>
                            <li><strong>Unit:</strong> {self.sale_order.property_unit_id.name}</li>
                            <li><strong>Offer:</strong> {self.sale_order.name}</li>
                            <li><strong>Requested Discount:</strong> {self.request_percentage}%</li>
                            <li><strong>Reason:</strong> {self.reason_for_request}</li>
                     </ul>

                      <p>
                                 Kindly review the request and take the necessary action.
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
                           View Discount Request
                        </a>
                        </p>
                    <p>
                        Best regards,<br/>
                      {self.env.user.name}<br/>
                    </p>
              """
            subject = _('Discount Approval Request For Offer -%s') % (
                self.sale_order.name)
            main_content = {
                'subject': subject,
                'author_id': self.env.user.partner_id.id,
                'body_html': body_html,
                'email_to': email_to,
            }
            self.env['mail.mail'].sudo().create(main_content).send()





