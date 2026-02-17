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


class PdcDepositedWizard(models.TransientModel):
    _name = 'pdc.deposited.wizard'
    _description = "PDC Deposited"

    deposited = fields.Many2one('account.journal', string='Deposited',
                                domain="[('type', '=', 'bank')]")
    deposited_on = fields.Date(string='Deposited On')

    def action_add_done(self):
       pdc_id =  self.env['pdc.payment.received'].search(
            [('id', '=', self.env.context.get('active_id'))])
       if pdc_id:
           pdc_id.deposited = self.deposited
           pdc_id.deposited_on = self.deposited_on
           pdc_id.status = 'deposited'



