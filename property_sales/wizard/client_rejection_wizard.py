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
from odoo import models, fields


class ClientRejectionWizard(models.TransientModel):
    _name = 'client.rejection.wizard'
    _description = "Client Rejection Wizard"

    reason = fields.Text("Reject Reason")

    sale_id = fields.Many2one('sale.order',)


    def action_client_reject(self):
        if self.sale_id:
            self.sale_id.write({
                'state': 'rejected',
                'client_reject_reason': self.reason,
            })

            # Post in chatter
            self.sale_id.message_post(
                body=f"""
                            Client Rejected:- {self.reason}
                        """,
                subtype_xmlid="mail.mt_note",
            )