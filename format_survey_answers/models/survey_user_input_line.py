# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class SurveyUserInput(models.Model):
    _inherit = 'survey.user_input'

    project_id = fields.Many2one('project.project', 'Project', compute='compute_project_and_user',
                    store=True, help='Links to project if Project related Survey')
    user_id = fields.Many2one('res.users', 'Team Member', compute='compute_project_and_user',
                    store=True, help='links to Team Member if User Related Survey')

    @api.one
    @api.depends('user_input_line_ids.value_m2o')
    def compute_project_and_user(self):
        if len(self.user_input_line_ids) > 1:
            if self.user_input_line_ids[0].question_id.question == 'Project Name':
                self.project_id = self.user_input_line_ids[0].value_m2o
            if self.user_input_line_ids[1].question_id.question == 'Team Member' or 'Project Manager':
                self.user_id = self.user_input_line_ids[1].value_m2o

class SurveyUserInputLine(models.Model):
    _inherit = 'survey.user_input_line'

    project_id = fields.Many2one('project.project', 'Project',
                related='user_input_id.project_id', store=True)
    user_id = fields.Many2one('res.users', 'Team Member',
                related='user_input_id.user_id', store=True)
    page_id = fields.Many2one(related='question_id.page_id', string="Page", store=True)
    value = fields.Char('Answer')

    @api.model
    def create(self, vals):
        if vals['answer_type'] == 'suggestion':
            vals['value'] = self.env['survey.label'].browse(int(vals.get('value_suggested'))).value
        else:
            values = [ vals.get('value_text'), vals.get('value_number'), vals.get('value_date'),
                    vals.get('value_free_text') and vals.get('value_free_text')[:40] ]
            vals['value'] = next(value for value in values if value is not None)
        return super(SurveyUserInputLine, self).create(vals)

    @api.multi
    def write(self, vals):
        for record in self:
            if record.answer_type == 'suggestion':
                vals['value'] = self.env['survey.label'].browse(int(vals.get('value_suggested'))).value
            else:
                values = [ vals.get('value_text'), vals.get('value_number'), vals.get('value_date'),
                        vals.get('value_free_text') and vals.get('value_free_text')[:40] ]
                vals['value'] = next(value for value in values if value is not None)
        return super(SurveyUserInputLine, self).write(vals)
