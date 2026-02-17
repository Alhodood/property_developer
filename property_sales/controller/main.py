#############################################################################
#    Alhodood Technologies.
#    Copyright (C) 2024-TODAY Alhodood Technologies(<https://www.alhodood.com>)
#    Author: Alhodood Technologies(<https://www.alhodood.com>)
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
from odoo import http
from odoo.exceptions import UserError
from odoo.http import request

class SaleOfferController(http.Controller):

    @http.route(['/sale/offer/accept'], type='http', auth='public', website=True)
    def accept_offer(self, token, id, **kwargs):
        sale_order = request.env['sale.order'].sudo().search([('id','=',int(id)), ('access_token','=',token)])
        if not sale_order:
            return "Invalid link or expired."
        sale_order.sudo().write({'state': 'accepted'})
        return f"Thank you! You have accepted the offer {sale_order.name}."

    @http.route(['/sale/offer/decline'], type='http', auth='public', website=True)
    def decline_offer(self, token, id, **kwargs):
        sale_order = request.env['sale.order'].sudo().search([('id','=',int(id)), ('access_token','=',token)])
        if not sale_order:
            return "Invalid link or expired."

        if sale_order.state in ['rejected', 'accepted']:
            return request.render(
                'property_sales.sale_offer_already_done',
                {'sale_order': sale_order}
            )
        # sale_order.sudo().write({'state': 'rejected'})
        return request.render('property_sales.sale_offer_reject_page', {
            'sale_order': sale_order,
            'token': token,
        })

    @http.route('/sale/offer/decline/submit', type='http', auth='public', methods=['POST'], website=True)
    def decline_offer_submit(self, id=None, token=None, reason=None, **kw):
        sale_order = request.env['sale.order'].sudo().search([
            ('id', '=', int(id)),
            ('access_token', '=', token)
        ], limit=1)

        if not sale_order:
            return "Invalid link or expired."

        # Reject with reason
        sale_order.write({
            'state': 'rejected',
            'client_reject_reason': reason,
        })

        # Log in chatter
        sale_order.message_post(
            body=f"""
                Offer Rejected by Client:- {reason}
            """,
            subtype_xmlid="mail.mt_note",
        )
        return request.render(
            'property_sales.sale_offer_reject_thank_you',
            {
                'sale_order': sale_order
            }
        )

    @http.route(['/lead/register'], type='http', auth='public', website=True, csrf=True)
    def lead_register_form(self, token=None, **kw):
        lead = None

        res_company_partners = request.env['res.company'].sudo().search([])
        res_company_partners = res_company_partners.mapped('partner_id')

        # Search all partners that are companies but not linked to any res.company
        companies = request.env['res.partner'].sudo().search([
            ('is_company', '=', True),
            ('id', 'not in', res_company_partners),
        ])
        doc_types = self.env['partner.document.type'].sudo().search([])
        return request.render('property_sales.portal_lead_register', {
            'lead': lead,
            'doc_types': doc_types,
            'countries': request.env['res.country'].sudo().search([]),
            'states': request.env['res.country.state'].sudo().search([]),
            'companies': companies
        })

    @http.route(['/lead/register/submit'], type='http', auth='public', website=True, methods=['POST'], csrf=True)
    def lead_register_submit(self, **post):
        """
        Handles:
        - Create / Update res.partner using token
        - Save required documents
        - Save extra document
        - NO expiry validation
        """
        import base64

        lead = self.env['res.partner'].sudo().search([
            ('email', '=', post.get('email')),
        ], limit=1)

        if lead:
            return request.render(
                'property_sales.portal_already_submitted',
                {'lead': lead}
            )

        Doc = self.env['partner.document'].sudo()

        country_id = int(post.get('country_id')) if post.get('country_id') else False
        state_id = int(post.get('state_id')) if post.get('state_id') else False
        desc = post.get('description')
        lead = lead.create({
            'name': post.get('name'),
            'phone': post.get('phone'),
            'email': post.get('email'),
            'par_type': 'lead',
            'street': post.get('street'),
            'street2': post.get('street2'),
            'city': post.get('city'),
            'state_id': state_id,
            'zip': post.get('zip'),
            'country_id': country_id,
            'additional_comments':desc
        })

        files = request.httprequest.files

        # Helper function to create attachment and document
        def create_document(name, file_field, number_field=None, issue_field=None, expiry_field=None):
            uploaded_files = files.getlist(file_field)
            if uploaded_files or post.get(number_field) or post.get(issue_field) or post.get(expiry_field):
                for uploaded in uploaded_files:
                    if not uploaded or not uploaded.filename:
                        continue
                    data = uploaded.read()
                    if not data:
                        continue

                    attachment = request.env['ir.attachment'].create({
                        'name': uploaded.filename,
                        'type': 'binary',
                        'datas': base64.b64encode(data),
                        'res_model': 'partner.document',
                        'res_id': 0,  # temporary
                    })

                    doc_vals = {
                        'partner_id': lead.id,
                        'name': name,
                        'pdoc_attachment_ids': [(4, attachment.id)],
                    }
                    if number_field:
                        doc_vals['name'] = post.get(number_field)
                    if issue_field:
                        doc_vals['issue_date'] = post.get(issue_field)
                    if expiry_field:
                        doc_vals['expiry_date'] = post.get(expiry_field)

                    doc = Doc.create(doc_vals)
                    attachment.write({'res_id': doc.id})
                    if number_field == 'passport_no':
                        lead.sudo().write({
                            "passport_number": doc_vals['name'],
                            "passport_attachment_id": base64.b64encode(data).decode('utf-8'),
                            "passport_date_of_issue": doc_vals['issue_date'],
                            "passport_date_of_expiry": doc_vals['expiry_date'],
                        })
                    elif number_field == 'emirates_no':
                        lead.sudo().write({
                            "emirates_id":doc_vals['name'],
                            "emirates_id_attachment_id":base64.b64encode(data).decode('utf-8'),
                            "emirates_id_issue":doc_vals['issue_date'],
                            "emirates_id_expiry":doc_vals['expiry_date'],
                        })

        # Passport
        create_document(
            name="Passport",
            file_field='doc_passport',
            number_field='passport_no',
            issue_field='passport_issue_date',
            expiry_field='expiry_passport'
        )

        # Emirates ID
        create_document(
            name="Emirates ID",
            file_field='doc_emirates_id',
            number_field='emirates_no',
            issue_field='emirates_issue_date',  # make sure you update HTML input name accordingly
            expiry_field='expiry_emirates_id'
        )

        # EXTRA DOCS (extra_doc_file_<X>)
        files = request.httprequest.files

        for key in files:
            if key.startswith('extra_doc_file_'):
                idx = key.replace('extra_doc_file_', '')
                doc_name = post.get(f"extra_doc_name_{idx}") or "Extra Document"
                expiry_raw = post.get(f"extra_doc_expiry_{idx}") or False

                for uploaded in files.getlist(key):
                    if not uploaded or not uploaded.filename:
                        continue

                    data = uploaded.read()
                    if not data:
                        continue

                    attachment = request.env['ir.attachment'].create({
                        'name': uploaded.filename,
                        'type': 'binary',
                        'datas': base64.b64encode(data),
                        'res_model': 'partner.document',
                        'res_id': 0,  # temporary, will link after Doc creation
                    })

                    doc = Doc.create({
                        'partner_id': lead.id,
                        'name': doc_name,
                        'pdoc_attachment_ids': [(4, attachment.id)],  # link attachment
                        'expiry_date': expiry_raw,
                    })
                    attachment.write({'res_id': doc.id})

        # ---------- Return Thank You Page ----------
        return request.redirect(f"/lead/thanks/{lead.id}")

    @http.route(['/lead/thanks/<int:lead_id>'], type='http', auth='public', website=True)
    def lead_thanks(self, lead_id, **kw):
        lead = request.env['res.partner'].sudo().browse(lead_id)
        return request.render("property_sales.portal_lead_thanks", {
            'lead': lead,
        })
