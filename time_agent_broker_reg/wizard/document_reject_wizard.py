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

class AgentDocumentRejectWizard(models.TransientModel):
    _name = 'agent.document.reject.wizard'
    _description = 'Reject Document Wizard'

    document_id = fields.Many2one('reg.agent.document',readonly=True)
    agent_id = fields.Many2one('reg.agent',readonly=True)
    reason = fields.Text("Reason", required=True)

    def confirm_reject(self):
        if self.document_id:
            self.document_id.write({
                'verified': 'rejected',
                'reason': self.reason,
            })
        elif self.agent_id:
            mail_tmpl = self.env.ref('time_agent_broker_reg.mail_template_agent_rejected', raise_if_not_found=False)
            self.agent_id.status = 'rejected'
            self.agent_id.reject_reason = self.reason
            if mail_tmpl:
                # the template can use object.reject_reason
                mail_tmpl.send_mail(self.agent_id.id, force_send=True)
        return {'type': 'ir.actions.act_window_close'}
