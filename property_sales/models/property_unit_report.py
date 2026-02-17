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
from odoo import models, api

class ReportAvailablePropertyUnit(models.AbstractModel):
    _name = 'report.property_sales.report_available_property_unit'
    _description = 'Available Property Unit Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        units = self.env['property.unit'].browse(docids)
        return {
            'doc_ids': units.ids,
            'doc_model': 'property.unit',
            'docs': units,
            'company': self.env.company,
        }
