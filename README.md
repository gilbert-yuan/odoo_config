odoo_config
### **主要写了一些自己平时总结的，项目的经验**
-----------------------------------------------------------------------------------------------
 1. 产品多图上传展示 （参考师兄 product_images）
 		1. 用VUE 实现前端逻辑
 		2. 支持鼠标拖拉， 把图片拖动到组件向关的位置即可
 		3. 图片顺序变更支持鼠标拖动图片改变图片顺序，会会写入数据库
-----------------------------------------------------------------------------------------------
2. 自定义导入导出，继承所写模块就可以很方便的实现，导入导出的功能( import_export_wizard )
	1. 包装了excel的读写功能，只需简单代码即可实现，正常的导入导出功能
	2. 继承简单
	3. 字段控制简单，只能导出自己规定的几个字段，导出人不能进行修改导出字段的数量（代码控制的，如果做成可配置的就更加方便了。）
-----------------------------------------------------------------------------------------------
3. python 常用知识点 （ptyhon tools）
  1. python 播放mp3 类音频的方法
  3. 读写文件常用的方法
-----------------------------------------------------------------------------------------------
4. 自己探索写的odoo的手机端的适应代码。（projectPath）
	1. 初步探索用VUX 自动转换ODOO的页面，把odoo的页面根据电脑端的配置直接转换成手机端的
	2. 优势。简单查看，快速，用来演示有些功能很方便，缺点。 缺少配置、没有可定制空间
	3.  使用方法 cd /projectPath/ 
	4.  npm install 
	5.  修改 /projectPath/config/index.js ---> target: 'http://dingding.tunnel.800890.com' 把这个链接换成 自己本机或者远程的服务（记得添加dbfilter 哟 --不然找不到是那个库的）
	6.  npm run dev
-------------------------------------------------------------------------------------------------
5. extra_views_base 模块说明
 	1. 示范性添加一个视图模块， 就是给添加一种视图类型
 	2. 仿照标准的写法进行添加视图类型
 	3. 如果有想要添加视图类型了可以仿照这个模块来进行修改
 		
-------------------------------------------------------------------------------------------------
6. odoo8 odoo11 自带导出，时间字段存在时区问题 
	1.如题 在odoo8 和odoo11中都是存在的，时区问题的影响，在系统自带的 导出文件的时候就会出现
 ```python
 # odoo 8 解决导出数据的时区问题
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

# odoo 11 解决导出数据的时区问题
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
 ------------------------
 7. python tools 模块加入pyh模块的收藏
 	1. 因为经常会用到， 计算的html 字段，进行展示一表格，之类的text 为了更加的 方便规范的使用所以决定使用这个库， 
 	2. 这个库已经停止支持，（用的人很少，试用了下感觉还行）
 	3. 
    4. pyh 模块使用方法[ http://hanxiaomax.github.io/trans/pyh-chinese-doc/](python tools 模块加入pyh模块的收藏 #1)
    5. 下面是使用片段， 感觉还是比手动拼接会高大上一点
    ```python
    from pyh import *
    page = PyH('My wonderful PyH page')
    page.addCSS('myStylesheet1.css', 'myStylesheet2.css')
    page.addJS('myJavascript1.js', 'myJavascript2.js')
    page << h1('My big title', cl='center')
    page << div(cl='myCSSclass1 myCSSclass2', id='myDiv1') << p('I love PyH!', id='myP1')
    mydiv2 = page << div(id='myDiv2')
    mydiv2 << h2('A smaller title') + p('Followed by a paragraph.')
    page << div(id='myDiv3')
    page.myDiv3.attributes['cl'] = 'myCSSclass3'
    page.myDiv3 << p('Another paragraph')
    page.printOut()
    ```
-------------------------------------------
8. odoo Redis 使用 主要使用了redis的这三个方面 (session cache redis.lock )
   1. 以为业务需要（也没啥紧急的业务，就是想研究下，说白了就是有点闲。。。）想要详细的去控制session的 存储
   		1. 然后自己就去网上搜索，最终找了个模块就是下面的链接，嗯，看起了没问题，当进一步试用的时候才发现，这个库，不行，根本不能起到作用（偶尔还是可能的是因为odoo lazycr 引起的--猜测👎 ，但是这个也是odoo的一大特色--性能提升方面）
   		2. https://github.com/Smile-SA/odoo_addons/blob/11.0/smile_redis_session_store/redis_session_store.py
   		3.  无奈只能自己把相关的代码复制到源码库里面进行详细的测试，测试发现，是可以的，这个应该也和odoo的继承的机制有关，安装的模块，始终都是在整体的框架的代码加载完成后才进行加载模块
   		4.  https://gitee.com/Gilbert_yuan_wen/openerp-china/blob/master/openerp/http.py # 详细代码在链接里面 
   	
    2. odoo的性能一直是使用odoo的人的心头之痛（这里指的不是垃圾代码引起的无所谓的消耗引起的系统很慢）
    	1. 在odoo中系统cache都是存储在内存中， 当访问系统的人增多的时候，cache的作用会越来越小，一些不必要的访问数据库，会越来越多，对odoo的性能来说是一大挑战，所以就想着把odoo的cache 存储到redis 中
    	2. 说干，就干https://github.com/gilbert-yuan/odoo_config/issues/2 这是探索的一个过程，最终结果当然是成功了呀，自己在RDM（redis 可视化工具） 中可以详细的看到缓存的使用情况
    	 
    3.  odoo 中redis.lock
    	1. 先上代码再说用处
    	2.  ```python
    	    redis_instance = redis.Redis(host=redis_params.get('redis_host', 'localhost'),
                             port=int(redis_params.get('redis_port', '6379')),
                             db=int(redis_params.get('redis_decorate_db', '2')),
                             password=redis_params.get("redis_password", ''))

    		def redis_lock(blocking=True, error_str="请稍后重试!", blocking_timeout=3, timeout=60):
                def decorator(func):
                    def wrapper(self, *args, **kwargs):
                        purchase_need_refresh_lock = redis_instance.lock("%s_%s" % (self._table, func.func_name), timeout=timeout)
                        if purchase_need_refresh_lock.acquire(blocking=blocking, blocking_timeout=blocking_timeout):
                            try:
                                func_return = func(self, *args, **kwargs)
                            except Exception as error:
                                raise error
                            finally:
                                purchase_need_refresh_lock.release()
                        else:
                            raise osv.except_osv(u'错误！', error_str)
                        return func_return
                    return wrapper
                return decorator
        ```
        3.  因为二开的功能存在多个人执行统一操作， 但是如果多人同时点击会存在数据上的重复的处理所以就 要加锁，当别人正在使用的时候其他人不能进行点击点击的效果进行延后
        4.  当然如果只是启动了一个服务的话，就用python 普通的线程锁是没有问题的，但是如果 开启了多个服务就需要多个服务共用一个锁。
        5.  至于如何无缝的开启多个服务就需要用到 用redis 进行cache 共用了
       
