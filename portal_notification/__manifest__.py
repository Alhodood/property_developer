# -*- coding: utf-8 -*-
#############################################################################

#    Alhodood Technologies.
#
#    Copyright (C) 2026-TODAY Alhodood Technologies(<https://www.alhodood.com>)
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
{
    'name': 'Portal Notification',
    'version': '19.1.1',
    'category': 'Extra Tools',
    'summary': """ This module allows to Show Notifications in Portal""",
    'author': 'Alhodood Technologies',
    'depends': ['web','portal'],
    'data': [
        'security/ir.model.access.csv',
        'views/portal_notification.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'portal_notification/static/src/js/portal_notification.js',
        ],
    },
    'images': ['static/description/thumbnail.gif'],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False
}
