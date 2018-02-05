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
    loader = jinja2.PackageLoader('odoo.addons.supplier', "html")

jinja2Env = jinja2.Environment('<%', '%>', '${', '}', '%', loader=loader, autoescape=True)


class Product(models.Model):
    _inherit = 'product.product'

    @api.model
    def get_table_json_data(self):
        empty_data = []
        for index in range(15):
            empty_data.append(['', ''])
        return simplejson.dumps(empty_data)

    images_html = fields.Text(string=u'图片列表', compute='_get_all_images_html')
    description_editor = fields.Text(compute='_get_editor_html', string=u'描述编辑器')
    description_editor_ids = fields.One2many('description.editor.row', 'product_id', u'描述记录')
    """ 
        <page string="编辑产品" attrs="{'invisible':[('id', '=', False)]}">
            <field name="description_editor" widget="html"/>
        </page>
        <page string="图片上传">
        <field name="images_html" widget="html"/>
        </page>
        XML 中文中使用方法
    """
    @api.multi
    def _get_all_images_html(self):
        for product in self:
            template = jinja2Env.get_template('images.html')
            if product.sku:
                self.images_html = template.render({'editor_id': product.id, 'editor_sku': product.sku})
  
    @api.multi
    def _get_editor_html(self):
        template = jinja2Env.get_template('editor.html')
        for product in self:
            self.description_editor = template.render({'editor_id': product.id,
                                                       'shop_id': 0,
                                                       'save_field': 'introduction'})

class DescriptionEditorRow(models.Model):
    _name = 'description.editor.row'
    _order = 'index asc'

    product_id = fields.Many2one('vop.product.template', u'产品')
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


