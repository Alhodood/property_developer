# -*- coding: utf-8 -*-
#############################################################################
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
{
    'name': 'Agent Registration & Document Vault',
    'version': '19.0.0.0.5',
    'category': 'Verifion',
    'author': 'Alhodood Technologies',
    'summary': 'Time Customization',
    'description': 'Agent Registration Link',
    'depends': [
        "base", "contacts", "portal", "mail", "web","website","purchase",'property_sales'
    ],
    'data': [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence.xml",
        "data/demo.xml",
        "data/mail_templates.xml",
        "views/agent_views.xml",
        "views/document_type_views.xml",
        "views/document_views.xml",
        "views/portal_templates.xml",
        "wizard/share_agent_reg_link.xml",
        "views/menu_items.xml",
        "wizard/document_reject_wizard.xml"
    ],
    'assets': {},
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
