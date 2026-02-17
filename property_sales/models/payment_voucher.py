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
from odoo import api, models, fields,_
from odoo.exceptions import UserError


class PaymentVoucher(models.Model):
    _name = 'payment.voucher'
    _description = 'Payment Voucher'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(
        string='Sequence',
        copy=False,
    )

    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=True
    )

    company_id = fields.Many2one(
        'res.company',
        string="Company",
        tracking=True,
        default=lambda self: self.env.company,
        readonly=True
    )

    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('posted', 'Posted')
        ],
        default='draft',
        tracking=True
    )

    cheque_line_ids = fields.One2many(
        'payment.voucher.line',
        'voucher_id',
        string='Collected Cheques'
    )

    @api.model
    def create(self, vals):
        res = super(PaymentVoucher, self).create(vals)
        seq = self.env['ir.sequence'].next_by_code(
            'property.voucher.sequence')
        res.name = seq
        return res

    def action_post(self):
        for record in self:
            if not record.cheque_line_ids:
                raise UserError(
                    _("Please add at least one cheque line before posting.")
                )
            for line in record.cheque_line_ids:
                if line.amount == 0.0:
                    raise UserError(
                        _("Please Add Amount Greater Than Zero !!.")
                    )
                if line.property_type == 'sale':
                    if not line.property_project_id or not line.property_unit_id:
                        raise UserError(
                            _("Please Choose Proper Property And Unit !!.")
                        )
                    self.env['account.payment'].sudo().create({
                        'payment_type': 'inbound',
                        'partner_id': record.partner_id.id,
                        'amount': line.amount,
                        'currency_id': line.currency_id.id,
                        'date': line.cheque_date,
                        'memo': line.cheque_number,
                        'journal_id': line.journal_id.id,
                        'payment_method_line_id': line.payment_method_id.id,
                        'voucher_id': self.id,
                        'property_type': line.property_type,
                        'property_project_id': line.property_project_id.id,
                        'property_unit_id': line.property_unit_id.id,
                        'company_id': self.company_id.id,
                    })
                if line.property_type == 'construction':
                    self.env['account.payment'].sudo().create({
                        'payment_type':'inbound',
                        'partner_id':record.partner_id.id,
                        'amount':line.amount,
                        'currency_id':line.currency_id.id,
                        'date':line.cheque_date,
                        'memo':line.cheque_number,
                        'journal_id':line.journal_id.id,
                        'payment_method_line_id':line.payment_method_id.id,
                        'voucher_id':self.id,
                        'property_type':line.property_type,
                        'project_construction_id':line.project_construction_id.id,
                        'company_id':self.company_id.id,
                    })
            record.state = 'posted'

    def action_view_payments(self):
        return {
            'name': 'Payment Voucher',
            'view_type': 'list',
            'view_mode': 'list,form',
            'res_model': 'account.payment',
            'domain': [('voucher_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'context': {'default_voucher_id': self.id,}
        }


class PaymentVoucherLine(models.Model):
    _name = 'payment.voucher.line'
    _description = 'Payment Voucher Cheque Line'

    voucher_id = fields.Many2one(
        'payment.voucher',
        string='Voucher',
        ondelete='cascade'
    )

    cheque_date = fields.Date(
        string='Cheque Date',
        required=True
    )

    cheque_number = fields.Char(
        string='Cheque Number',
        required=True
    )

    amount = fields.Monetary(
        string='Amount',
        required=True
    )
    available_journal_ids = fields.Many2many(
        comodel_name='account.journal',
        compute='_compute_available_journal_ids'
    )

    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        compute='_compute_journal_id',
        store=True, readonly=False, precompute=True,  check_company=True,
        index=False,
        required=True,
    )

    partner_id = fields.Many2one(
        related='voucher_id.partner_id',
        store=True,
        readonly=True
    )

    company_id = fields.Many2one(
        'res.company',
        string="Company",
        tracking=True,
        related='voucher_id.company_id',
        readonly=True,
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.company.currency_id.id
    )

    available_payment_method_line_ids = fields.Many2many(
        'account.payment.method.line',
        compute='_compute_available_payment_method_lines'
    )

    payment_method_id = fields.Many2one(
        'account.payment.method.line',
        compute='_compute_payment_method_line_id',
        readonly=False, store=True, copy=False,
        domain="[('id', 'in', available_payment_method_line_ids)]",
        string='Payment Method'
    )

    property_type = fields.Selection([
        ('sale', 'Sales')],
        string="Property Type",
    )

    property_project_id = fields.Many2one(
        'property.project',
        string="Sale Property",
        tracking=True,
    )

    property_unit_id = fields.Many2one(
        'property.unit',
        string="Sale Unit",
        domain="[('project_id', '=', property_project_id)]",
        tracking=True,
    )


    @api.depends('voucher_id','cheque_number')
    def _compute_available_journal_ids(self):
        """
        Get all journals having at least one payment method for inbound/outbound depending on the payment_type.
        """
        journals = self.env['account.journal'].search([
            '|',
            ('company_id', 'parent_of', self.env.company.id),
            ('company_id', 'child_of', self.env.company.id),
            ('type', 'in', ('bank', 'cash', 'credit')),
        ])
        for pay in self:
            pay.available_journal_ids = journals.filtered(
                'inbound_payment_method_line_ids')

    def _get_payment_method_codes_to_exclude(self):
        # can be overriden to exclude payment methods based on the payment characteristics
        self.ensure_one()
        return []

    @api.depends('company_id', 'partner_id')
    def _compute_journal_id(self):
        for payment in self:
            # default customer payment method logic
            partner = payment.partner_id
            payment_type = 'inbound'
            if not bool(payment._origin) and (partner or payment_type):
                field_name = f'property_{payment_type}_payment_method_line_id'
                default_payment_method_line = \
                payment.partner_id.with_company(payment.company_id)[field_name]
                journal = default_payment_method_line.journal_id
                if journal:
                    payment.journal_id = journal
                    continue

            company = payment.company_id or self.env.company
            if not payment.journal_id or company != payment.journal_id.company_id:
                payment.journal_id = self.env['account.journal'].search([
                    *self.env['account.journal']._check_company_domain(
                        company),
                    ('type', 'in', ['bank', 'cash', 'credit']),
                ], limit=1)

    @api.depends('journal_id', 'company_id')
    def _compute_available_payment_method_lines(self):
        for pay in self:
            pay.available_payment_method_line_ids = pay.journal_id._get_available_payment_method_lines(
                'inbound')
            to_exclude = pay._get_payment_method_codes_to_exclude()
            if to_exclude:
                pay.available_payment_method_line_ids = pay.available_payment_method_line_ids.filtered(
                    lambda x: x.code not in to_exclude)

    @api.depends('available_payment_method_line_ids')
    def _compute_payment_method_line_id(self):
        ''' Compute the 'payment_method_line_id' field.
        This field is not computed in '_compute_payment_method_line_fields' because it's a stored editable one.
        '''
        for pay in self:
            available_payment_method_lines = pay.available_payment_method_line_ids
            inbound_payment_method = pay.partner_id.property_inbound_payment_method_line_id
            if inbound_payment_method.id in available_payment_method_lines.ids:
                pay.payment_method_id = inbound_payment_method
            elif pay.payment_method_id.id in available_payment_method_lines.ids:
                pay.payment_method_id = pay.payment_method_id
            elif available_payment_method_lines:
                pay.payment_method_id = available_payment_method_lines[
                    0]._origin
            else:
                pay.payment_method_id = False