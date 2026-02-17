from dateutil.relativedelta import relativedelta

from odoo import fields, models

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    joining_date = fields.Date(string="Join Date")
    gratuity_ids = fields.One2many(
        'employee.gratuity',
        'employee_id',
        string='Gratuity'
    )

    def generate_gratuity(self):
        today = fields.Date.today()
        Gratuity = self.env['employee.gratuity'].sudo()

        employees = self.sudo().search([('active', '=', True),
        ('joining_date', '!=', False)])

        gratuities = self.env['employee.gratuity'].sudo().search([])
        gratuities.unlink()

        for employee in employees:
            start_date = employee.joining_date
            # avoid duplicate record for same month
            Gratuity.create({
                'employee_id': employee.id,
                'user_id': employee.user_id.id,
                'joining_date': start_date,
                'last_working_day': today,
                'wage': employee.wage,
            })


class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'
    joining_date = fields.Date(string="Join Date")