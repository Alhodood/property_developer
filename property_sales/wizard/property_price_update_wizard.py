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
from odoo.exceptions import UserError


class ProjectHandoverNotifyWizard(models.TransientModel):
    _name = 'property.price.update.wizard'
    _description = 'Property Unit Price Update'

    project_id = fields.Many2one(
        'property.project',
        string="Project",
        required=True,
        readonly=True
    )

    apply_on = fields.Selection([
        ('all', 'All Units'),
        ('selected', 'Selected Units')
    ], default='selected', required=True)

    unit_status_ids = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('available', 'Available'),
            ('reserved', 'Blocked'),
            ('on_hold', 'On Hold'),
        ],
        string="Unit Status",
        required=True,
        default='available'
    )

    unit_type_id = fields.Many2one(
        'property.unit.type',
        string="Unit Type",

    )

    unit_ids = fields.Many2many(
        'property.unit',
        string="Units",
        domain="[('project_id','=',project_id),('type_id','=',unit_type_id)]"
    )

    price_type = fields.Selection([
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount')
    ], required=True,
    default='percentage')

    percentage_value = fields.Float("Percentage (%)")
    fixed_value = fields.Monetary("Fixed Amount")
    type_percentage = fields.Selection(
        [('decrease','Decrease'),
         ('increase','Increase')],
        string="Percentage Type"
    )
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id
    )

    def action_send_notification(self):
        if self.apply_on == 'all':
            if self.price_type == 'percentage':
                if self.percentage_value == 0.0:
                    raise UserError(
                        _("Please Choose the percentage greater than zero !!"))
                unit_ids =self.env['property.unit'].sudo().search([('project_id','=',self.project_id.id),
                                                                   ('type_id','=',self.unit_type_id.id),
                                                                   ('status','in',['draft','available','reserved','on_hold'])])
                property_price_id =self.env['property.price.update'].create({
                    'project_id':self.project_id.id,
                    'property_unit_ids':unit_ids.ids,
                    'price_type':'percentage',
                    'currency_id':self.currency_id.id,
                    'percentage_value':self.percentage_value,
                    'fixed_value':self.fixed_value,
                    'type_percentage':self.type_percentage,
                })
                for unit in unit_ids:
                    if self.type_percentage == 'decrease':
                        old_amount = unit.php
                        per_amount = (old_amount * self.percentage_value) /100
                        new_amount = old_amount - per_amount
                        unit.php = new_amount
                        property_price_unit_id = self.env['property.price.unit.history'].create({
                            'price_update_id': property_price_id.id,
                            'project_id': self.project_id.id,
                            'property_unit_id': unit.id,
                            'old_value':old_amount,
                            'current_value':new_amount,
                        })
                    if self.type_percentage == 'increase':
                        old_amount = unit.php
                        per_amount = (old_amount * self.percentage_value) / 100
                        new_amount = old_amount + per_amount
                        unit.php = new_amount
                        property_price_unit_id = self.env[
                            'property.price.unit.history'].create({
                            'price_update_id': property_price_id.id,
                            'project_id': self.project_id.id,
                            'property_unit_id': unit.id,
                            'old_value': old_amount,
                            'current_value': new_amount,
                        })
                unit_names = ", ".join(unit_ids.mapped('name'))
                if self.type_percentage == 'decrease':
                    message = _(
                        "%s has decrease the price  by %s percentage for the following units:\n %s"
                    ) % (
                                  self.env.user.name,
                                  str( self.percentage_value),
                                  unit_names
                              )

                    self.project_id.message_post(
                        body=message,
                    )
                if self.type_percentage == 'increase':
                    message = _(
                        "%s has increase the price by %s percentage for the following units:\n %s"
                    ) % (
                                  self.env.user.name,
                                  str(self.percentage_value),
                                  unit_names
                              )

                    self.project_id.message_post(
                        body=message,
                    )
            else:
                unit_ids = self.env['property.unit'].sudo().search(
                    [('project_id', '=', self.project_id.id),
                     ('type_id', '=', self.unit_type_id.id),
                     ('status', 'in', ['draft', 'available', 'reserved', 'on_hold'])])
                property_price_id = self.env['property.price.update'].create({
                    'project_id': self.project_id.id,
                    'property_unit_ids': unit_ids.ids,
                    'price_type': 'fixed',
                    'currency_id': self.currency_id.id,
                    'percentage_value': self.percentage_value,
                    'fixed_value': self.fixed_value,
                    'type_percentage': self.type_percentage,
                })
                for unit in unit_ids:
                    old_amount = unit.php
                    new_amount = self.fixed_value
                    unit.php = new_amount
                    property_price_unit_id = self.env[
                        'property.price.unit.history'].create({
                        'price_update_id': property_price_id.id,
                        'project_id': self.project_id.id,
                        'property_unit_id': unit.id,
                        'old_value': old_amount,
                        'current_value': new_amount,
                    })
                unit_names = ", ".join(unit_ids.mapped('name'))
                message = _(
                    "%s has updated the price to %s for the following units:\n %s"
                ) % (
                              self.env.user.name,
                              str(self.fixed_value),
                              unit_names
                          )

                self.project_id.message_post(
                    body=message,
                )
        else:
            if not self.unit_ids:
                raise UserError(
                    _("Please Choose the units !!"))
            if self.price_type == 'percentage':
                if self.percentage_value == 0.0:
                    raise UserError(
                        _("Please Choose the percentage greater than zero !!"))
                unit_ids = self.unit_ids
                property_price_id = self.env['property.price.update'].create({
                    'project_id': self.project_id.id,
                    'property_unit_ids': unit_ids.ids,
                    'price_type': 'percentage',
                    'currency_id': self.currency_id.id,
                    'percentage_value': self.percentage_value,
                    'fixed_value': self.fixed_value,
                    'type_percentage': self.type_percentage,
                })
                for unit in unit_ids:
                    if self.type_percentage == 'decrease':
                        old_amount = unit.php
                        per_amount = (old_amount * self.percentage_value) / 100
                        new_amount = old_amount - per_amount
                        unit.php = new_amount
                        property_price_unit_id = self.env[
                            'property.price.unit.history'].create({
                            'price_update_id': property_price_id.id,
                            'project_id': self.project_id.id,
                            'property_unit_id': unit.id,
                            'old_value': old_amount,
                            'current_value': new_amount,
                        })
                    if self.type_percentage == 'increase':
                        old_amount = unit.php
                        per_amount = (old_amount * self.percentage_value) / 100
                        new_amount = old_amount + per_amount
                        unit.php = new_amount
                        property_price_unit_id = self.env[
                            'property.price.unit.history'].create({
                            'price_update_id': property_price_id.id,
                            'project_id': self.project_id.id,
                            'property_unit_id': unit.id,
                            'old_value': old_amount,
                            'current_value': new_amount,
                        })
                unit_names = ", ".join(unit_ids.mapped('name'))
                if self.type_percentage == 'decrease':
                    message = _(
                        "%s has decrease the price  by %s percentage for the following units:\n %s"
                    ) % (
                                  self.env.user.name,
                                  str(self.percentage_value),
                                  unit_names
                              )

                    self.project_id.message_post(
                        body=message,
                    )
                if self.type_percentage == 'increase':
                    message = _(
                        "%s has increase the price by %s percentage for the following units:\n %s"
                    ) % (
                                  self.env.user.name,
                                  str(self.percentage_value),
                                  unit_names
                              )

                    self.project_id.message_post(
                        body=message,
                    )
            else:
                unit_ids = self.unit_ids
                property_price_id = self.env['property.price.update'].create({
                    'project_id': self.project_id.id,
                    'property_unit_ids': unit_ids.ids,
                    'price_type': 'fixed',
                    'currency_id': self.currency_id.id,
                    'percentage_value': self.percentage_value,
                    'fixed_value': self.fixed_value,
                    'type_percentage': self.type_percentage,
                })
                for unit in unit_ids:
                    old_amount = unit.php
                    new_amount = self.fixed_value
                    unit.php = new_amount
                    property_price_unit_id = self.env[
                        'property.price.unit.history'].create({
                        'price_update_id': property_price_id.id,
                        'project_id': self.project_id.id,
                        'property_unit_id': unit.id,
                        'old_value': old_amount,
                        'current_value': new_amount,
                    })
                unit_names = ", ".join(unit_ids.mapped('name'))
                message = _(
                    "%s has updated the price to %s for the following units:\n %s"
                ) % (
                              self.env.user.name,
                              str(self.fixed_value),
                              unit_names
                          )

                self.project_id.message_post(
                    body=message,
                )





