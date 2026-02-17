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
from odoo import api, models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    property_project_id = fields.Many2one(
        'property.project',
        string="Sale Project",
        tracking=True
    )

    property_unit_id = fields.Many2one(
        'property.unit',
        string="Sale Unit",
    )

    sale_id = fields.Many2one(
        'sale.order',
        string="Sale Order"
    )


    property_type = fields.Selection([
        ('sale','Sales'),
    ],
        string="Property Type",
    )

    spa_id = fields.Many2one(
        'spa.book',
        string="Spa"
    )

    sale_property_commission_id = fields.Many2one(
        'sale.commission.to.be.paid',
        string="sale commission"
    )

    agent_sale_commission_id = fields.Many2one(
        'agent.commission.to.be.paid',
        string="Agent Commission"
    )



