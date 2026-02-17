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
from datetime import datetime
from odoo.exceptions import UserError
import base64
import xlrd


class PaymentLineUpload(models.TransientModel):
    _name = 'import.payment.plan.lines'
    _description = "Import Payment LInes"

    file = fields.Binary(string='Upload File', required=True)
    filename = fields.Char(string='Filename')

    def action_process_file(self):
        if not self.file:
            raise UserError(_("Please upload a file."))
        sale_order = self.env['sale.order'].sudo().search([('id', '=', self.env.context.get('active_id'))])
        file_data = base64.b64decode(self.file)
        workbook = xlrd.open_workbook(file_contents=file_data)
        sheet = workbook.sheet_by_index(0)
        total_percentage = 0.0
        lines = []
        plan_date = False
        for row_idx in range(1, sheet.nrows):
            row = sheet.row(row_idx)
            name = row[0].value if len(row) > 0 else False
            plan_date = False
            if len(row) > 1 and row[1].value:
                if row[1].ctype == xlrd.XL_CELL_DATE:
                    plan_date = xlrd.xldate_as_datetime(
                        row[1].value,
                        workbook.datemode
                    ).date()
                else:
                    date_str = str(row[1].value).strip()
                    try:
                        plan_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    except ValueError:
                        raise UserError(
                            _(
                                "Invalid date format in row %s.\n\n"
                                "Allowed format: YYYY-MM-DD\n"
                                "Example: 2025-01-10"
                            ) % (row_idx + 1)
                        )

        for row_idx in range(1, sheet.nrows):
            row = sheet.row(row_idx)
            name = row[0].value if len(row) > 0 else False
            plan_date = False
            if len(row) > 1 and row[1].value:
                if row[1].ctype == xlrd.XL_CELL_DATE:
                    plan_date = xlrd.xldate_as_datetime(
                        row[1].value,
                        workbook.datemode
                    ).date()
                else:
                    plan_date = row[1].value
            percentage = row[2].value if len(row) > 2 else 0.0

            if not percentage:
                continue

            percentage = float(percentage)
            total_percentage += percentage
            lines.append({
                'name': name,
                'plan_date': plan_date,
                'percentage': percentage,
            })

        if total_percentage > 100:
            raise UserError("Total percentage cannot be greater than 100%.!!")
        if total_percentage < 100 and lines:
            remaining = 100 - total_percentage
            lines[-1]['percentage'] += remaining
        product_line = sale_order.offer_quote_line_ids.filtered(
            lambda l: l.product_line
        )
        product_line = product_line[0]
        sales_amount = product_line.discounted_amount
        lines = sorted(
            lines,
            key=lambda l: l['plan_date'] or fields.Date.max
        )
        running_total = 0.0
        last_index = len(lines) - 1
        for idx, line in enumerate(lines):
            amount = (sales_amount * line['percentage']) / 100

            if idx != last_index:
                integer_part = int(amount)
                last_two = integer_part % 100
                rounded = (
                    integer_part - last_two
                    if last_two < 50
                    else integer_part + (100 - last_two)
                )
                running_total += rounded
            else:
                rounded = sales_amount - running_total
            line.update({
                'amount': amount,
                'actual_amount': amount,
                'rounded_amount': rounded,
            })
        sale_order.plan_lines_ids.unlink()
        for vals in lines:
            vals['sale_order'] = sale_order.id
            self.env['payment.plan.offer.line'].create(vals)
        return {'type': 'ir.actions.act_window_close'}


class PaymentLineBookingUpload(models.TransientModel):
    _name = 'import.payment.booking.plan.lines'
    _description = "Import Booking Payment LInes"

    file = fields.Binary(string='Upload File', required=True)
    filename = fields.Char(string='Filename')

    def action_process_file(self):
        if not self.file:
            raise UserError(_("Please upload a file."))
        offer_booking = self.env['offer.booking'].sudo().search([('id', '=', self.env.context.get('active_id'))])
        file_data = base64.b64decode(self.file)
        workbook = xlrd.open_workbook(file_contents=file_data)
        sheet = workbook.sheet_by_index(0)
        total_percentage = 0.0
        running_total = 0.0
        invoiced_lines = offer_booking.payment_schedule_ids.filtered(
            lambda l: l.inv_created
        )
        if invoiced_lines:
            invoiced_percentage = sum(invoiced_lines.mapped('percentage'))
            invoiced_rounded_total = sum(invoiced_lines.mapped('rounded_amount'))
            running_total = invoiced_rounded_total
            total_percentage = invoiced_percentage
        lines = []
        plan_date = False
        for row_idx in range(1, sheet.nrows):
            row = sheet.row(row_idx)
            name = row[0].value if len(row) > 0 else False
            plan_date = False
            if len(row) > 1 and row[1].value:
                if row[1].ctype == xlrd.XL_CELL_DATE:
                    plan_date = xlrd.xldate_as_datetime(
                        row[1].value,
                        workbook.datemode
                    ).date()
                else:
                    date_str = str(row[1].value).strip()
                    try:
                        plan_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    except ValueError:
                        raise UserError(
                            _(
                                "Invalid date format in row %s.\n\n"
                                "Allowed format: YYYY-MM-DD\n"
                                "Example: 2025-01-10"
                            ) % (row_idx + 1)
                        )

        for row_idx in range(1, sheet.nrows):
            row = sheet.row(row_idx)
            name = row[0].value if len(row) > 0 else False
            plan_date = False
            if len(row) > 1 and row[1].value:
                if row[1].ctype == xlrd.XL_CELL_DATE:
                    plan_date = xlrd.xldate_as_datetime(
                        row[1].value,
                        workbook.datemode
                    ).date()
                else:
                    plan_date = row[1].value
            percentage = row[2].value if len(row) > 2 else 0.0

            if not percentage:
                continue

            percentage = float(percentage)
            total_percentage += percentage
            lines.append({
                'name': name,
                'plan_date': plan_date,
                'percentage': percentage,
            })

        if total_percentage > 100:
            raise UserError(
                _("Total percentage with booking lines cannot be greater than 100%%.\n"
                  "Current total: %.2f%%") % total_percentage
            )
        if not lines:
            raise UserError(_("No valid lines found in file."))
        if total_percentage < 100 and lines:
            remaining = 100 - total_percentage
            lines[-1]['percentage'] += remaining
        sales_amount = offer_booking.final_total_property_value
        lines = sorted(
            lines,
            key=lambda l: l['plan_date'] or fields.Date.max
        )
        last_index = len(lines) - 1
        for idx, line in enumerate(lines):
            amount = (sales_amount * line['percentage']) / 100

            if idx != last_index:
                integer_part = int(amount)
                last_two = integer_part % 100
                rounded = (
                    integer_part - last_two
                    if last_two < 50
                    else integer_part + (100 - last_two)
                )
                running_total += rounded
            else:
                rounded = sales_amount - running_total
            line.update({
                'amount': amount,
                'rounded_amount': rounded,
            })
        offer_booking.payment_schedule_ids.filtered(
            lambda l: not l.inv_created
        ).unlink()
        for vals in lines:
            vals['offer_id'] = offer_booking.id
            self.env['payment.schedule.line'].create(vals)
        return {'type': 'ir.actions.act_window_close'}