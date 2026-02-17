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

from datetime import date, timedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import mimetypes

class PropertySalesDocument(models.Model):
    _name = 'property.sales.document'
    _description = 'Property Sales Documents'

    name = fields.Char(
        string='Document Number',
        required=True,
        copy=False,
        help='You can give your Document number.'
    )

    description = fields.Text(
        string='Description',
        copy=False,
        help="Description of the documents."
    )

    attachments_doc = fields.Binary(
        string='Attachment'
    )

    expiry_date = fields.Date(
        string='Expiry Date',
        copy=False,
        help="Expiry date of the documents."
    )

    property_id = fields.Many2one(
        comodel_name='property.project',
        invisible=1,
        copy=False,
        help='Specify the Property name.'
    )

    pdoc_attachment_ids = fields.Many2many(
        comodel_name='ir.attachment',
        relation='psdoc_attach_rel',
        column1='psdoc_id',
        column2='psattach_id3',
        string="Attachment",
        help='You can attach the copy of your document',
        copy=False
    )

    issue_date = fields.Date(
        string='Issue Date',
        default=fields.Date.today,
        help="Date of issued",
        copy=False
    )

    document_type_id = fields.Many2one(
        comodel_name='property.sales.document.type',
        string="Document Type",
        help="Type of the document."
    )

    before_days = fields.Integer(
        string="Days",
        help="How many number of days before to get the notification email."
    )

    notification_type = fields.Selection([
        ('single', 'Notification on expiry date'),
        ('multi', 'Notification before few days'),
        ('everyday', 'Everyday till expiry date'),
        ('everyday_after', 'Notification on and after expiry')
    ], string='Notification Type',
        help="Select type of the documents expiry notification."
    )

    notification_to = fields.Many2one(
        comodel_name='res.partner',
        string='Notification To'
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('verify', 'Verify'),
        ('expire', 'Expired'),
    ],default='draft', string='Status')

    is_expiry = fields.Boolean(default=True)

    attachments_doc_filename = fields.Char(string="Filename")

    attachments_doc_id = fields.Integer('Attachment doc id')

    def action_expire_doc(self):
        self.state = 'expire'
        if self.notification_to:
            self.env['portal.notification'].create({
                'name': 'Document-' + self.name,
                'message': 'Document Expired',
                'partner_id': self.notification_to.id,
            })

    def action_verify_doc(self):
        if not self.attachments_doc and not self.pdoc_attachment_ids:
            raise UserError("Add Attachments first.")

        if self.property_id:
            folder_id = self.property_id.property_folder_id

        if folder_id:
            # 🔒 Freeze attachment IDs
            Documents = self.env['documents.document']

            if self.attachments_doc:
                file_data = self.attachments_doc
                file_name = 'document-'+self.name+'.pdf'

                attachment = self.env['ir.attachment'].create({
                    'name': file_name,
                    'datas': file_data,
                    'res_model': self._name,
                    'res_id': self.id,
                })

                doc = self.env['documents.document'].sudo().create({
                    'name': file_name,
                    'attachment_id': attachment.id,
                    'folder_id': folder_id,
                })
                self.attachments_doc_id = doc.id

            # From one2many attachments
            for attachment in self.pdoc_attachment_ids:
                mimetype = mimetypes.guess_type(attachment.name)[0] or 'application/octet-stream'
                document = Documents.sudo().create({
                    'name': attachment.name,
                    'datas': attachment.datas,
                    'type': 'binary',  # 🔥 THIS LINE FIXES EVERYTHING
                    'folder_id': folder_id,
                    'owner_id': self.env.user.id,
                    'mimetype': mimetype,
                    'res_model': self._name,
                    'res_id': self.id,
                    'attachment_id':attachment.id
                })

        self.state='verify'
        if self.notification_to:
            self.env['portal.notification'].create({
                'name': 'Document-'+self.name,
                'message': 'Document Verified',
                'partner_id': self.notification_to.id,
            })

    def mail_reminder(self):
        """Sending document expiry notification to employees."""
        for record in self.search([('expiry_date', '!=', False)]):
            if record.property_id:
                name = record.property_id.name

            exp_date = fields.Date.from_string(record.expiry_date)
            days_before = timedelta(days=record.before_days or 0)
            is_expiry_today = fields.Date.today() == exp_date
            is_notification_day = any([record.notification_type == 'single'
                                       and is_expiry_today,
                                       record.notification_type == 'multi'
                                       and (fields.Date.today() == fields.Date.
                                            from_string(
                                           record.expiry_date) - days_before
                                            or is_expiry_today),
                                       record.notification_type == 'everyday'
                                       and fields.Date.today() >= fields.Date.
                                      from_string(
                                           record.expiry_date) - days_before,
                                       record.notification_type ==
                                       'everyday_after'
                                       and fields.Date.today() <=
                                       fields.Date.from_string(
                                           record.expiry_date) + days_before,
                                       not record.notification_type and
                                       fields.Date.today() == fields.Date.
                                      from_string(
                                           record.expiry_date) - timedelta(
                                           days=7), ])
            if is_notification_day and record.notification_to:
                employee_name = record.notification_to.name
                document_name = record.name
                document_type = record.document_type_id.name
                expiry_date_str = str(record.expiry_date)
                mail_content = (
                    f"Hello {employee_name},<br>Your Document {document_name} in {name}"
                    f"is going to expire on {expiry_date_str}. "
                    "Please renew it before the expiry date."
                )
                subject = _('Document-%s %s Expired On %s') % (document_type,
                    document_name, expiry_date_str)
                main_content = {
                    'subject': subject,
                    'author_id': self.env.user.partner_id.id,
                    'body_html': mail_content,
                    'email_to': record.notification_to.email,
                }
                self.env['portal.notification'].create({
                    'name': 'Document-' + record.name,
                    'message': subject,
                    'partner_id': record.notification_to.id,
                })
                self.env['mail.mail'].create(main_content).send()

    @api.constrains('expiry_date')
    def _check_expiry_date(self):
        """This method is called as a constraint whenever the 'expiry_date'
         field of an 'hr.employee.document' record is modified."""
        for rec in self:
            if rec.expiry_date:
                exp_date = fields.Date.from_string(rec.expiry_date)
                if exp_date < date.today():
                    raise UserError(_('Your Document Is Expired.'))
