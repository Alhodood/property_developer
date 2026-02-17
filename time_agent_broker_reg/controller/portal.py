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
from odoo import http, _
from odoo.http import request
class AgentRegisterController(http.Controller):

    @http.route(['/agent/register'], type='http', auth='public', website=True, csrf=True)
    def agent_register_form(self, token=None, **kw):
        """Render registration form. Token is used to lookup the reg.agent record created by salesman."""
        agent = None

        res_company_partners = request.env['res.company'].sudo().search([])
        res_company_partners = res_company_partners.mapped('partner_id')

        # Search all partners that are companies but not linked to any res.company
        companies = request.env['res.partner'].sudo().search([
            ('is_company', '=', True),
            ('id', 'not in', res_company_partners),
        ])
        doc_types = self.env['reg.document.type'].sudo().search([])
        return request.render('time_agent_broker_reg.portal_agent_register', {
            'agent': agent,
            'doc_types': doc_types,
            'countries': request.env['res.country'].sudo().search([]),
            'states': request.env['res.country.state'].sudo().search([]),
            'companies':companies
        })

    @http.route(['/agent/register/submit'], type='http', auth='public',website=True, methods=['POST'], csrf=True)
    def agent_register_submit(self, **post):
        """
        Handles:
        - Create / Update reg.agent using token
        - Save required documents
        - Save extra document
        - NO expiry validation
        """
        import base64

        agent = self.env['reg.agent'].sudo().search([
            ('email', '=', post.get('email')),
            ('status', 'in', ['draft','approved'])
        ], limit=1)

        if agent:
            return request.render(
                'time_agent_broker_reg.portal_already_submitted',
                {'agent': agent}
            )

        Agent = request.env['reg.agent'].sudo()
        Doc = request.env['reg.agent.document'].sudo()

        # ---------- Fetch agent by token ----------

        agent = Agent.create({
            'name': post.get('name') or 'Unknown',
            'email': post.get('email'),
            'phone': post.get('phone'),
        })

        # ---------- Update Basic Data ----------
        is_company = post.get('is_company')
        company = False
        if int(is_company):
            company = True

        country_id = int(post.get('country_id')) if post.get('country_id') else False
        state_id = int(post.get('state_id')) if post.get('state_id') else False
        company_id = int(post.get('company_id')) if post.get('company_id') else False
        agent.sudo().write({
            'name': post.get('name'),
            'email': post.get('email'),
            'phone': post.get('phone'),
            'agent_description': post.get('description'),
            'is_company':company,
            'registration_type':'link',

            'street': post.get('street'),
            'street2': post.get('street2'),
            'city': post.get('city'),
            'state_id': state_id,
            'country_id': country_id,
            'zip': post.get('zip'),
            'person_company_id':company_id
        })

        # ---------- Save Required + Extra Documents ----------
        files = request.httprequest.files

        for key in files:
            if key.startswith('doc_type_'):
                doc_type_id = int(key.replace('doc_type_', ''))
                expiry_date = post.get(f"expiry_doc_{doc_type_id}") or False

                # 🔴 THIS IS THE FIX
                for uploaded in files.getlist(key):
                    if not uploaded:
                        continue

                    data = uploaded.read()
                    Doc.create({
                        'agent_id': agent.id,
                        'doc_type_id': doc_type_id,
                        'name': request.env['reg.document.type']
                        .sudo()
                        .browse(doc_type_id)
                        .name,
                        'file': base64.b64encode(data),
                        'file_name': uploaded.filename,
                        'expiry_date': expiry_date,
                    })

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

                        Doc.create({
                            'agent_id': agent.id,
                            'name': doc_name,
                            'file': base64.b64encode(data),
                            'file_name': uploaded.filename,
                            'expiry_date': expiry_raw,
                        })

        # ---------- Mark completed and notify ----------
        agent.sudo().action_receive_submission()

        # ---------- Return Thank You Page ----------
        return request.redirect(f"/agent/thanks/{agent.id}")

    @http.route(['/agent/thanks/<int:agent_id>'], type='http', auth='public', website=True)
    def agent_thanks(self, agent_id, **kw):
        agent = request.env['reg.agent'].sudo().browse(agent_id)
        return request.render("time_agent_broker_reg.portal_agent_thanks", {
            'agent': agent,
        })