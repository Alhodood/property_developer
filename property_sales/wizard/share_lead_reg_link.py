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
from odoo import models, fields, api

class ShareLeadLinkWizard(models.TransientModel):
    _name = 'share.lead.reg.wizard'
    _description = 'Share Lead Link Wizard'

    partner_ids = fields.Many2many(
        'res.partner',
        string="Send To"
    )

    record_url = fields.Char(
        string="Record Link",
        readonly=True
    )

    record_url_html = fields.Html(
        string="Link",
        compute="_compute_record_url_html",
        sanitize=False
    )

    def _compute_record_url_html(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url = f"{base_url}/lead/register"

        for rec in self:
            rec.record_url = url
            rec.record_url_html = f"""
                    <div style="display:flex;gap:6px;">
                        <input type="text"
                               value="{url}"
                               id="copy_link_input"
                               readonly="readonly"
                               style="width:300px !important;padding:6px;" />

                        <button type="button"
                                style="padding:6px 12px;
                                       background:#875A7B;
                                       color:#fff;
                                       border:none;
                                       border-radius:4px;
                                       cursor:pointer;"
                                onclick="
                                    var el=document.getElementById('copy_link_input');
                                    el.select();
                                    document.execCommand('copy');
                                    this.innerText='Copied!';
                                ">
                            Copy
                        </button>
                    </div>
                """

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)

        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        res['record_url'] = f"{base_url}/lead/register"

        return res

    def action_send_link(self):
        self.ensure_one()

        template = self.env.ref(
            'property_sales.mail_template_lead_registration',
            raise_if_not_found=False
        )

        if not template or not self.partner_ids:
            return

        email_to = ','.join(self.partner_ids.mapped('email'))

        template.send_mail(
            self.id,
            force_send=True,
            email_values={
                'email_to': email_to,
            }
        )
