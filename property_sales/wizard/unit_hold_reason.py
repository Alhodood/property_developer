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

class PropertyUnitHoldWizard(models.TransientModel):
    _name = 'property.unit.hold.wizard'
    _description = "Hold Property Units Wizard"

    reason = fields.Text(string="Reason for Hold",
                         required=True)

    unit_ids = fields.Many2many(
        'property.unit',
        string="Units"
    )


    def action_add_done(self):
        for rec in self.unit_ids:
            if rec.status in ['draft','available']:
                rec.last_hold_date = fields.Date.today()
                rec.last_hold_by = self.env.user.id
                rec.hold_reason = self.reason
                rec.status = "on_hold"



