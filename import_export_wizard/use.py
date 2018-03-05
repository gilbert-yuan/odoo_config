###此文件为8.0 版示例 ❤新的版本请参考使用
# -*- coding: utf-8-*-
from openerp.osv import osv, fields, orm
SUPERUSER_ID = 1
import time
#IHS6K 加班调休表增加新的类型“年假”，年假可以被调休核销
class import_annual_leave_wizard(osv.osv):

    _name = 'import.annual.leave.wizard'
    _inherit = ['import.wizard']

    def need_column_date_header(self, cr, uid, context=None):
        vals = [('employee_id', u"员工姓名"), ('age', u"年份"), ('hour_qty', u"年假小时数"), ('expire_date', u"到期日期")]
        return vals

    def return_vals_action(self, cr, uid, ids, this_id, context=None):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'import.annual.leave.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': this_id,
            'views': [(False, 'form')],
            'target': 'new',
        }

    def judge_and_write_vals(self, cr, uid, ids, data_dcit, context=None):
        employee_obj = self.pool.get('hr.employee')
        employee_ids = employee_obj.search(cr, uid, [('name', '=', data_dcit.get('employee_id'))], context=context)
        if len(employee_ids) == 0:
            raise osv.except_osv(u'错误', u'员工%s不存在！'% data_dcit.get('employee_id'))
        elif len(employee_ids) > 1:
            raise osv.except_osv(u'错误', u'此员工%s,在系统中对应多个！' % data_dcit.get('employee_id'))
        now_date_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        data_dcit.update({'employee_id': employee_ids[0], 'type': 'annual_leave', 'is_approve': True,
                          'note': u'人事统一导入年假', 'start_time': now_date_time, 'end_time': now_date_time})
        work_obj = self.pool.get('work.overtime.leave')
        work_id = work_obj.search(cr, uid, [('age', '=', int(data_dcit.get('age'))),
                                  ('employee_id', '=',  data_dcit.get('employee_id'))], context=context)
        if work_id:
            work_obj.write(cr, uid, work_id, data_dcit, context=context)
        else:
            work_obj.create(cr, uid, data_dcit, context=context)
        return True

#         <record id="dftg_import_annual_leave_wizard" model="ir.ui.view">
#             <field name="name">import.annual.leave.wizard</field>
#             <field name="model">import.annual.leave.wizard</field>
#             <field name="arch" type="xml">
#                 <form string="导入一单多发快递单号">
#                     <field name='state' invisible='1' />

#                     <div states='1'>
#                         <b>注意：</b>
#                         <p>之前曾导入过的记录会被重复导入!</p>
#                         <p>请上传之前导出的文件</p>
#                         <field name="data" filename="filename" />
#                     </div>
#                     <group states='1'>
#                         <button name='button_next' type='object' string='年假导入'/>
#                     </group>
#                     <group states='2'>
#                         <field name="selected" />
#                         <field name="imported" />
#                         <button name='button_ok' type='object' string='确定'/>
#                     </group>
#                 </form>
#             </field>
#         </record>
#         <record id="dftg_import_annual_leave_wizard_action" model="ir.actions.act_window">
#             <field name="name">年假导入</field>
#             <field name="type">ir.actions.act_window</field>
#             <field name="res_model">import.annual.leave.wizard</field>
#             <field name="view_type">form</field>
#             <field name="view_mode">form</field>
#             <field name="target">new</field>
#         </record>


class express_delivery_export_wizard(osv.osv):
    _name = 'express.delivery.export.wizard'
    _inherit = ['export.wizard']

    def model_fields_data_provide(self, cr, uid, context=None):
        model_obj = self.pool.get('sale.order.express.delivery')
        vals = [('id', u"内部序号"), ('so_id', u"销售订单"), ('consignee', u"联系人"), ('mobile_number', u"手机号码"),
                ('phone_number', u"电话号码"), ('province', u"省"), ('city', u"市"), ('county', u"县"), ('street', u"详细地址"),
                ('delivery_products', u"送货列表"), ('note', u"备注"), ('express_type_id', u"快递方式"),
                ('express_code', u"快递单号")]
        return model_obj, vals

    def return_vals_construction(self, cr, uid, ids, exported, this_id, out, to_export_ids, context=None):
        vals = {'data': out,
                'filename': u'销售订单快递发货地址%s.xls' % datetime.now().strftime("%Y%m%d"),
                'state': '2',
                'exported': exported}
        self.write(cr, uid, ids, vals, context=context)
        self.pool.get('sale.order.express.delivery').write(cr, uid, to_export_ids, {'is_export': True, 'export_date':datetime.now(),
                                                                'export_uid': uid},context=context)
        self.pool.get("sale.order.express.delivery").write(cr, uid, to_export_ids, {'is_exported': True},
                                                           context=context)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'express.delivery.export.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': this_id,
            'views': [(False, 'form')],
            'target': 'new',
        }

#      <record id="dftg_express_delivery_import_wizard" model="ir.ui.view">
#             <field name="name">express.delivery.import.wizard</field>
#             <field name="model">express.delivery.import.wizard</field>
#             <field name="arch" type="xml">
#                 <form string="导入一单多发快递单号">
#                     <field name='state' invisible='1' />

#                     <div states='1'>
#                         <b>注意：</b>
#                         <p>之前曾导入过的记录不会被重复导入</p>
#                         <p>请上传之前导出的文件</p>
#                         <field name="data" filename="filename" />
#                     </div>
#                     <group states='1'>
#                         <button name='button_next' type='object' string='导入快递单号'/>
#                     </group>
#                     <group states='2'>
#                         <field name="selected" />
#                         <field name="imported" />
#                         <button name='button_ok' type='object' string='确定'/>
#                     </group>
#                 </form>
#             </field>
#         </record>
#         <record id="dftg_express_delivery_import_wizard_action" model="ir.actions.act_window">
#             <field name="name">导入一单多发快递单号</field>
#             <field name="type">ir.actions.act_window</field>
#             <field name="res_model">express.delivery.import.wizard</field>
#             <field name="view_type">form</field>
#             <field name="view_mode">form</field>
#             <field name="target">new</field>
#         </record>
