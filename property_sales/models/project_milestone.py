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

from odoo import api, models, fields


class ProjectMilestone(models.Model):
    _inherit = 'project.milestone'

    start_date = fields.Date(string="Start Date")
    planned_start_date = fields.Date(string="Planned Start Date")
    planned_end_date = fields.Date(string="Planned End Date")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')
    ], string="Status", default='draft', tracking=True)

    starting_delay = fields.Integer(string="Starting Delay", compute="_compute_delays", store=True)
    closing_delay = fields.Integer(string="Closing Delay", compute="_compute_delays", store=True)
    actual_progress = fields.Float(string="% Calculated By Property Manager")
    rera_progress = fields.Float(string="% Calculated by RERA")

    @api.depends('start_date', 'deadline', 'state')
    def _compute_delays(self):
        today = fields.Date.today()
        for record in self:
            if record.start_date and record.state in ('draft', 'pending') and today > record.start_date:
                record.starting_delay = (today - record.start_date).days
            else:
                record.starting_delay = 0
            if record.deadline and record.state != 'completed' and today > record.deadline:
                record.closing_delay = (today - record.deadline).days
            else:
                record.closing_delay = 0

    def action_set_pending(self):
        self.state = 'pending'

    def action_set_in_progress(self):
        self.state = 'in_progress'

    def action_set_completed(self):
        self.state = 'completed'
        self.is_reached = True

    def action_view_tasks_milestones(self):
        return {
            'name': 'Milestone Tasks',
            'type': 'ir.actions.act_window',
            'view_mode': 'list',
            'res_model': 'project.task',
            'views': [(self.env.ref('property_sales.view_project_task_tree_milestone').id, 'list')],
            'domain': [('milestone_id', '=', self.id), ('project_id', '=', self.project_id.id)],
            'target': 'new',
            'context': {
                'create': False,
                'delete': False,
                'edit': False
            },

        }
