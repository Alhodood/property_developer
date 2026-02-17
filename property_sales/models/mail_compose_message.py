# -*- coding: utf-8 -*-
#############################################################################
import mimetypes

#    Alhodood Technologies.
#
#    Copyright (C) 2025-TODAY Alhodood Technologies(<https://www.alhodood.com>)
#    Author: Alhodood Technologies(<https://www.alhodood.com>)
#
#    You can modify it under the terms of the GNU Affero General Public
#    License (AGPL v3), Version 3.
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
from odoo import models

class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    def action_send_mail(self):
        """Project task value change after Mail Send"""
        res = super(MailComposeMessage, self).action_send_mail()

        # After sending, if this was triggered from estimation approval
        if self._context.get('default_model') == 'sale.order':
            sale_record = self.env[self._context['default_model']].browse(self._context['default_res_ids'])
            company = self.env.company
            property_folder = self.env['documents.document'].sudo().search([
                ('name', '=', sale_record.property_unit_id.project_id.name),
                ('type', '=', 'folder'),
                ('owner_id', '=', False),
            ], limit=1)
            if not property_folder:
                property_folder = self.env['documents.document'].sudo().create({
                    'name': sale_record.property_unit_id.project_id.name,
                    'type': 'folder',
                    'owner_id': False,
                    'company_id': company.id,
                    'access_internal': 'view',
                })

            unit_folder = self.env['documents.document'].sudo().search([
                ('name', '=', sale_record.property_unit_id.name),
                ('type', '=', 'folder'),
                ('owner_id', '=', False),
                ('folder_id', '=', property_folder.id),
            ], limit=1)
            if not unit_folder:
                unit_folder = self.env['documents.document'].sudo().create({
                    'name': sale_record.property_unit_id.name,
                    'type': 'folder',
                    'owner_id': False,
                    'access_internal': 'view',
                    'folder_id': property_folder.id
                })

            offer_folder = self.env['documents.document'].sudo().search([
                ('name', '=', 'Offer'),
                ('type', '=', 'folder'),
                ('owner_id', '=', False),
                ('folder_id', '=', unit_folder.id),
            ], limit=1)
            if not offer_folder:
                offer_folder = self.env['documents.document'].sudo().create({
                    'name': 'Offer',
                    'type': 'folder',
                    'owner_id': False,
                    'access_internal': 'view',
                    'folder_id': unit_folder.id
                })

            sale_folder = self.env['documents.document'].sudo().search([
                ('name', '=', sale_record.name),
                ('type', '=', 'folder'),
                ('owner_id', '=', False),
                ('folder_id', '=', offer_folder.id),
            ], limit=1)
            if not sale_folder:
                sale_folder = self.env['documents.document'].sudo().create({
                    'name': sale_record.name,
                    'type': 'folder',
                    'owner_id': False,
                    'access_internal': 'view',
                    'folder_id': offer_folder.id
                })

            for attachment in self.attachment_ids:
                mimetype = mimetypes.guess_type(attachment.name)[0] or 'application/octet-stream'
                document = self.env['documents.document'].sudo().create({
                    'name': attachment.name,
                    'datas': attachment.datas,
                    'type': 'binary',  # 🔥 THIS LINE FIXES EVERYTHING
                    'folder_id': sale_folder.id,
                    'owner_id': self.env.user.id,
                    'partner_id': sale_record.partner_id.id,
                    'tag_ids': [(6, 0, [])],
                    'mimetype': mimetype,
                    'res_model': self._name,
                    'res_id': self.id,
                })
        return res
