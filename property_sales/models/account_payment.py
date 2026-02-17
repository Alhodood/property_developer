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


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    property_project_id = fields.Many2one(
        'property.project',
        string="Property Project",
        tracking=True,
    )

    property_unit_id = fields.Many2one(
        'property.unit',
        string="Property Unit",
        domain="[('project_id', '=', property_project_id)]",
        tracking=True,
    )

    property_type = fields.Selection([
        ('sale', 'Sales')],
        string="Property Type",
    )

    voucher_id = fields.Many2one(
        'payment.voucher',
        string="Voucher",
        tracking=True,
    )