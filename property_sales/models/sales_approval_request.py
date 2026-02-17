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
from odoo import models, fields,_,api
from odoo.exceptions import UserError

class SaleDiscountApprovalRequest(models.Model):
    _name = 'sale.discount.approval.request'
    _description = 'Sales Discount Approval Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'sale_order_id'
    _order = 'id desc'

    sequence_code = fields.Char(
        string="Sequence"
    )

    sale_order_id = fields.Many2one(
        'sale.order',
        string="Sale Order",
        tracking=True,
        required=True
    )

    client_type = fields.Selection(
        [('direct', 'Direct'),
         ('indirect', 'Indirect')],
        string="Client Type",
        related='sale_order_id.client_type'
    )

    partner_id = fields.Many2one(
        'res.partner',
        string="partner",
        related='sale_order_id.partner_id'
    )

    property_project_id = fields.Many2one(
        'property.project',
        string="Project",
        related='sale_order_id.property_project_id',
        tracking=True
    )

    property_unit_id = fields.Many2one(
        'property.unit',
        string="Unit",
        related='sale_order_id.property_unit_id',
    )

    discount_based_on = fields.Selection(
        [('down_payment', 'Down Payment'),
         ('Payment_Plan', 'Payment Plan')
         ],
        string="Discount Based On",
        related='sale_order_id.discount_based_on',
    )

    payment_plan_id = fields.Many2one(
        'property.payment.plan',
        string="Payment Plan",
        related='sale_order_id.payment_plan_id',

    )

    requested_by = fields.Many2one(
        'res.users',
        string="Requested By",
        tracking=True,
        default=lambda self: self.env.user
    )

    request_date = fields.Date(
        string="Date",
        default=fields.Date.today,
    )

    approval_user_ids = fields.Many2many(
        'res.users',
        tracking=True,
        string="Approval Users"
    )

    approved_user = fields.Many2one(
        'res.users',
        tracking=True,
        string="Approved/ Rejected User"
    )

    discount_percent = fields.Float(
        string="Request Discount %"
    )

    reason_for_request = fields.Text(
        string="Reason For Request"
    )

    currency_id = fields.Many2one(
        'res.currency',
        related="sale_order_id.currency_id",
        string="Currency"
    )

    approval_state = fields.Selection([
        ('waiting', 'Waiting Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ],
    string="Approval State",
    default='waiting',
    tracking=True
    )

    company_id = fields.Many2one(
        'res.company',
        tracking=True,
        string="Company",
        default=lambda self: self.env.company,
    )

    is_approver = fields.Boolean(
        string="Is Approver",
        compute='_compute_is_approver'
    )

    @api.model
    def create(self, vals):
        res = super(SaleDiscountApprovalRequest, self).create(vals)
        seq = self.env['ir.sequence'].next_by_code(
            'discount.request.sequence')
        res.sequence_code = seq
        return res

    @api.depends('approval_user_ids','sequence_code')
    def _compute_is_approver(self):
        for rec in self:
            if self.env.user.id in rec.approval_user_ids.ids:
                rec.is_approver = True
            else:
                rec.is_approver = False

    def action_approve(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Discount Approved Reason',
            'res_model': 'discount.approved.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_sale_order': self.sale_order_id.id,
                'default_discount_request_id': self.id,
            }
        }


    def action_reject(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Discount Reject Reason',
            'res_model': 'discount.reject.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_sale_order': self.sale_order_id.id,
                'default_discount_request_id': self.id,
            }
        }