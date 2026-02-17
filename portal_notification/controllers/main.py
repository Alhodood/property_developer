# -*- coding: utf-8 -*-
#############################################################################

#    Alhodood Technologies.
#
#    Copyright (C) 2026-TODAY Alhodood Technologies(<https://www.alhodood.com>)
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
import json
from odoo import http
from odoo.http import request

class PortalNotificationController(http.Controller):

    @http.route('/my/notifications', type='http', auth='user', website=True)
    def portal_notifications(self):
        partner = request.env.user.partner_id
        notifications = request.env['portal.notification'].sudo().search([
            ('partner_id', '=', partner.id)
        ],limit=100)
        notifications_list = []
        for n in notifications:
            notifications_list.append({
                'id': n.id,
                'name': n.name,
                'message': n.message,
                'is_read': n.is_read,  # store as primitive
                'create_date': n.create_date.strftime('%d/%m/%Y %H:%M'),
            })

        notifications.sudo().write({'is_read': True})
        return request.render('portal_notification.portal_notifications_page', {
            'notifications': notifications_list
        })

    @http.route('/portal/get_notification_count', type='http', auth='user', methods=['GET','POST'])
    def get_notification_count(self):
        partner = request.env.user.partner_id
        count = request.env['portal.notification'].sudo().search_count([
            ('partner_id', '=', partner.id),
            ('is_read', '=', False)
        ])
        return request.make_response(
            json.dumps({'count': count}),
            headers=[('Content-Type', 'application/json')]
        )
