# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools


class ProjectWorksheetTemplate(models.Model):
    _inherit = 'project.worksheet.template'

    def _generate_worksheet_model(self, template):
        template = super(ProjectWorksheetTemplate,self)._generate_worksheet_model(template)
        name = 'x_project_worksheet_template_' + str(template.id)
        # Drop constraint that we can only have one worksheet per task.
        task_conname = '%s_%s' % (name, 'x_task_id_uniq')
        tools.drop_constraint(self.env.cr, name, task_conname)
        # Make the template model inherit from a generic worksheet model
        model = template.model_id
        model.write({'field_id': [
            (0, 0, {
                'name': 'x_worksheet_id',
                'field_description': 'Worksheet',
                'ttype': 'many2one',
                'relation': 'project.task.worksheet.meta',
                'required': True,
                'on_delete': 'cascade',
            }),
        ]})
        # Add constraint that we can only have one worksheet per worksheet.meta
        worksheet_conname = '%s_%s' % (name, 'x_worksheet_id_uniq')
        tools.add_constraint(self.env.cr, name, worksheet_conname, 'unique(x_worksheet_id)')
        # Change the x_task_id to be a related field instead
        task_id_field = model.field_id.filtered(lambda f: f.name =='x_task_id')
        task_id_field.write({
            'related': "x_worksheet_id.task_id"
        })
        return template
