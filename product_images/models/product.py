#!/usr/bin/python3
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
import itertools
import odoo
import simplejson
import os
import sys
import jinja2

if hasattr(sys, 'frozen'):
    # When running on compiled windows binary, we don't have access to package loader.
    path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'html'))
    loader = jinja2.FileSystemLoader(path)
else:
    loader = jinja2.PackageLoader('odoo.addons.product_images', "html")

jinja2Env = jinja2.Environment('<%', '%>', '${', '}', '%', loader=loader, autoescape=True)


class ProductImage(models.Model):
    _name = "product.image"

    image_path = fields.Char(u'产品图片地址', help="http://img13.360buyimg.com/n0/")
    is_primary = fields.Boolean(u'是主图')
    order_sort = fields.Integer(u'图片顺序')
    template_id = fields.Many2one('product.template', string=u'产品', index=True)

    _sql_constraints = [
        ('product_template_sort_uniq', 'unique(template_id, order_sort)', "SKU 图片顺序 已经存在请核对后再进行添加 !"),
    ]


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    images_html = fields.Text(string=u'图片列表', compute='_get_all_images_html')
    description_editor = fields.Text(compute='_get_editor_html', string=u'描述编辑器')
    description_editor_ids = fields.One2many('description.editor.row', 'product_id', u'描述记录')
    image_path = fields.Char(u'产品图片地址', help="http://img13.360buyimg.com/n0/")
    introduction = fields.Text(u'产品详细描述')

    @api.multi
    def _get_all_images_html(self):
        for product in self:
            template = jinja2Env.get_template('images.html')
            self.images_html = template.render({'editor_id': product.id})
    @api.multi
    def _get_editor_html(self):
        template = jinja2Env.get_template('editor.html')
        for product in self:
            self.description_editor = template.render({'editor_id': product.id,
                                                       'save_field': 'introduction'})

class DescriptionEditorRow(models.Model):
    _name = 'description.editor.row'
    _order = 'index asc'

    product_id = fields.Many2one('product.template', u'产品')
    index = fields.Integer(u'序号')
    value = fields.Text(u'实际值')
    component = fields.Char(u'组件')

    @api.multi
    def unlink(self):
        for row in self:
            if row.component == 'image-input':
                filename = row.value.lstrip('editor_image?filename=')
                if os.path.isfile(filename):
                    os.remove(filename)
        return super(DescriptionEditorRow, self).unlink()
