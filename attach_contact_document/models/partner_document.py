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

class ContactDocument(models.Model):
    _name = 'partner.document'
    _description = 'Contact Documents'
    _order = 'create_date desc'

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
        'Attachment'
    )

    expiry_date = fields.Date(
        string='Expiry Date',
        copy=False,
        help="Expiry date of the documents."
    )

    partner_id = fields.Many2one(
        'res.partner',
        invisible=1,
        copy=False,
        help='Specify the customer name.'
    )

    pdoc_attachment_ids = fields.Many2many(
        'ir.attachment',
        'pdoc_attach_rel',
        'pdoc_id',
        'attachment_id',
        string="Attachment",
        copy=False
    )


    issue_date = fields.Date(
        string='Issue Date',
        default=fields.Date.today,
        help="Date of issued",
        copy=False
    )

    document_type_id = fields.Many2one(
        'partner.document.type',
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
    ],
    string='Notification Type',
    help="Select type of the documents expiry notification."
    )

    notification_to = fields.Many2many(
        'res.partner',
        string='Notification To'
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('verified', 'Verified'),
        ('expire', 'Expired'),
    ], default='draft', tracking=True)

    is_expiry = fields.Boolean(default=True)

    partner_folder_id = fields.Many2one(
        'documents.document',
        string='Partner Folder',
        readonly=True
    )

    def action_expire_doc(self):
        self.state = 'expire'
        for rec in self.notification_to:
            rec.env['portal.notification'].create({
                'name': 'Document-' + self.name,
                'message': 'Document Expired',
                'partner_id': rec.id,
            })

    def action_verify(self):
        Document = self.env['documents.document'].sudo()
        Attachment = self.env['ir.attachment'].sudo()

        if not self.pdoc_attachment_ids and not self.attachments_doc:
            raise UserError("Attach Document")

        for rec in self:
            if not rec.partner_id:
                raise UserError(_("Please select a Partner first."))

            partner = rec.partner_id
            # ------------------------------------------------
            # 1. Create Partner Folder if not exists
            # ------------------------------------------------
            folder = partner.partner_folder_id
            if not folder:
                folder = Document.create({
                    'name': partner.name,   # Folder name = Partner name
                    'type': 'folder',
                    'company_id': rec.env.company.id,
                    'access_internal': 'view',
                    'owner_id': False,
                })

                partner.partner_folder_id = folder.id

            rec.partner_folder_id = folder.id
            # ------------------------------------------------
            # 2. Binary field attachment
            # ------------------------------------------------
            if rec.attachments_doc:
                binary_attach = Attachment.create({
                    'name': rec.name or 'Partner Document',
                    'type': 'binary',
                    'datas': rec.attachments_doc,
                    'res_model': rec._name,
                    'res_id': rec.id,
                })

                exists = Document.search([
                    ('attachment_id', '=', binary_attach.id),
                    ('folder_id', '=', folder.id),
                ], limit=1)

                if not exists:
                    Document.create({
                        'name': binary_attach.name,
                        'attachment_id': binary_attach.id,
                        'folder_id': folder.id,
                        'company_id': rec.env.company.id,
                        'owner_id': rec.env.user.id,
                    })

            # ------------------------------------------------
            # 3. Many2many attachments
            # ------------------------------------------------
            for attach in rec.pdoc_attachment_ids:
                exists = Document.search([
                    ('attachment_id', '=', attach.id),
                    ('folder_id', '=', folder.id),
                ], limit=1)

                if not exists:
                    Document.create({
                        'name': attach.name,
                        'attachment_id': attach.id,
                        'folder_id': folder.id,
                        'company_id': rec.env.company.id,
                        'owner_id': rec.env.user.id,
                    })

            rec.state = 'verified'
            for rec in self.notification_to:
                rec.env['portal.notification'].create({
                    'name': 'Document-' + self.name,
                    'message': 'Document Verified',
                    'partner_id': rec.id,
                })


    def mail_reminder(self):
        today = fields.Date.today()

        records = self.search([
            ('expiry_date', '!=', False),
            ('notification_to', '!=', False),
        ])
        for record in records:
            expiry_date = record.expiry_date
            before_days = record.before_days or 0
            notify_date = expiry_date - timedelta(days=before_days)
            send_mail = False

            # 1 Notification on expiry date
            if record.notification_type == 'single':
                send_mail = today == expiry_date

            # 2 Notification before few days (only once)
            elif record.notification_type == 'multi':
                send_mail = today == notify_date

            # 3 Everyday till expiry date
            elif record.notification_type == 'everyday':
                send_mail = notify_date <= today <= expiry_date

            # 4 Notification on and after expiry
            elif record.notification_type == 'everyday_after':
                send_mail = expiry_date <= today <= (expiry_date + timedelta(days=before_days))

            if not send_mail:
                continue

            # Send mail to each partner
            for partner in record.notification_to:
                if not partner.email:
                    continue

                subject = _(
                    "Document Expiry Reminder: %s"
                ) % (record.name)

                body_html = f"""
                    <p>Hello {partner.name},</p>
                    <p>
                        The document <strong>{record.name}</strong>
                        for partner <strong>{record.partner_id.name}</strong>
                        will expire on <strong>{expiry_date}</strong>.
                    </p>
                    <p>Please take the necessary action.</p>
                """
                for rec in record.notification_to:
                    rec.env['portal.notification'].create({
                        'name': 'Document-' + record.name,
                        'message': subject,
                        'partner_id': rec.id,
                    })

                self.env['mail.mail'].create({
                    'subject': subject,
                    'body_html': body_html,
                    'email_to': partner.email,
                    'author_id': self.env.user.partner_id.id,
                }).send()

    @api.constrains('expiry_date')
    def _check_expiry_date(self):
        """This method is called as a constraint whenever the 'expiry_date'
         field of an 'hr.employee.document' record is modified."""
        for rec in self:
            if rec.expiry_date:
                exp_date = fields.Date.from_string(rec.expiry_date)
                if exp_date < date.today():
                    raise UserError(_('Your Document Is Expired.'))
    
    def get_portal_url(self):
        return f"/my/documents"

    def get_portal_upload_url(self):
        return f"/my/documents/{self.id}/upload"