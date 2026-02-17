# -*- coding: utf-8 -*-
#############################################################################

#    Alhodood Technologies.
#
#    Copyright (C) 2024-TODAY Alhodood Technologies(<https://www.alhodood.com>)
#    Author: Alhodood Technologies(<https://www.alhodood.com>)
#
#    You can modify it under the terms of the GNU Affero General Public License (AGPL v3), Version 3.
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
from odoo import fields, models, _


class ProjectHandoverNotifyWizard(models.TransientModel):
    _name = 'project.handover.notify.wizard'
    _description = 'Notify Project Handover'

    project_id = fields.Many2one(
        'project.project',
        string="Project",
        required=True,
        readonly=True
    )

    unit_ids = fields.Many2many(
        'property.unit',
        string="Units",
        domain = "[('project_con_id', '=', project_id),"
                 "('snagging_completed','=',True),"
                 "('handover_completed','=',False)]",
    )

    def action_send_notification(self):
        for unit in self.unit_ids:
            spa = self.env['spa.book'].sudo().search([
                ('property_unit_id', '=', unit.id),
                ('status', '=', 'general_manager_approved')
            ], limit=1)

            if not spa:
                continue
            email_to = spa.partner_id.email
            email_cc = spa.crm_user_id.email if spa.crm_user_id else False
            if email_to:
                body_html = f"""
                                <p>Dear {spa.partner_id.name},</p>
                               <p>
                                We are pleased to inform you that the construction of your property  <strong>{unit.name}</strong>
                                 under the project {unit.project_id.name}   has been successfully completed.
                               </p>
                                   <p>
                                    The property is now ready for handover. Our CRM team will coordinate
                                    with you shortly to complete the handover process.
                                    </p>
                                   Thank you for your trust and cooperation
                                  </p>
                                   <p>
                                       Best regards,<br/>
                                       {self.env.company.name}
                                   </p>
                            """
                subject = _(
                    'Property Construction Completed – Handover Notification')
                main_content = {
                    'subject': subject,
                    'author_id': self.env.user.partner_id.id,
                    'body_html': body_html,
                    'email_to': email_to,
                    'email_cc': email_cc,
                }
                self.env['mail.mail'].sudo().create(main_content).send()
