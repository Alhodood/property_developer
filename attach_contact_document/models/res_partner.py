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
from odoo import fields, models, _, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    document_count = fields.Integer(
        compute='_compute_document_count',
        string='Documents',
        help='Count of documents.'
    )

    partner_folder_id = fields.Many2one(
        comodel_name='documents.document',
        string='Folder',
        ondelete='set null'
    )

    def _compute_document_count(self):
        """Get count of documents."""
        for rec in self:
            rec.document_count = self.env[
                'partner.document'].sudo().search_count(
                [('partner_id', '=', rec.id)])

    def action_document_view(self):
        self.ensure_one()
        return {
            'name': _('Documents'),
            'domain': [('partner_id', '=', self.id)],
            'res_model': 'partner.document',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'list,form',
            'limit': 80,
            'context': "{'default_partner_id': %s}" % self.id
        }
