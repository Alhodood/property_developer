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

class DiscountApprovedWizard(models.TransientModel):
    _name = 'discount.approved.wizard'
    _description = "Discount Request Wizard"

    sale_order = fields.Many2one(
        'sale.order',
        string="Sales Offer",
        readonly=True
    )

    discount_request_id = fields.Many2one(
        'sale.discount.approval.request',
        string="Discount Request",
        readonly=True
    )

    reason_for_request = fields.Text(
        string="Reason"
    )


    def action_update_reason(self):
        self.sale_order.discount_approved =True
        self.sale_order.discount_status ='approved'
        self.sale_order.approved_reject_reason =self.reason_for_request
        self.sale_order.discount_approved_percentage = self.discount_request_id.discount_percent
        self.discount_request_id.approval_state = 'approved'
        self.discount_request_id.approved_user = self.env.user.id
        message = _(
            "Discount Request Approved by %s.\n Reason:%s"
        ) % (
                      self.env.user.name,
                      self.reason_for_request,
                  )

        self.discount_request_id.message_post(
            body=message,
        )
        self.sale_order.message_post(
            body=message,
        )
        if self.discount_request_id.requested_by.partner_id.email:
            base_url = self.env['ir.config_parameter'].sudo().get_param(
                'web.base.url')
            record_url = f"{base_url}/web#id={self.sale_order.id}&model={self.sale_order._name}&view_type=form"
            body_html = f"""
                    <p>Dear {self.discount_request_id.requested_by.name},</p>
                    <p>
                        The <strong>Discount Approval Request</strong> for the offer {self.sale_order.name}  has been approved
                       by  {self.env.user.name}.
                    </p>

                      <p>
                                 Kindly review the offer and take the necessary action.
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
            subject = _('Discount Request For Offer -%s - Approved ') % (
                self.sale_order.name)
            main_content = {
                'subject': subject,
                'author_id': self.env.user.partner_id.id,
                'body_html': body_html,
                'email_to': self.discount_request_id.requested_by.partner_id.email,
            }
            self.env['mail.mail'].sudo().create(main_content).send()


class DiscountRejectWizard(models.TransientModel):
    _name = 'discount.reject.wizard'
    _description = "Discount Reject Wizard"

    sale_order = fields.Many2one(
        'sale.order',
        string="Sales Offer",
        readonly=True
    )

    discount_request_id = fields.Many2one(
        'sale.discount.approval.request',
        string="Discount Request",
        readonly=True
    )

    reason_for_request = fields.Text(
        string="Reason"
    )

    def action_update_reason(self):
        self.sale_order.discount_approved = True
        self.sale_order.discount_status = 'rejected'
        self.sale_order.approved_reject_reason = self.reason_for_request
        self.sale_order.discount_approved_percentage = self.discount_request_id.discount_percent
        self.discount_request_id.approval_state = 'rejected'
        self.discount_request_id.approved_user = self.env.user.id
        message = _(
            "Discount Request Rejected by %s.\n Reason:%s"
        ) % (
                      self.env.user.name,
                      self.reason_for_request,
                  )

        self.discount_request_id.message_post(
            body=message,
        )
        self.sale_order.message_post(
            body=message,
        )
        if self.discount_request_id.requested_by.partner_id.email:
            base_url = self.env['ir.config_parameter'].sudo().get_param(
                'web.base.url')
            record_url = f"{base_url}/web#id={self.sale_order.id}&model={self.sale_order._name}&view_type=form"
            body_html = f"""
                            <p>Dear {self.discount_request_id.requested_by.name},</p>
                            <p>
                                The <strong>Discount Approval Request</strong> for the offer {self.sale_order.name}  has been rejected
                               by  {self.env.user.name}.
                            </p>

                              <p>
                                         Kindly review the offer and take the necessary action.
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
            subject = _('Discount Request For Offer -%s - Rejected ') % (
                self.sale_order.name)
            main_content = {
                'subject': subject,
                'author_id': self.env.user.partner_id.id,
                'body_html': body_html,
                'email_to': self.discount_request_id.requested_by.partner_id.email,
            }
            self.env['mail.mail'].sudo().create(main_content).send()








