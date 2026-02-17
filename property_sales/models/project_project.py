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
from odoo import fields,models,api,_
from odoo.exceptions import UserError
#
# class Project(models.Model):
#     _inherit = 'project.project'
#
#     is_construction = fields.Boolean(
#         string="Is Construction",
#         default=False,
#     )
#     is_create_property = fields.Boolean(
#         string="Is Create Property",
#         default=False
#     )
#
#     schedule_line_ids = fields.One2many(
#         'invoice.schedule.line',
#         'project_id',
#         string='Invoice Schedules'
#     )
#
#     advance_percentage = fields.Float("Advance %")
#     advance_amount = fields.Float("Advance Amount")
#
#     retention_percentage = fields.Float("Retention %")
#     retention_amount = fields.Float("Retention Amount")
#     retention_reminder = fields.Date("Retention Date")
#
#     is_advance_added_in_line = fields.Boolean(
#         string="Is Advance Added in Line",
#         compute="_compute_advance_retention_added",
#         store=True,
#     )
#
#     is_retention_added_in_line = fields.Boolean(
#         string="Is Retention Added in Line",
#         compute="_compute_advance_retention_added",
#         store=True,
#     )
#     project_register_name = fields.Char(
#         string="RERA Project Reg. No."
#     )
#
#     project_value =fields.Float(
#         string="Project Value",
#     )
#
#     rera_info = fields.Text(
#         string="Rera Details",
#         tracking=True,
#         copy=False,
#     )
#
#     license_project = fields.Char(
#         string="License",
#         tracking=True,
#         copy=False
#     )
#
#     project_managed = fields.Many2many(
#         'res.partner',
#         string="Projects managed",
#
#     )
#
#     type_id = fields.Selection([
#         ('residential','Residential'),
#         ('commercial','Commercial')
#     ],string="Project Type")
#
#     project_sequence = fields.Char(
#         string='Sequence',
#         tracking=True
#     )
#
#     street1 = fields.Char(
#         string="Street1",
#         tracking=True
#     )
#     street2 = fields.Char(
#         string="Street2",
#         tracking=True
#     )
#     town_ship = fields.Char(
#         string="Township",
#         tracking=True
#     )
#     city = fields.Char(
#         string="City",
#         tracking=True
#     )
#     country_id = fields.Many2one(
#         'res.country',
#         string="Country",
#         tracking=True
#     )
#     state_id = fields.Many2one(
#         'res.country.state',
#         string="State",
#         domain="[('country_id', '=', country_id)]",
#         tracking=True
#     )
#
#     zip = fields.Char(
#         string="Zip",
#         tracking=True
#     )
#     latitude = fields.Float(
#         string="Latitude",
#         digits=(16, 8),
#         tracking=True
#     )
#     longitude = fields.Float(
#         string="Longitude",
#         digits=(16, 8),
#         tracking=True
#     )
#
#     location_url = fields.Char(
#         string="Location Url",
#         tracking=True
#     )
#
#     property_type_id = fields.Many2one(
#         comodel_name='property.project.type',
#         string="Property Type",
#         tracking=True
#     )
#
#
#     property_unit_available_ids = fields.One2many(
#         comodel_name='project.unit.available',
#         inverse_name='project_id',
#         string="Property Unit Available"
#     )
#
#     has_invoiced_normal_lines = fields.Boolean(
#         string="Has Invoiced Normal Lines",
#         compute="_compute_has_invoiced_normal_lines",
#         store=True,
#     )
#
#     construction_completion_date = fields.Date(
#         string="Construction Completion Date"
#     )
#
#     construction_completed = fields.Boolean(
#         string="Construction Completed",
#         default=False,
#     )
#
#     @api.depends('schedule_line_ids.is_invoiced',
#                  'schedule_line_ids.is_advance',
#                  'schedule_line_ids.is_retention')
#     def _compute_has_invoiced_normal_lines(self):
#         for rec in self:
#             # Get project lines excluding advance and retention
#             normal_lines = rec.schedule_line_ids.filtered(
#                 lambda l: not l.is_advance and not l.is_retention
#             )
#             # Check if any is invoiced
#             rec.has_invoiced_normal_lines = any(normal_lines.mapped('is_invoiced'))
#
#     @api.onchange('advance_percentage')
#     def _onchange_adv_progress(self):
#         if self.project_value:
#             self.advance_amount = (self.project_value * self.advance_percentage) / 100
#
#     @api.onchange('project_value')
#     def _onchange_prj_value(self):
#         self.advance_amount = 0
#         self.advance_percentage = 0
#         self.retention_amount = 0
#         self.retention_percentage = 0
#
#     def action_complete_construction(self):
#         self.construction_completed = True
#
#     @api.onchange('advance_amount')
#     def _onchange_advance_amount(self):
#         if self.project_value:
#             self.advance_percentage = (self.advance_amount / self.project_value) * 100
#
#     def action_advance_wizard(self):
#         if self.project_value<=0:
#             raise UserError("Set Project Value")
#         if self.advance_percentage<=0 or self.is_advance_added_in_line:
#             raise UserError("Set Advance Percentage")
#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'Advance',
#             'res_model': 'advance.retention.wizard',
#             'view_mode': 'form',
#             'target': 'new',
#             'context': {
#                 'default_project_id': self.id,
#                 'default_is_advance': True,
#                 'default_amount': self.advance_amount,
#                 'default_date': fields.Date.today(),
#             }
#         }
#
#     @api.depends('schedule_line_ids')
#     def _compute_advance_retention_added(self):
#         for rec in self:
#             rec.is_advance_added_in_line = False
#             rec.is_retention_added_in_line = False
#
#             for line in rec.schedule_line_ids:
#                 if line.is_advance:
#                     rec.is_advance_added_in_line = True
#                 if line.is_retention:
#                     rec.is_retention_added_in_line = True
#
#     @api.onchange('retention_percentage')
#     def _onchange_ret_progress(self):
#         if self.project_value:
#             self.retention_amount = (self.project_value * self.retention_percentage) / 100
#
#
#     @api.onchange('retention_amount')
#     def _onchange_retention_amount(self):
#         if self.project_value:
#             self.retention_percentage = (self.retention_amount / self.project_value) * 100
#
#     def action_notify_handover(self):
#         self.ensure_one()
#         return {
#             'name': 'Notify Handover',
#             'type': 'ir.actions.act_window',
#             'res_model': 'project.handover.notify.wizard',
#             'view_mode': 'form',
#             'target': 'new',
#             'context': {
#                 'default_project_id': self.id,
#             }
#         }
#
#     def action_retention_wizard(self):
#         if not self.retention_reminder:
#             raise UserError("Set Reminder Date")
#         if self.project_value<=0:
#             raise UserError("Set Project Value")
#         if self.retention_percentage<=0 or self.is_retention_added_in_line:
#             raise UserError("Set Retention Percentage")
#         valid_lines = self.schedule_line_ids.filtered(
#             lambda l: not l.is_advance
#                       and not l.is_retention
#         )
#         total_progress = sum(valid_lines.mapped('actual_progress'))
#         if total_progress != 100:
#             raise UserError(
#                 f"Total Actual Progress must be 100%. "
#                 f"Current total is {total_progress:.2f}%."
#             )
#
#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'Retention',
#             'res_model': 'advance.retention.wizard',
#             'view_mode': 'form',
#             'target': 'new',
#             'context': {
#                 'default_project_id': self.id,
#                 'default_is_retention': True,
#                 'default_amount': self.retention_amount,
#                 'default_date': fields.Date.today(),
#             }
#         }
#
#     def action_create_property(self):
#         property_unit_available_ids =[]
#         for line in self.property_unit_available_ids:
#             property_unit_available_ids.append((0, 0, {
#                 'type_id': line.type_id.id,
#                 'number_of_unit': line.number_of_unit,
#                 'area_sqft': line.area_sqft,
#             }))
#         self.env['property.project'].sudo().create({
#             'name':self.name,
#             'street1':self.street1,
#             'street2':self.street2,
#             'town_ship':self.town_ship,
#             'city':self.city,
#             'country_id':self.country_id.id,
#             'state_id':self.state_id.id,
#             'zip':self.zip,
#             'latitude':self.latitude,
#             'longitude':self.longitude,
#             'location_url':self.location_url,
#             'property_owner_id':self.user_id.id,
#             'property_manager_id':self.user_id.id,
#             'property_owner_partner_id':self.user_id.partner_id.id,
#             'company_id':self.company_id.id if self.company_id else self.env.company.id,
#             'property_type_id':self.property_type_id.id,
#             'analytic_account_id':self.account_id.id,
#             'project_register_name':self.project_register_name,
#             'property_unit_summary_ids':property_unit_available_ids,
#             'is_created_from_pr':True,
#             'project_con_id':self.id,
#         })
#         self.sudo().is_create_property = True
#
#     def action_open_property_sales(self):
#         return {
#             'name': _('Properties'),
#             'domain': [('project_con_id', '=', self.id)],
#             'res_model': 'property.project',
#             'type': 'ir.actions.act_window',
#             'view_id': False,
#             'view_mode': 'list,form',
#         }
#
#
#     def send_retention_reminder_mail(self):
#         projects = self.env['project.project'].sudo().search([])
#         for project in projects:
#             if fields.Date.today() == project.retention_reminder:
#                 subject = f"Retention Reminder - {project.name}"
#                 body = f"""
#                     <p>Dear {project.user_id.name},</p>
#
#                     <p>This is a reminder that the retention date for the project
#                     <strong>{project.name}</strong> is <strong>{project.retention_reminder}</strong>.</p>
#
#                     <p><strong>Retention Amount:</strong> {project.retention_amount}</p>
#
#                     <p>Regards,<br/>{self.env.user.name}</p>
#                 """
#
#                 mail_values = {
#                     'subject': subject,
#                     'body_html': body,
#                     'email_to': project.user_id.email,
#                     'email_from': self.env.user.email,
#                 }
#
#                 mail = self.env['mail.mail'].create(mail_values)
#                 mail.send()
#
#
# class ProjectUnitAvailable(models.Model):
#     _name = 'project.unit.available'
#     _inherit = ['mail.thread', 'mail.activity.mixin']
#     _rec_name = 'type_id'
#     _description = 'Project Unit Available'
#     _order = 'id desc'
#
#     type_id = fields.Many2one(
#         'property.unit.type',
#         string="Type"
#     )
#
#     number_of_unit = fields.Integer(
#         string="Number Of Unit"
#     )
#
#     area_sqft = fields.Float(
#         string="Area(Sqft)"
#     )
#
#     project_id = fields.Many2one(
#         'project.project',
#         string="Project",
#         tracking=True
#     )
#
#     @api.onchange('type_id', 'project_id')
#     def _onchange_type_project_warning(self):
#         if self.type_id and self.project_id:
#             exists = self.env['project.unit.available'].search([
#                 ('type_id', '=', self.type_id.id),
#                 ('project_id', '=', self.project_id._origin.id),
#                 ('id', '!=', self.id),
#             ])
#             if exists:
#                 raise UserError(
#                     "Type Already Added !!")


class ProjectTask(models.Model):
    _inherit = 'project.task'

    is_oqood = fields.Boolean(
        string="Is Oqood",
    )

    oqood_id = fields.Many2one(
        'oqood.registration',
        string="Oqood Registration"
    )