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

class SaleCommissionToBePAid(models.Model):
    _name = 'sale.commission.to.be.paid'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'sequence_code'
    _description = 'Sales Commission To Be Paid'
    _order = 'id desc'

    sequence_code = fields.Char(
        string="Sequence",
    )

    spa_id = fields.Many2one(
        'spa.book',
        string="Spa"
    )

    date_created = fields.Date(
        string="Date",
        default=fields.Date.context_today,
    )

    commission_amount = fields.Float(
        string="Commission Amount"
    )

    sales_person_id = fields.Many2one(
        'res.users',
        string="Sales Person"
    )

    created_by = fields.Many2one(
        'res.users',
        string="Created By"
    )

    property_project_id = fields.Many2one(
        'property.project',
        string="Project",
    )
    company_id = fields.Many2one(
        'res.company',
        string="Company",
        tracking=True,
        related="property_project_id.company_id",
    )


    final_total_property_value = fields.Float(
        string="Final Property Sale Value",
    )

    property_unit_id = fields.Many2one(
        'property.unit',
        string="Unit",
        domain='[("project_id", "=", property_project_id)]',
    )

    bill_ids = fields.One2many(
        'account.move',
        'sale_property_commission_id',
        string="Bills"
    )

    @api.model
    def create(self, vals):
        res = super(SaleCommissionToBePAid, self).create(vals)
        seq = self.env['ir.sequence'].next_by_code('sale.commission.sequence')
        res.sequence_code = seq
        return res


class AgentCommissionToBePAid(models.Model):
    _name = 'agent.commission.to.be.paid'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'sequence_code'
    _description = 'Agent Commission To Be Paid'
    _order = 'id desc'

    sequence_code = fields.Char(
        string="Sequence",
    )

    spa_id = fields.Many2one(
        'spa.book',
        string="Spa"
    )

    date_created = fields.Date(
        string="Date",
        default=fields.Date.context_today,

    )

    commission_amount = fields.Float(
        string="Commission Amount",
    )

    agent = fields.Many2one(
        'res.partner',
        string="Agent",
    )

    created_by = fields.Many2one(
        'res.users',
        string="Created By",
    )

    property_project_id = fields.Many2one(
        'property.project',
        string="Project",
    )

    company_id = fields.Many2one(
        'res.company',
        string="Company",
        tracking=True,
        related="property_project_id.company_id",
    )

    final_total_property_value = fields.Float(
        string="Final Property Sale Value",
    )

    property_unit_id = fields.Many2one(
        'property.unit',
        string="Unit",
        domain='[("project_id", "=", property_project_id)]',
    )
    bill_ids = fields.One2many(
        'account.move',
        'agent_sale_commission_id',
        string="Bills"
    )

    @api.model
    def create(self, vals):
        res = super(AgentCommissionToBePAid, self).create(vals)
        seq = self.env['ir.sequence'].next_by_code('agent.commission.sequence')
        res.sequence_code = seq
        return res


