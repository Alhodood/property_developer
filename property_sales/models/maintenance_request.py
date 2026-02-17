#############################################################################
#    Alhodood Technologies.
#    Copyright (C) 2024-TODAY Alhodood Technologies(<https://www.alhodood.com>)
#    Author: Alhodood Technologies(<https://www.alhodood.com>)
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

class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'

    property_type = fields.Selection(
        [('sale', 'Sale')],
        string="Property Type"
    )

    property_project_id = fields.Many2one(
        'property.project',
        string="Project",
        tracking=True
    )

    property_unit_id = fields.Many2one(
        'property.unit',
        string="Unit",
        tracking=True,
        domain='[("project_id", "=", property_project_id),'
               '("status","=","sold")]',
    )

    snagging_unit = fields.Many2one(
        'snagging.unit',
        string="Snagging Unit"
    )


    def write(self, vals):
        res = super(MaintenanceRequest, self).write(vals)
        if 'stage_id' in vals:
            for record in self:
                if record.stage_id.done and record.snagging_unit:
                    crm_user = record.snagging_unit.sudo().crm_user_id
                    if crm_user and crm_user.partner_id.email:
                        base_url = self.env[
                            'ir.config_parameter'].sudo().get_param(
                            'web.base.url')
                        record_url = f"{base_url}/web#id={record.snagging_unit.sudo().id}&model={record.snagging_unit.sudo()._name}&view_type=form"

                        subject = _(
                            'Maintenance Completed – Snagging %s') % (
                                      record.snagging_unit.sudo().sequence)
                        body_html = f"""
                            <p>Dear {crm_user.name},</p>
                            <p>
                                The maintenance request <strong>{record.name}</strong> for the snagging unit 
                                <strong>{record.snagging_unit.sudo().sequence}</strong> has been completed.
                            </p>
                            <ul>
                                <li><strong>Project:</strong> {record.property_project_id.name}</li>
                                <li><strong>Unit:</strong> {record.property_unit_id.name}</li>
                                <li><strong>Snagging Reference:</strong> {record.snagging_unit.sudo().sequence}</li>
                                <li><strong>Completed On:</strong> {record.write_date}</li>
                            </ul>
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
                                                  View Snagging
                                               </a>
                            </p>
                            <p>Best regards,<br/>{self.env.user.name}</p>
                        """

                        # Send email
                        self.env['mail.mail'].sudo().create({
                            'subject': subject,
                            'body_html': body_html,
                            'email_to': crm_user.partner_id.email,
                            'author_id': self.env.user.partner_id.id,
                        }).send()
        return res


