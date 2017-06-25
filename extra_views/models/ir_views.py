# -*- coding: utf-8 -*-
from odoo import models, fields

class view(models.Model):
    _inherit = 'ir.ui.view'

    type = fields.Selection([
        ('tree', 'Tree'),
        ('form', 'Form'),
        ('graph', 'Graph'),
        ('pivot', 'Pivot'),
        ('calendar', 'Calendar'),
        ('diagram', 'Diagram'),
        ('gantt', 'Gantt'),
        ('kanban', 'Kanban'),
        ('sales_team_dashboard', 'Sales Team Dashboard'),
        ('search', 'Search'),
        ('qweb', 'QWeb'),
        ('extra_views', 'extra_views')], string=u'视图类型')
