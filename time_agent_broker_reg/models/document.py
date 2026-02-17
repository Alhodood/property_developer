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
from odoo import models, fields, api
from mimetypes import guess_type

class RegAgentDocument(models.Model):
    _name = 'reg.agent.document'
    _description = 'Agent Document'

    agent_id = fields.Many2one('reg.agent', string='Agent', required=True, ondelete='cascade')
    doc_type_id = fields.Many2one('reg.document.type', string='Document Type')
    name = fields.Char(string='Document Name', required=True)
    expiry_date = fields.Date(string='Expiry Date')
    verified = fields.Selection([
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected')
    ], default='pending', string='Status')

    reason= fields.Text('Reason')
    file = fields.Binary(string='File')
    file_name = fields.Char(string='File Name')

    attachments_doc_mimetype = fields.Char("MIME Type", readonly=True,compute="_compute_mime")

    def _compute_mime(self):
        for rec in self:
            if rec.file_name:
                rec.attachments_doc_mimetype = guess_type(rec.file_name)[0] or 'application/octet-stream'
            else:
                rec.attachments_doc_mimetype = False

    def action_approve(self):
        self.write({'verified': 'verified'})

    def action_reject(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Reject Reason',
            'res_model': 'agent.document.reject.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_document_id': self.id
            }
        }
