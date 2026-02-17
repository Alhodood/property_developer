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
{
    'name': 'Property Sales Management',
    'version': '19.0.0.5.5',
    'category': 'Property Management',
    'sequence': 1,
    'website': 'https://www.alhodood.com/',
    'author': 'Alhodood Technologies',
    'summary': 'Property Sales Management',
    'description': 'Property Sales Mangement For Uae ',
    'depends': ['sale_management', 'account', 'project', 'account_analytic_parent', 'stock','maintenance','base_geolocalize',
                'crm', 'sale_crm','utm','documents','purchase','accountant','hr_timesheet','pdc_payment_property','portal_notification'
                ],
    'data': [
        'data/ir_cron.xml',
        'data/ir_sequence.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'report/report.xml',
        'report/sale_offer_report_template.xml',
        'report/pdc_receipt_template.xml',
        'report/spa_report.xml',
        'views/res_company.xml',
        'views/product_template.xml',
        'views/property_project.xml',
        'views/document_type.xml',
        'views/payment_plan.xml',
        'views/sales_document.xml',
        'views/sales_unit_document.xml',
        'views/property_unit.xml',
        'views/amenities.xml',
        'wizard/share_lead_reg_link.xml',
        'views/res_partner.xml',
        'views/lead_reg_link_mail_template.xml',
        'views/sale_order_mail_template.xml',
        'views/reject_reason_template.xml',
        'views/project_milestone.xml',
        'views/project_project.xml',
        'views/portal_templates.xml',
        'views/blocking_request.xml',
         'views/payment_voucher.xml',
        'views/account_move.xml',
        'views/account_payment.xml',
        'views/crm_lead.xml',
        'views/sales_order.xml',
        'views/offer_booking.xml',
        'views/spa_view.xml',
        'views/oqood_registration.xml',
        'views/sanagging_unit.xml',
        'views/maintenance_request_view.xml',
        'views/title_deed.xml',
        'views/pre_title_deed.xml',
        'views/key_handover.xml',
        'views/payment_spa_line.xml',
        'views/pdc_payment_received.xml',
        'views/commission_sale_to_be_paid.xml',
        'views/sales_approval_request.xml',
        'views/termination_request.xml',
        'views/available_unitl_report_template.xml',
        'views/available_unitl_project_report_template.xml',
        'views/booking_form_report_template.xml',
        'report/snagging_report_template.xml',
        'report/key_handover_report_template.xml',
        'views/ir_action_report.xml',
        'views/mail_template.xml',
        'views/ternimation_notify_email_template.xml',
        'wizard/property_blocking_request.xml',
        'wizard/payment_line_upload.xml',
        'wizard/advance_retention_wizard.xml',
        'wizard/confirmation_wizard.xml',
        'wizard/unit_hold_reason.xml',
        'wizard/spa_payment_wizard.xml',
        'wizard/collected_pdc_wizard.xml',
        'wizard/client_rejection_wizard.xml',
        'wizard/project_handover_notify_wizard.xml',
        'wizard/property_price_update_wizard.xml',
        'wizard/sales_payment_update_wizard.xml',
        'wizard/discount_approval_wizard.xml',
        'wizard/discount_approved_reject_wizard.xml',
    ],
    'assets': {
    },
    'demo': [
        'data/document_type_demo.xml',
    ],
    'external_dependencies': {
    },
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}
