#!/usr/bin/python3
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)
import base64
import StringIO
import xlrd,xlwt


class ExportWizard(models.Model):
    _name = 'export.wizard'

    selected = fields.Integer(u'当前已选', readonly=1, default=lambda self: len(self._context.get('active_ids'))),
    exported = fields.Integer(u'之前已导出', readonly=1),
    filename = fields.Char(u'文件名', readonly=1),
    data = fields.Binary(u'文件', readonly=1),
    state = fields.Selection([('1', '1'), ('2', '2')], default=1, string=u'状态'),

    @api.multi
    def model_fields_data_provide(self):
        return True

    @api.multi
    def model_export_data_header_field(self, selected):
        model_obj, filed_list_tuple = self.model_fields_data_provide()
        to_export_ids = model_obj.search([('id', 'in', selected)])
        exported = len(self._context.get('active_ids')) - len(to_export_ids)
        export_data = model_obj.export_data(selected, [field_name for field_name, fields_string in filed_list_tuple]).get(
            'datas', [])
        return filed_list_tuple, export_data, exported, to_export_ids

    @api.multi
    def return_vals_construction(self, exported, this_id, out, to_export_ids):
        pass

    #导出确认
    @api.multi
    def button_next(self):
        ids = self.ids
        if self._context is None:
            context = {}
        if isinstance(ids, int):
            this_id = ids
        else:
            this_id = ids[0]
        xls = StringIO.StringIO()
        # 发货记录导出的字段 [卡号 产品 快递单号 快递方式 联系人 省 市 县 街道 手机 电话 期望发货日期]
        xls_workbook = xlwt.Workbook(encoding="utf8")
        data_sheet = xls_workbook.add_sheet('data')
        selected = context.get('active_ids')
        filed_list_tuple, export_data, exported, to_export_ids = self.model_export_data_header_field(selected)
        for index, (filed_name, fields_string) in enumerate(filed_list_tuple):
            data_sheet.write(0, index, fields_string)
        for row, records in enumerate(export_data):
            for column, record in enumerate(records):
                export_value = record
                if type(record) is float or type(record) is int:
                    export_value = str(record or u" ")    # 将数字转成字符串，以免被excel变成科学计数法
                data_sheet.write(row+1, column, export_value)
        xls_workbook.save(xls)
        xls.seek(0)
        out = base64.encodestring(xls.getvalue())
        return self.return_vals_construction(exported, this_id, out, to_export_ids)


class ImportWizard(models.Model):
    _name = 'import.wizard'

    selected = fields.Integer(u'总导入条数', readonly=1),
    imported = fields.Integer(u'有效条数', readonly=1),
    to_import = fields.Text(u'需导入的有效条目'),
    data = fields.Binary(u'请选择文件上传'),
    template_data = fields.Binary(u'模版', readonly=1),
    template_file_name = fields.Char(u'模版文件名', readonly=1),
    state = fields.Selection([('1', '1'), ('2', '2')], default='1', string=u'状态'),

    @api.multi
    def need_column_date_header(self):
        return True

    @api.multi
    def judge_data_is_pass(self, record, need_head):
        return True

    @api.multi
    def return_vals_action(self, this_id):
        return True

    @api.multi
    def judge_and_write_vals(self, data_dcit):
        return True

    #导入确认
    @api.multi
    def button_next(self):
        self.ensure_one()
        ids = self.ids
        if self._context is None:
            context = {}
        if isinstance(ids, int):
            this_id = ids
        else:
            this_id = ids[0]
        this = self
        if not this.data:
            raise UserError(u'错误', u'请关掉导入页面重新导入一遍')
        xls_file = StringIO.StringIO(base64.decodestring(this.data))
        workbook = xlrd.open_workbook(file_contents=xls_file.read())
        worksheet = workbook.sheets()[0]
        need_head = dict(self.need_column_date_header())
        selected = 0  # 导入文件的总行数（不包含header行）
        to_import = []  # 有效的行数（已输入了快递单号和快递方式，且erp中未记录发货的）
        nrows = worksheet.nrows
        for i in range(nrows):
            selected += 1
            record = worksheet.row_values(i)
            if i == 0:
                header = record
                if any([True for key, val in need_head.items() if header.count(val) > 1 or header.count(val) == 0]):
                    raise UserError(u'错误', u'文件格式有误，请重新上传')
            else:
                #不需要严格的判断每个格子都有值(而且格子中还有可能非null的0、False、''空字符串等情况)
                if any([record[header.index(val)] for key, val in need_head.items()]):
                    is_pass = self.judge_data_is_pass(record, need_head)
                    if is_pass in [None, True]:
                        to_import.append({key: record[header.index(val)] for key, val in need_head.items()})
        if selected > 0:
            selected -= 1
        imported = len(to_import)
        vals = {'state': '2',
                'selected': selected,
                'imported': imported,
                'to_import': to_import}

        self.write(vals)
        return self.return_vals_action(this_id)

    @api.multi
    def button_ok(self):
        to_import = eval(self.to_import)
        if not to_import:
            raise UserError(u'错误', u'文件中没有需要导入的行')
        for data_dcit in to_import:
            self.judge_and_write_vals(data_dcit)
        return True

    #导出excel模版
    @api.multi
    def export_template_xls(self):
        xls = StringIO.StringIO()
        xls_workbook = xlwt.Workbook(encoding="utf8")
        data_sheet = xls_workbook.add_sheet('data')
        fileds_dict = self.need_column_date_header()
        for index, (filed_name, fields_string) in enumerate(fileds_dict):
            data_sheet.write(0, index, fields_string)
        xls_workbook.save(xls)
        xls.seek(0)
        out = base64.encodestring(xls.getvalue())
        self.write({'template_data': out, 'template_file_name': u'模版.xls'})
        return {
             'type': 'ir.actions.act_url',
             'url': '/web/binary/saveas?model=' + self._name + '&field=template_data&id=%s&filename_field=template_file_name' % (self._ids[0]),
             'target': 'self',
        }