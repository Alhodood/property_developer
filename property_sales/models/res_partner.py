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

from odoo import fields, models, _, api
from dateutil.relativedelta import relativedelta
from datetime import timedelta
from translate import Translator


class ResPartner(models.Model):
    _inherit = 'res.partner'

    par_type = fields.Selection([
        ('lead', 'Lead'),
        ('agent', 'Agent'),
        ('occupant', 'Occupant'),
        ('tenant', 'Tenant'),
        ('landlord', 'Landlord'),
    ],
        string="Partner Type",
        tracking=True,
    )

    date_of_birth = fields.Date(
        string="Date Of Birth",
        tracking=True,
    )

    age = fields.Integer(
        string="Age",
        compute='_compute_age'
    )
    date_of_marriage = fields.Date(
        string="Date Of Marriage"
    )

    apartment_no_arabic = fields.Char(
        string='Villa/Apartment Number Arabic',
        tracking=True,
    )
    apartment_no = fields.Char(
        string='Villa/Apartment Number',
        tracking=True,
    )

    name_arabic = fields.Char(
        string="Name(arabic)",
        tracking=True,
    )
    nationality_id = fields.Many2one(
        'res.country',
        string="Nationality",
        tracking=True,
    )
    nationality_arabic = fields.Char(
        sting="Nationality (Arabic)",
        tracking=True,
    )

    emirates_id = fields.Char(
        string="Emirates ID",
        tracking=True,
    )
    emirates_id_expiry = fields.Date(
        string="Emirates ID Date Of Expiry",
        tracking=True,
    )
    emirates_id_issue = fields.Date(
        string="Emirates ID Date Of Issue",
        tracking=True,
    )

    non_resident = fields.Boolean(
        string="Non Resident",
        default=False,
        tracking=True,
    )

    visa_date_of_issue = fields.Date(
        string="Visa Date Of Issue",
        tracking=True,
    )
    place_of_issue = fields.Char(
        string="Place Of Issue",
        tracking=True,
    )

    passport_number = fields.Char(
        string="Passport No",
        tracking=True,
    )

    passport_date_of_issue = fields.Date(
        string="Passport Date Of Issue",
        tracking=True,
    )

    passport_date_of_expiry = fields.Date(
        string="Passport Date Of Expiry",
        tracking=True,
    )

    visa_number = fields.Char(
        string="Visa Number",
        tracking=True,
    )

    visa_date_of_expiry = fields.Date(
        string="Visa Date Of Expiry",
        tracking=True,
    )

    project_ids = fields.Many2many(
        'property.project',
        string="Projects",
        tracking=True,
    )

    lead_status = fields.Selection([
        ('new', 'New'),
        ('call_back', 'Call Back'),
        ('site_vist', 'Site Visit'),
        ('agent_briefing', 'Agent Briefing'),
        ('agent', 'Agent'),
        ('agent_disqualified', 'Agent Disqualified'),
        ('freelance_agent', 'Freelance Agent'),
        ('un_qualified', 'Unqualified'),
        ('converted', 'Converted')],
        string="Status",
        default='new',
        tracking=True,
    )

    lead_priority = fields.Selection([
        ('hot', 'Hot'),
        ('warm', 'Warm'),
        ('cold', 'Cold'),
        ('booked', 'Booked'),
        ('lost', 'Lost')],
        string='Priority',
        tracking=True,
    )
    campaign_id = fields.Many2one(
        'utm.campaign',
        string="Campaign",
        ondelete='set null',
        tracking=True,
    )
    medium_id = fields.Many2one(
        'utm.medium',
        string="Medium",
        ondelete='set null',
        tracking=True,
    )
    source_id = fields.Many2one(
        'utm.source',
        string="Source",
        ondelete='set null',
        tracking=True,
    )
    referred_by = fields.Char(
        string="Referred By",
        tracking=True,
    )
    property_type_id = fields.Many2one(
        'property.project.type',
        string="Property Type",
        tracking=True,
    )
    no_of_bedroom = fields.Integer(
        string="Number Of Bedrooms",
        tracking=True,
    )

    budget_range = fields.Selection(
        [('below_500', 'Below 500'),
         ('500k-1m', '500k-1M'),
         ('1M-2M', '1M-2M'),
         ('2M-3M', '2M-3M'),
         ('3M-4M', '3M-4M'),
         ('4M-5M', '4M-5M'),
         ('5M-6M', '5M-6M'),
         ('6M-7M', '6M-7M'),
         ('7M-8M', '7M-8M'),
         ('8M-9M', '8M-9M'),
         ('10M+', '10M+')],
        string="Budget Range",
        tracking=True,
    )

    preferred_language = fields.Many2one(
        'res.lang',
        string="Preferred Language",
        tracking=True,
    )
    primary_contact = fields.Selection(
        [('email', 'Email'),
         ('call', 'Call'),
         ('direct', 'Direct')
         ],
        string="Primary Contact Mode",
        tracking=True,
    )

    your_message = fields.Text(
        string="Your Message",
        tracking=True
    )

    subject = fields.Text(
        string="Subject",
        tracking=True
    )
    emirates_id_attachment_id = fields.Binary(
        string="Emirates ID"
    )
    emirates_id_filename = fields.Char(
        "Emirates ID Filename",
        tracking=True,
    )
    passport_filename = fields.Char(
        "Passport Filename",
        tracking=True,
    )
    passport_attachment_id = fields.Binary(
        string="Passport",
    )

    is_verified = fields.Boolean(
        string="Is Verified",
        default=False,
        tracking=True,
    )

    rera_number = fields.Char(
        string="RERA Registration Number",
        tracking=True
    )
    trade_license_number = fields.Char(
        string="Trade License Number",
        tracking=True
    )
    trade_license_expiry = fields.Date(
        string="Trade License Expiry Date",
        tracking=True
    )
    agent_briefing = fields.Boolean(
        string="Agent Briefing",
        default=False,
        tracking=True,
    )
    no_of_branches = fields.Integer(
        string="No of Branches",
        tracking=True
    )

    has_relationship_manager = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')],
        string="Do you have relationship manager?",
        default="no",
        tracking=True,
    )

    rm_mobile = fields.Char(
        string="Relationship Manager Mobile",
        tracking=True
    )

    rm_email = fields.Char(
        string="Relationship Manager Email",
        tracking=True
    )

    uae_residence = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')],
        string="UAE Residence?",
        default="no",
        tracking=True
    )

    passport_number_agent = fields.Char(
        string="Passport Number",
        tracking=True
    )
    passport_expiry = fields.Date(
        string="Passport Expiry Date",
        tracking=True
    )

    lead_agent_id = fields.Many2one(
        'res.partner',
        string="Agent",
        domain="[('par_type', '=', 'agent')]",
        tracking=True,
    )

    client_type = fields.Selection(
        [('direct','Direct'),
         ('indirect','Indirect')],
        string="Client Type",
    )

    sales_person = fields.Many2one(
        'res.users',
        string="Sales Person",
        tracking=True,
    )

    property_blocking_request_ids = fields.One2many(
        'blocking.request',
        'partner_id',
        string="Blocking Request",
        tracking=True,
    )

    sale_offer_ids = fields.One2many(
        'sale.order',
        'partner_id',
        string="Offers",
        tracking=True,
    )

    crm_lead_ids = fields.One2many(
        'crm.lead',
        'partner_id',
        string="Leads",
        tracking=True,
    )

    payment_ids = fields.One2many(
        'account.payment',
        'partner_id',
        string="Payments",
        groups="account.group_account_user,account.group_account_manager",
        tracking=True,
    )


    invoices_ids = fields.One2many(
        'account.move',
        'partner_id',
        string="Invoices",
        domain="[('move_type', '=', 'out_invoice')]",
    )

    crm_lead_lead_agent_ids = fields.One2many(
        'crm.lead',
        'lead_agent_id',
        string="Agent Leads"
    )

    sale_offer_lead_agent_ids = fields.One2many(
        'sale.order',
        'lead_agent_id',
        string="Agent Offers"
    )

    work_address = fields.Char(
        string="Work Address",
        tracking=True,
    )
    employer_name = fields.Char(
        string="Employer Name",
        tracking=True,
    )
    profession_job_tital = fields.Char(
        string="Profession / Job Title",
        tracking=True,
    )
    monthly_income_range = fields.Selection(
        selection=[
            ('below_5000', 'Below 5,000'),
            ('5000_10000', '5,000 – 10,000'),
            ('10000_20000', '10,000 – 20,000'),
            ('20000_50000', '20,000 – 50,000'),
            ('above_50000', 'Above 50,000'),
        ],
        string="Monthly Income Range",
        required=True,
        default='5000_10000',
        tracking=True
    )

    spa_ids = fields.One2many(
        'spa.book',
        'partner_id',
        string="Spa Bookings"
    )

    booking_offer_ids = fields.One2many(
        'offer.booking',
        'partner_id',
        string="Offer Booking"
    )

    oqood_ids = fields.One2many('oqood.registration',
                                'partner_id',
                                string="Oqood"
                                )

    snagging_ids = fields.One2many('snagging.unit',
                                   'partner_id',
                                   string="Snaggings"
                                   )
    key_handover_ids = fields.One2many('key.handover',
                                       'lead_agent_id',
                                       string="Key Handovers"
                                       )

    additional_comments = fields.Text(string="Additional Comments")

    @api.model
    def create(self, vals):
        res = super().create(vals)
        new_name = False
        # if res.emirates_id_attachment_id:
        #     new_name = res._extract_name_from_emirates_id(
        #         res.emirates_id_attachment_id, res.emirates_id_filename)
        # elif res.passport_attachment_id:
        #     new_name = res._extract_name_from_passport(
        #         res.passport_attachment_id, res.passport_filename)
        # if new_name:
        #     res.name = new_name
        # translator = Translator(to_lang="ar")
        # text = res.name
        # translation = translator.translate(text)
        # res.name_arabic = translation
        # if res.nationality_id:
        #     translator = Translator(to_lang="ar")
        #     text = res.nationality_id.name
        #     translation = translator.translate(text)
        #     res.nationality_arabic = translation
        return res

    @api.model
    def write(self, vals):
        res = super().write(vals)
        new_name = False
        # if vals.get('emirates_id_attachment_id'):
        #     new_name = self._extract_name_from_emirates_id(
        #         self.emirates_id_attachment_id, self.emirates_id_filename)
        #     if new_name:
        #         self.name = new_name
        # elif vals.get('passport_attachment_id'):
        #     if not self.emirates_id_attachment_id:
        #         new_name = self._extract_name_from_passport(
        #             self.passport_attachment_id, self.passport_filename)
        # if new_name:
        #     self.name = new_name
        if vals.get("name") or new_name:
            translator = Translator(to_lang="ar")
            text = self.name
            translation = translator.translate(text)
            self.name_arabic = translation
        return res

    @api.onchange('nationality_id')
    def _onchange_nationality_id_name(self):
        """Auto-translate English name to Arabic"""
        if self.nationality_id:
            translator = Translator(to_lang="ar")
            text = self.nationality_id.name
            translation = translator.translate(text)
            self.nationality_arabic = translation

    # @api.onchange("emirates_id_attachment_id", "passport_attachment_id")
    # def _onchange_id_passport(self):
    #     for rec in self:
    #         new_name = False
    #         if rec.emirates_id_attachment_id:
    #             new_name = rec._extract_name_from_emirates_id(
    #                 rec.emirates_id_attachment_id, rec.emirates_id_filename)
    #         elif rec.passport_attachment_id:
    #             new_name = rec._extract_name_from_passport(
    #                 rec.passport_attachment_id, rec.passport_filename)
    #         if new_name:
    #             rec.name = new_name

    # def _extract_name_from_emirates_id(self, file_data, filename):
    #     if not file_data:
    #         return False
    #
    #     binary_data = base64.b64decode(file_data)
    #
    #     # Convert PDF or Image
    #     if filename.lower().endswith(".pdf"):
    #         images = convert_from_bytes(binary_data)
    #     else:
    #         images = [Image.open(io.BytesIO(binary_data))]
    #
    #     text = ""
    #     for img in images:
    #         # Convert to OpenCV format
    #         img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    #         text += pytesseract.image_to_string(img_cv, lang="eng")
    #     text = text.replace(";", " ").replace("|", " ")
    #     # Extract only "Name" line
    #     for line in text.splitlines():
    #         if "Name" in line or "NAME" in line:
    #             return line.replace("Name", "").replace("NAME", "").replace(
    #                 ":", "").replace(":", "").replace(";", "").strip()
    #
    #     # Fallback: longest English-looking line
    #     candidates = [line.strip() for line in text.splitlines() if
    #                   line.strip().isalpha()]
    #     if candidates:
    #         return max(candidates, key=len)
    #
    #     return False

    # def _extract_name_from_passport(self, file_data, filename):
    #     if not file_data:
    #         return False
    #
    #     binary_data = base64.b64decode(file_data)
    #
    #     # Convert PDF or Image
    #     if filename.lower().endswith(".pdf"):
    #         images = convert_from_bytes(binary_data, dpi=300)
    #     else:
    #         images = [Image.open(io.BytesIO(binary_data))]
    #     for img in images:
    #         try:
    #             img_array = np.array(img)
    #             mrz = read_mrz(img_array)
    #             if mrz and mrz.valid:
    #                 return f"{mrz.surname} {mrz.names}".title()
    #         except:
    #             continue
    #     return False

    def action_verify_partner(self):
        self.is_verified = True

    def _cron_check_expiry_reminders(self):
        today = fields.Date.today()
        reminder_date = today + timedelta(days=3)
        trade_lisence_partners = self.search([
            ('trade_license_expiry', '=', reminder_date),
            ('par_type', '=', 'agent')])
        eid_partners = self.search([
            ('emirates_id_expiry', '=', reminder_date),
            ('par_type', '=', 'lead')])
        pass_partners = self.search([
            ('passport_date_of_expiry', '=', reminder_date),
            ('par_type', '=', 'lead')])
        for par in trade_lisence_partners:
            if par.sales_person.email:
                subject = f"Trade License Expiry - Reminder ❗️"
                body = f"""<p>Dear<strong> {par.sales_person.name}</strong>, </p>
                             <p>{par.name} Trade License <b>{par.trade_license_number}</b> will expire soon <b></p>
                             <ul>
                                <li>Trade License Expiry Date: <b>{par.trade_license_expiry}</b></li>
                            </ul>
                            <p>Please take necessary action before expiry</p>
                            <p>Regards,<br/>
                                Odoo System</p>"""
                mail_values = {
                    'subject': subject,
                    'body_html': body,
                    'email_to': par.sales_person.email,
                }
                self.env['mail.mail'].create(mail_values).send()
        for par in eid_partners:
            if par.sales_person.email:
                subject = f"Emirates ID Expiry - Reminder ❗️"
                body = f"""<p>Dear<strong> {par.sales_person.name}</strong>, </p>
                             <p>{par.name} Emirates ID <b>{par.emirates_id}</b> will expire soon <b></p>
                             <ul>
                                <li>Emirates ID Expiry Date: <b>{par.emirates_id_expiry}</b></li>
                            </ul>
                            <p>Please take necessary action before expiry</p>
                            <p>Regards,<br/>
                                Odoo System</p>"""
                mail_values = {
                    'subject': subject,
                    'body_html': body,
                    'email_to': par.sales_person.email,
                }
                self.env['mail.mail'].create(mail_values).send()

        for par in pass_partners:
            if par.sales_person.email:
                subject = f"Passport Expiry - Reminder ❗️"
                body = f"""<p>Dear<strong> {par.sales_person.name}</strong>, </p>
                                    <p>{par.name} Passport <b>{par.passport_number}</b> will expire soon <b></p>
                                    <ul>
                                       <li>Passport Expiry Date: <b>{par.passport_date_of_expiry}</b></li>
                                   </ul>
                                   <p>Please take necessary action before expiry</p>
                                   <p>Regards,<br/>
                                       Odoo System</p>"""
                mail_values = {
                    'subject': subject,
                    'body_html': body,
                    'email_to': par.sales_person.email,
                }
                self.env['mail.mail'].create(mail_values).send()


    @api.depends('date_of_birth')
    def _compute_age(self):
        today = fields.Date.today()
        for rec in self:
            if rec.date_of_birth:
                rec.age = relativedelta(today, rec.date_of_birth).years
            else:
                rec.age = 0


    def action_view_oqood(self):
        buyers_ids = self.env['property.buyer.detail'].sudo().search([('buyer_id','=',self.id)])
        offers = buyers_ids.mapped('offer_id')
        if offers:
            oqood_ids = self.env['oqood.registration'].sudo().search([('offer_booking','in',offers.ids)])
            if oqood_ids:
                return {
                    'name': 'Oqood',
                    'type': 'ir.actions.act_window',
                    'view_mode': 'list',
                    'res_model': 'oqood.registration',
                       'domain': [('id', 'in', oqood_ids.ids)],
                    'target': 'current',
                }

    def action_view_snagging(self):
        buyers_ids = self.env['property.buyer.detail'].sudo().search([('buyer_id','=',self.id)])
        offers = buyers_ids.mapped('offer_id')
        if offers:
            snagging_ids = self.env['snagging.unit'].sudo().search([('offer_booking','in',offers.ids)])
            if snagging_ids:
                return {
                    'name': 'Snagging',
                    'type': 'ir.actions.act_window',
                    'view_mode': 'list',
                    'res_model': 'snagging.unit',
                    'domain': [('id', 'in', snagging_ids.ids)],
                    'target': 'current',
                }

    def action_view_key_handover(self):
        buyers_ids = self.env['property.buyer.detail'].sudo().search([('buyer_id','=',self.id)])
        offers = buyers_ids.mapped('offer_id')
        if offers:
            key_hand_over = self.env['key.handover'].sudo().search([('offer_booking','in',offers.ids)])
            if key_hand_over:
                return {
                    'name': 'Key HandOver',
                    'type': 'ir.actions.act_window',
                    'view_mode': 'list',
                    'res_model': 'key.handover',
                    'domain': [('id', 'in', key_hand_over.ids)],
                    'target': 'current',
                }