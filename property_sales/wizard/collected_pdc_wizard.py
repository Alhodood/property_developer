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


class SpaAddPdcWizard(models.TransientModel):
    _name = 'spa.add.pdc.wizard'
    _description = 'Add PDC Wizard'

    spa_id = fields.Many2one(
        'spa.book',
        string="SPA",
        readonly=True
    )

    property_project_id = fields.Many2one(
        'property.project',
        string="Property",
        related='spa_id.property_project_id',
        readonly=True
    )

    property_unit_id = fields.Many2one(
        'property.unit',
        string="Unit",
        related='spa_id.property_unit_id',
        readonly=True
    )

    partner_id = fields.Many2one(
        'res.partner',
        string="Customer",
        related='spa_id.partner_id',
        readonly=True
    )

    cheque_pay_name = fields.Char(
        string="Cheque Pay Name",
        required=True
    )

    bank = fields.Char(
        string="Bank"
    )

    line_ids = fields.One2many(
        'spa.add.pdc.wizard.line',
        'wizard_id',
        string="Cheque Lines"
    )

    def action_done(self):
        for line in self.line_ids:
            self.env['pdc.payment.received'].create({
                'spa_id': self.spa_id.id,
                'property_type': 'sale',
                'property_project_id': self.property_project_id.id,
                'property_unit_id': self.property_unit_id.id,
                'customer_id': self.partner_id.id,
                'cheque_pay_name': self.cheque_pay_name,
                'cheque_date': line.date,
                'cheque_no': line.cheque_number,
                'amount': line.amount,
                'bank': self.bank,
                'status':'draft',
            })


class SpaAddPdcWizardLine(models.TransientModel):
    _name = 'spa.add.pdc.wizard.line'
    _description = 'Add PDC Line'

    wizard_id = fields.Many2one(
        'spa.add.pdc.wizard',
        required=True,
        ondelete='cascade'
    )

    date = fields.Date(
        string="Cheque Date",
        required=True
    )

    cheque_number = fields.Char(
        string="Cheque Number",
        required=True
    )

    amount = fields.Float(
        string="Amount",
        required=True
    )
