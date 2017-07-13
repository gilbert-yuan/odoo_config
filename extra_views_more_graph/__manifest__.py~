# -*- coding: utf-8 -*-
{
    'name': '外部视图引入',
    'version': '11.11',
    'author':'gilbert(静静)',
    'website':'',
    'summary': '引入外部js重置视图',
    'category': 'js',
    'sequence': 15,
    'description':
    '''
动作中 记得更改或者添加 extra_views. tree,kanban,form,calendar,pivot,extra_views
<extra_views string="Sales Orders" extra_views_options="[['bar',{'fields':['partner_id','user_id','amount_total']}],['pie',{'fields':['user_id']}],['pie',{'fields':['team_id']}]]">
    <field name="partner_id"/>
    <field name="user_id"/>
    <field name="team_id"/>
    <field name="amount_total" type="measure"/>
</extra_views>

	在一个odoo视图中展示出多个 视图 (针对同一模型)进而可以进行数据的多维的分析
    ''',
    'depends': ['web'],
    'data':[
        'views/webclient_templates.xml'
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'application': True,
}
