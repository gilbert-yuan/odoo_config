# odoo_config
主要写了一些自己平时总结的，项目的经验
----------------------------------
1.产品多图上传展示 （参考师兄 product_images）
----------------------------------
2.自定义导入导出，继承所写模块就可以很方便的实现，导入导出的功能( mport_export_wizard )
------------------------------------------------------
3.python 常用知识点 （ptyhon tools）
  python 播放mp3 类音频的方法
  读写文件常用的方法
--------------------------------------------------
4.自己探索写的odoo的手机端的适应代码。（projectPath）
-----------------------------------
5.odoo8 odoo11 自带导出，时间字段存在时区问题 
 ```
from openerp.fields import Datetime, Field
ISODATEFORMAT = '%Y-%m-%d'

Newdatetime = Datetime.convert_to_export
def convert_to_export(self, value, env):
 timezone = pytz.timezone(env.context.get('tz'))
    return_val = Newdatetime(self, value, env)
   if isinstance(return_val, datetime.datetime) and return_val:
         return self.to_string(return_val.replace(tzinfo=pytz.timezone('UTC')).astimezone(timezone))
   elif return_val:
          return self.to_string(self.from_string(return_val).replace(tzinfo=pytz.timezone('UTC')).astimezone(timezone))
        return return_val
Datetime.convert_to_export = convert_to_export



import datetime, pytz
from odoo.fields import Datetime

Newdatetime = Datetime.convert_to_export


def convert_to_export(self, value, record):
 
  timezone = pytz.timezone(record._context.get('tz'))
  return_val = Newdatetime(self, value, record)
  if isinstance(return_val, datetime.datetime) and return_val:
      return self.to_string(return_val.replace(tzinfo=pytz.timezone('UTC')).astimezone(timezone))
  elif return_val:
       return self.to_string(self.from_string(return_val).replace(tzinfo=pytz.timezone('UTC')).astimezone(timezone))
 return return_val

Datetime.convert_to_export = convert_to_export
 ```
