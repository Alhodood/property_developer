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
from odoo import api, models, fields


class PdcReasonReceiveWizard(models.TransientModel):
    _name = 'pdc.reason.receive.wizard'
    _description = "Reason"

    feedback = fields.Text('Feedback')

    def action_add_feedback(self):
        payment_receive = self.env['pdc.payment.received'].browse(self.env.context['active_id'])
        if self.env.context.get('state') == 'returned':
            payment_receive.return_reason = self.feedback
        elif self.env.context.get('state') == 'hold':
            payment_receive.hold_reason = self.feedback
        else:
            payment_receive.reject_reason = self.feedback


