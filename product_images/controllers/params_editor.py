#!/usr/bin/python3
from odoo import http
from odoo.http import request
from werkzeug.datastructures import FileStorage
import simplejson
import os
import re, uuid
from odoo import tools


class ParamsEditor(http.Controller):
    def __init__(self):
        self.login_user = False
        self.login_session = False

    @http.route('/editor/get', auth='public', csrf=False)
    def editor_get(self, osv_info, editor_id, ):
        osv_info = simplejson.loads(osv_info)
        return request.make_response(simplejson.dumps(
            [{
                'id': row.id,
                'index': row.index,
                'value': row.value,
                'component': row.component,
            } for row in getattr(request.env[osv_info.get('model', 'product.template')].browse(int(editor_id)), osv_info.get('field', 'description_editor_ids'))]
        ))

    def _generate_image_path(self, model, editor_id, file):
        if not file or not isinstance(file, FileStorage):
            return ''

        def make_dir(main_direction, direction):
            direction = os.path.join(main_direction, direction)
            if not os.path.exists(direction):
                os.mkdir(direction)
            if not os.path.isdir(direction):
                raise ValueError(u'错误, 默认图片文件夹%s已经存在且不是文件夹' % direction)
        direction = request.env['ir.config_parameter'].get_param('dfzx_supplier.editor_image_folder')
        if direction:
            if not os.path.exists(direction) or not os.path.isdir(direction):
                raise ValueError(u'错误，系统配置中获取到的路径不不是文件夹或不存在')
        else:
            main_direction = tools.config.filestore(request.env.cr.dbname)
            img_direction = 'editor_image'
            first_direction = os.path.join(img_direction, editor_id[0:2])
            direction = os.path.join(first_direction, editor_id)
            make_dir(main_direction, img_direction)
            make_dir(main_direction, first_direction)
            make_dir(main_direction, direction)
        pattern = '(.*?)(\.jpg|\.jpeg|\.png|\.gif)'
        file_new_name = file.filename
        file_name = re.findall(pattern, file_new_name)
        if file_name:
            file_new_name = "%s%s" % (uuid.uuid4().hex, file_name[0][1])
        filename = os.path.join(direction, model + editor_id + file_new_name)
        file.save(os.path.join(main_direction, filename))
        return 'editor_image?filename=' + filename

    @http.route('/editor/save', auth='public', csrf=False)
    def editor_save(self, osv_info, editor_id, delete_items, **args):
        osv_info = simplejson.loads(osv_info)
        editor_row_obj = request.env[osv_info.get('model_line', 'description.editor.row')]
        res = []
        image_id_keys = list(filter(lambda item: item.endswith('-id'), args.keys()))
        for index in range(len(args) - len(image_id_keys)):
            item = args.get(str(index), None)
            write_val, create_val = {}, {}
            write_id = False
            if str(index) + '-id' in args:
                write_id = simplejson.loads(args[str(index) + '-id']).get('id')
                if write_id:
                    write_val = {'index': index}
                else:
                    create_val = {
                        osv_info.get('editor_field', 'product_id'): int(editor_id),
                        'value': self._generate_image_path(osv_info.get('model', 'product.template'), editor_id, item),
                        'index': index,
                        'component': 'image-input',
                    }
            elif item:
                item = simplejson.loads(item)
                if item.get('id'):
                    write_id = item.get('id')
                    write_val = {
                        'value': item.get('value'),
                        'index': index,
                    }
                else:
                    create_val = {
                        osv_info.get('editor_field', 'product_id'): int(editor_id),
                        'value': item.get('value'),
                        'index': index,
                        'component': item.get('component'),
                    }
            if write_val:
                editor_row = editor_row_obj.browse(int(write_id))
                editor_row.write(write_val)
            if create_val:
                res.append([index, editor_row_obj.create(create_val).id])
        if delete_items:
            delete_items_ids = list(map(int, simplejson.loads(delete_items)))
            (editor_row_obj.browse(delete_items_ids)).unlink()
        write_model = request.env[osv_info.get('model', 'product.template')]
        self.write_html_field(osv_info, osv_info.get('save_field', 'introduction'), editor_id, write_model)
        request.env.cr.commit()
        return request.make_response(simplejson.dumps(res))

    def write_html_field(self, osv_info, save_field, editor_id, write_model):
        html_list = []
        editor_row_obj = request.env[osv_info.get('model_line', 'description.editor.row')]
        for editor_row in editor_row_obj.search([('product_id', '=', int(editor_id))]):
            if editor_row.component == 'image-input':
                html_list.append("""<img style="text-align:center;min-width:400px;max-width:600px;padding:10px;margin:10px;"src="http://%s/%s"/>"""
                                 % (request.httprequest.host, editor_row.value))
            elif editor_row.component == 'text-input':
                html_list.append("""%s""" % editor_row.value)
        write_model_row = write_model.browse(editor_id)
        write_model_row[save_field] = """<div style="text-align:center;min-width:400px;max-width:600px;padding:10px;margin:10px;">%s</div>""" % ''.join(html_list)

    @http.route('/editor_image', auth='public')
    def editor_image(self, filename, **kwargs):
        if filename and filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            main_direction = tools.config.filestore(request.env.cr.dbname)
            if not os.path.isfile(filename):
                filename = os.path.join(main_direction, filename)
            if not os.path.isfile(filename):
                return ''
            with open(filename, 'rb') as img:
                response = request.make_response(img.read())
                suffix = filename[filename.rfind('.') + 1:]
                response.headers['Content-Type'] = 'image/' + suffix
                response.headers['Content-Disposition'] = 'attachment;filename=%s' % filename
                return response
        return ''

    @http.route('/images/get', auth='public', csrf=False)
    def images_get(self, osv_info, editor_id, **kws):
        return request.make_response(simplejson.dumps(
            [{
                'id': row.id,
                'type': 'ss',
                'index': row.order_sort,
                'value': row.image_path,
                'component': 'image-input',
            } for row in request.env['product.image'].search([('template_id', '=', int(editor_id))])]
        ))

    @http.route('/image/change_order', auth='public', type='json', csrf=False)
    def images_change_order(self, **kws):

        if request.jsonrequest.get('ids') and request.jsonrequest.get('ids') != ['undefined']:
            try:
                request.env.cr.execute("""UPDATE product_image ji SET
                                            order_sort=(select order_sort + 100  
                                            from product_image jin where jin.id=ji.id) 
                                             WHERE id in (%s);""" % ','.join(request.jsonrequest.get('ids')))
                for image in request.jsonrequest.get('change_list'):
                    if not image.get('id'):
                        continue
                    request.env.cr.execute("""UPDATE product_image ji SET  order_sort=%s,is_primary=%s
                                              WHERE id = %s""" % (image.get('index'),
                                                                  not int(image.get('index')),
                                                                  image.get('id')))
                    if not int(image.get('index')):
                        request.env.cr.execute("""UPDATE product_template jp SET image_path='%s' WHERE id = '%s'""" %
                                               (image.get('file_url'), image.get('product_id')))
                return {'result': 'success'}
            except Exception as E:
                return {'result': 'error', 'message': simplejson.dumps(E)}

    @http.route('/image/delete', auth='public', type='json', csrf=False)
    def images_delete(self, **kws):
        try:
            request.env.cr.execute("""DELETE FROM product_image WHERE id=%s""" % request.jsonrequest.get('id'))
            return {'result': 'success'}
        except Exception as E:
            return {'result': 'error', 'message': simplejson.dumps(E)}

    @http.route('/images/add', auth='public', type='http', csrf=False)
    def images_add(self, **kws):
        file_url = self._generate_image_path('product.image', kws.get('product_id'), kws.get('file'))
        request.env['product.image'].create({'template_id': kws.get('product_id'),
                                             'image_path': file_url,
                                             'order_sort': kws.get('index'),
                                             'is_primary': not (int(kws.get('index')) - 1)})
        if kws.get('index') == '1':
            request.env.cr.execute("""UPDATE product_template jp SET image_path='%s' WHERE id = %s""" %
                                   (file_url, kws.get('product_id')))
