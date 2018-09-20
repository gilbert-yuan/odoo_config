# -*- coding: utf-8 -*-
from openerp.addons.web import http
from openerp.addons.web.http import request
from openerp.modules.registry import RegistryManager
from contextlib import closing
import openerp
from openerp.osv import fields
from datetime import datetime, timedelta
import hashlib
import os, re
import sys
import random
import jinja2
import requests
import simplejson
from reportlab.graphics.barcode import createBarcodeDrawing
from wechatpy.enterprise.crypto import WeChatCrypto
from wechatpy.exceptions import InvalidSignatureException
from wechatpy.enterprise.exceptions import InvalidCorpIdException
from wechatpy.enterprise import parse_message, create_reply
from openerp.addons.auth_signup.controllers.main import AuthSignupHome as Home
from openerp.addons.web.controllers.main import login_redirect, db_monodb, ensure_db, set_cookie_and_redirect, \
    login_and_redirect
from wechatpy import WeChatClient
from werkzeug import urls
# TOKEN = os.getenv('WECHAT_TOKEN', '')
# EncodingAESKey = os.getenv('WECHAT_ENCODING_AES_KEY', '')
# CorpId = os.getenv('WECHAT_CORP_ID', 'wx08e6d7d5ad7979fa')
# Secert = os.getenv('WECHAT_SECERT', 'DTPjxjy22aAj7l9CpNEtYIyz7nkUUEzAmAffEus')
AgentId = 0

if hasattr(sys, 'frozen'):
    # When running on compiled windows binary, we don't have access to package loader.
    path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'html'))
    loader = jinja2.FileSystemLoader(path)
else:
    loader = jinja2.PackageLoader('openerp.addons.hatchtec', "static")

env = jinja2.Environment('<%', '%>', '${', '}', '%', loader=loader, autoescape=True)


class WeixinLogin(Home):
    @http.route()
    def web_login(self, *args, **kw):
        ensure_db()
        db = RegistryManager.get(request.db)
        session = openerp.registry(request.db)['weixin.session']
        if request.httprequest.method == 'GET' and request.session.uid and request.params.get('redirect'):
            # Redirect if already logged in and redirect param is present
            return http.redirect_with_hash(request.params.get('redirect'))
        # 取得session md5
        session_md5 = hashlib.md5()
        session_md5.update(request.session_id)
        request.params.setdefault('session_md5', session_md5.hexdigest())
        temp_password = "%06d" % (abs(hash(session_md5.hexdigest())) % (10 ** 6))
        request.params.setdefault('temp_password', temp_password)
        with closing(db.cursor()) as cr:
            session.create(cr, 1, {'session_id': request.session_id, 'temp_password': "D%s" % temp_password})
            cr.commit()
        response = super(WeixinLogin, self).web_login(*args, **kw)
        return response


class HatchtecController(http.Controller):
    login_user = False

    @http.route('/wechat/codes', auth='public')
    def wechat_codes(self, email):
        db = RegistryManager.get(request.db)
        user = openerp.registry(request.db)['res.users']

        with closing(db.cursor()) as cr:
            users = user.search(cr, 1, [('login', '=', email)])
            if not users:
                return request.make_response(simplejson.dumps({
                    'wrong': True,
                    'text': u'错误, 账户不存在',
                }))

            user_browse = user.browse(cr, 1, users[0])

            if not user_browse.weixin_id:
                return request.make_response(simplejson.dumps({
                    'wrong': True,
                    'text': u'错误，当前账户未在微信端绑定',
                }))

            random_codes = str(random.randint(100000, 999999))
            codes_time = datetime.strptime(fields.datetime.now(cr, 1), '%Y-%m-%d %H:%M:%S') + timedelta(minutes=3)
            user_browse.write({
                'random_codes': random_codes,
                'codes_time': codes_time.strftime('%Y-%m-%d %H:%M:%S'),
            })

            cr.commit()

            response = self._send_text(user_browse.weixin_id, random_codes)
            if response:
                return request.make_response(simplejson.dumps({
                    'wrong': True,
                    'text': '微信端发送消息错误，错误码：%s，请联系管理员' % response,
                }))

            return request.make_response(simplejson.dumps({
                'wrong': False,
            }))

    def _send_text(self, weixin_id, codes):
        url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=%s' % self._get_access_token()
        body = '''{
            "touser": "%s",
            "msgtype": "text",
            "agentid": %s,
            "text": {
                "content": "%s",
            }
        }''' % (weixin_id, AgentId, codes)
        response = requests.post(url, body)
        content = simplejson.loads(response.content)

        if content.get('errcode') > 0:
            return content.get('errcode')

        return ''

    @http.route('/binding', auth='public')
    def binding(self, code, **args):
        user_id, mobile = self._get_user_mobile_by_code(code)
        db = RegistryManager.get(request.db)
        user = openerp.registry(request.db)['res.users']

        with closing(db.cursor()) as cr:
            users = user.search(cr, 1, [('oauth_access_token', '=', mobile)])
            binding = False
            kw = {
                'binding': users and True or False,
                'mobile': mobile,
                'user_id': user_id,
            }

            template = env.get_template('binding.html')
            return template.render(kw)

    @http.route('/weixin_login_qrcode', auth='public')
    def weixin_login_qrcode(self, type, width=300, height=300, **args):
        width, height = int(width), int(height)
        barcode = createBarcodeDrawing(
            type, value=request.session_id, format='png', width=width, height=height
        )
        barcode = barcode.asString('png')
        return request.make_response(barcode, headers=[('Content-Type', 'image/png')])

    @http.route('/wechat/pulling', auth='public')
    def wechat_pulling(self, **args):
        db = RegistryManager.get(request.db)
        user = openerp.registry(request.db)['res.users']

        if self.login_user and request.session_id == self.login_session:
            with closing(db.cursor()) as cr:
                users = user.browse(cr, 1, self.login_user)

                self.login_user = False
                self.login_session = False
                uid = request.session.authenticate(request.session.db, users.login, users.oauth_access_token)
                if uid:
                    return u'ok'

        return 'error'

    @http.route('/wechat/binding', auth='public')
    def wechat_binding(self, user_id, mobile, login, password, **args):
        db = RegistryManager.get(request.db)
        user = openerp.registry(request.db)['res.users']

        with closing(db.cursor()) as cr:
            users = user.search(cr, 1, [('login', '=', login)])
            if not users:
                return request.make_response(simplejson.dumps({
                    'message': u'账户不存在',
                    'state': 'error',
                }))

            try:
                user.check_credentials(cr, users[0], password)
            except:
                return request.make_response(simplejson.dumps({
                    'message': u'密码错误',
                    'state': 'error',
                }))

            user.write(cr, 1, users[0], {
                'oauth_access_token': mobile,
                'weixin_id': user_id,
            })
            cr.commit()

        return request.make_response(simplejson.dumps({
            'state': 'done',
            'message': u'绑定成功，请使用手机微信扫码登录'
        }))

    @http.route('/wechat/unbinding', auth='public')
    def wechat_unbinding(self, mobile):
        db = RegistryManager.get(request.db)
        user = openerp.registry(request.db)['res.users']

        with closing(db.cursor()) as cr:
            users = user.search(cr, 1, [('oauth_access_token', '=', mobile)])
            user.write(cr, 1, users[0], {'oauth_access_token': False})

            cr.commit()

        return request.make_response(simplejson.dumps({
            'state': 'done',
            'message': u'解除绑定成功'
        }))

    def _get_access_token(self):
        access_token_url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken'
        access_token_params = {
            'corpid': CorpId,
            'corpsecret': Secert
        }

        response = requests.get(access_token_url, params=access_token_params)
        access_token = simplejson.loads(response.content)

        return access_token.get('access_token')

    def _get_user_id(self, code, access_token=None):
        get_user_url = 'https://qyapi.weixin.qq.com/cgi-bin/user/getuserinfo'
        get_user_params = {
            'access_token': access_token or self._get_access_token(),
            'code': code,
        }

        response = requests.get(get_user_url, params=get_user_params)
        return simplejson.loads(response.content).get('UserId', '')

    def _get_user_mobile_by_code(self, code):
        access_token = self._get_access_token()
        user_id = self._get_user_id(code, access_token)
        return user_id, self._get_user_mobile(user_id, access_token)

    def _get_user_mobile(self, user_id, access_token=None):
        get_user_url = 'https://qyapi.weixin.qq.com/cgi-bin/user/get'
        get_user_params = {
            'access_token': access_token or self._get_access_token(),
            'userid': user_id,
        }

        response = requests.get(get_user_url, params=get_user_params)
        return simplejson.loads(response.content).get('mobile', '')

    def _login(self, msg):
        db = RegistryManager.get(request.db)
        user = openerp.registry(request.db)['res.users']

        mobile = self._get_user_mobile(msg.source)
        if not mobile:
            return u'错误，用户手机号不存在'

        with closing(db.cursor()) as cr:
            users = user.search(cr, 1, [('oauth_access_token', '=', mobile)])
            if not users:
                return u'错误，当前用户还没有在ERP端绑定'

            users = user.browse(cr, 1, users[0])
            uid = request.session.authenticate(request.session.db, users.login, users.oauth_access_token)
            if uid:
                self.login_user = uid
                self.login_session = msg.scan_result
                return u'成功'

        return u'错误，自动登录失败'

    def atuo_log_in(self, msg):
        db = RegistryManager.get(request.db)
        user = openerp.registry(request.db)['res.users']
        session = openerp.registry(request.db)['weixin.session']
        mobile = self._get_user_mobile(msg.source)
        if not mobile:
            return u'错误，用户手机号不存在'
        with closing(db.cursor()) as cr:
            users = user.search(cr, 1, [('oauth_access_token', '=', mobile)])
            if not users:
                return u'错误，当前用户还没有在ERP端绑定'
            users = user.browse(cr, 1, users[0])
            uid = request.session.authenticate(request.session.db, users.login, users.oauth_access_token)
            if uid:
                self.login_user = uid
                session_id = session.search(cr, 1, [('temp_password', '=', msg.content)])
                session_old_id = session.search(cr, 1, [('mobile', '=', mobile)])
                if session_old_id:
                    session.unlink(cr, uid, session_old_id)
                    cr.commit()
                if session_id:
                    session.write(cr, 1, session_id, {'mobile': mobile})
                    session_row = session.browse(cr, 1, session_id)
                    cr.commit()
                    self.login_session = session_row.session_id
                return u'成功'
        return "登录成功！"

    @http.route('/wechat', type='http', auth='none')
    def wechat(self, **args):
        signature = args.get('msg_signature', '')
        timestamp = args.get('timestamp', '')
        nonce = args.get('nonce', '')
        crypto = WeChatCrypto(TOKEN, EncodingAESKey, CorpId)
        if request.httprequest.method == 'GET':
            echo_str = args.get('echostr', '')
            try:
                echo_str = crypto.check_signature(
                    signature,
                    timestamp,
                    nonce,
                    echo_str
                )
            except InvalidSignatureException:
                reply = u'抱歉，签名解析失败'

            return echo_str
        else:
            try:
                msg = crypto.decrypt_message(
                    request.httprequest.data,
                    signature,
                    timestamp,
                    nonce
                )
            except (InvalidSignatureException, InvalidCorpIdException):
                reply = u'抱歉，请求解析失败'
            msg = parse_message(msg)
            if msg.type == 'text':
                return_val = msg.content
                if re.match(r'^[D](\d){6}', msg.content, re.I):
                    return_val = self.atuo_log_in(msg)
                reply = create_reply(return_val, msg).render()
            elif msg.type == 'event' and msg.event == 'scancode_waitmsg' and msg.scan_type == 'qrcode':
                reply = create_reply(self._login(msg)).render()
            elif msg.type == 'event' and msg.event == 'view':
                reply = create_reply(u'成功').render()
            else:
                reply = create_reply(u'不可以支持当前类型', msg).render()

        return crypto.encrypt_message(reply, nonce, timestamp)