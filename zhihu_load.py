import json
import base64
from urllib import request
import re
import time
import hmac
import http.cookiejar
import requests


class Load(object):
    def __init__(self):
        self.url_1 = 'https://www.zhihu.com'

        # 声明一个CookieJar对象实例来保存cookie
        cookie = http.cookiejar.MozillaCookieJar()

        # 如果储存的cookie不存在(相同目录下)，则新建一个
        try:
            cookie.load('cookie.txt', ignore_discard=True, ignore_expires=True)
        except BaseException as f:
            print(f, '由于cookie不存在，所以在根目录新建了一个cookie.txt用于储存cookie')
            cookie.save('cookie.txt', ignore_discard=True, ignore_expires=True)

        # 利用urllib库的HTTPCookieProcessor对象来创建cookie处理器
        handler = request.HTTPCookieProcessor(cookie)
        # 通过handler来构建可以通过cookie登陆的opener
        self.opener = request.build_opener(handler)

    def load_by_cookie(self):
        # 尝试用已保存的cookie登陆，并返回是否登陆成功
        authorization = ''
        try:
            with open('authorization.txt', 'r') as f:
                authorization = f.read()  # 加载从文件中加载authorization
        except BaseException as f:
            print(f, 'authorization.txt不存在，自动跳过')

        req = request.Request(self.url_1)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0')
        req.add_header('authorization', 'oauth %s' % authorization)
        with self.opener.open(req) as f:
            temp = f.read().decode('utf-8')
            if '首页 - 知乎' not in temp:
                return False
            else:
                return True

    def load_url_by_cookie(self, url):
        # 尝试用已保存的cookie登陆
        with open('authorization.txt', 'r') as f:
            authorization = f.read()  # 加载从文件中加载authorization

        req = request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0')
        req.add_header('authorization', 'oauth %s' % authorization)
        with self.opener.open(req) as f:
            temp = f.read().decode('utf-8')
            if '首页 - 知乎' not in temp:
                print('登陆失败了，可能是cookie过期了')
            else:
                print(temp)


class MainLoad(object):
    def __init__(self):
        # 需要加载的网页地址
        self.url_1 = 'https://www.zhihu.com'
        self.url_2 = 'https://www.zhihu.com/signup?next=%2F'
        self.url_3 = 'https://static.zhihu.com/heifetz/main.app.bf03befe405b0d46c776.js'
        self.url_4 = 'https://www.zhihu.com/api/v3/oauth/captcha?lang=en'
        self.url_5 = 'https://www.zhihu.com/api/v3/oauth/sign_in'

        # 经过web分析，发现以下几个参数是登陆知乎必备的
        self.aliyungf_tc = ''
        self.__DAYU_PP = ''
        self.q_c1 = ''
        self._xsrf = ''
        self.d_c0 = ''
        self.authorization = ''
        self.capsion_ticket = ''
        self.z_c0 = ''

    # 用来生成cookie
    def make_cookie(self, name, value):
        return http.cookiejar.Cookie(version=0, name=name, value=value, port=None, port_specified=False,
                                     domain='', domain_specified=True, domain_initial_dot=False, path="/",
                                     path_specified=True, secure=False, expires=None, discard=False,
                                     comment=None, comment_url=None, rest=None)

    # 用于保存当前cookie到根目录
    def save_cookie(self):
        cookie_1 = http.cookiejar.MozillaCookieJar()
        cookie_1.set_cookie(self.make_cookie('aliyungf_tc', self.aliyungf_tc))
        cookie_1.set_cookie(self.make_cookie('_xsrf', self._xsrf))
        cookie_1.set_cookie(self.make_cookie('q_c1', self.q_c1))
        cookie_1.set_cookie(self.make_cookie('d_c0', self.d_c0))
        cookie_1.set_cookie(self.make_cookie('capsion_ticket', self.capsion_ticket))
        cookie_1.set_cookie(self.make_cookie('z_c0', self.z_c0))
        cookie_1.set_cookie(self.make_cookie('__DAYU_PP', self.__DAYU_PP))
        cookie_1.save('cookie.txt')

    # 主要登陆函数, 需传入账号密码, 登陆成功后才会退出, 并保存cookie
    def main_load(self, username, password):
        # 获取参数aliyungf_tc, _xsrf, q_c1, __DAYU_PP
        with request.urlopen(self.url_1) as f:
            temp_1 = str(f.headers)
            try:
                self.aliyungf_tc = re.findall(r'aliyungf_tc=(.*?);', temp_1)[0]
            except BaseException as f:
                self.__DAYU_PP = re.findall(r'__DAYU_PP=(.*?);', temp_1)[0]
                print(f, 'aliyungf_tc不存在，因此用__DAYU_PP')
            self._xsrf = re.findall(r'_xsrf=(.*?);', temp_1)[0]
            self.q_c1 = re.findall(r'q_c1=(.*?);', temp_1)[0]

        # 定义一个获取d_c0的函数，因为有时候返回的头文件不含d_c0，所以得反复获取
        def get_d_c0():
            req_2 = request.Request(self.url_2)
            req_2.add_header('User-Agent',
                             'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0')
            req_2.add_header('Cookie', 'aliyungf_tc=%s; _xsrf=%s; q_c1=%s; __DAYU_PP=%s' % (self.aliyungf_tc, self._xsrf, self.q_c1, self.__DAYU_PP))
            with request.urlopen(req_2) as f_1:
                temp_2 = str(f_1.headers)
                d_c0_ = re.findall(r'd_c0=(.*?);', temp_2)[0]
            return d_c0_

        flag_2 = 0
        while flag_2 == 0:
            try:
                self.d_c0 = get_d_c0()
                flag_2 = 1
            except BaseException as e:
                print(e)
                time.sleep(1)

        # 获取参数authorization, 并保存至文件
        with request.urlopen(self.url_3) as f:
            html = str(f.read())
            self.authorization = re.findall(r'"\),m="(.*?)",y="', html)[0]

        with open('authorization.txt', 'w') as f:
            f.write(self.authorization)  # 将authorization保存至文件

        flag_1 = 0  # 判断是否登陆成功, 当不成功时, 不断重复登陆

        while flag_1 != 201 and flag_1 != 200:
            # 获取参数capsion_ticket
            req_4 = request.Request(self.url_4)
            req_4.add_header('User-Agent',
                             'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0')
            req_4.add_header('Cookie', 'aliyungf_tc=%s; _xsrf=%s; q_c1=%s; d_c0=%s; __DAYU_PP=%s' % (self.aliyungf_tc, self._xsrf, self.q_c1, self.d_c0, self.__DAYU_PP))
            req_4.add_header('authorization', 'oauth %s' % self.authorization)
            with request.urlopen(req_4) as f:
                temp_4 = str(f.headers)
                self.capsion_ticket = re.findall(r'capsion_ticket=(.*?=/)', temp_4)[0]

            # 尝试获取验证码图片，并保存至根目录
            req_5 = request.Request(self.url_4)
            req_5.add_header('User-Agent',
                             'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0')
            req_5.add_header('Cookie', 'aliyungf_tc=%s; _xsrf=%s; q_c1=%s; d_c0=%s; capsion_ticket=%s; __DAYU_PP=%s' % (
                self.aliyungf_tc, self._xsrf, self.q_c1, self.d_c0, self.capsion_ticket, self.__DAYU_PP))
            req_5.add_header('authorization', 'oauth %s' % self.authorization)
            req_5.get_method = lambda: "PUT"
            with request.urlopen(req_5) as f:
                a = bytes(json.load(f)['img_base64'], encoding='utf-8')
            with open('验证码.jpg', 'wb') as f:
                f.write(base64.b64decode(a))

            captcha = input('请输入验证码(根目录中，验证码.jpg)：')

            # 计算加密参数signature
            client_id = self.authorization
            grant_type = 'password'
            timestamp = str(int(time.time() * 1000))
            source = 'com.zhihu.web'

            h = hmac.new(b'd1b964811afb40118a12068ff74a12f4', digestmod='sha1')
            h.update(bytes(grant_type, encoding='utf-8'))
            h.update(bytes(client_id, encoding='utf-8'))
            h.update(bytes(source, encoding='utf-8'))
            h.update(bytes(timestamp, encoding='utf-8'))
            signature = h.hexdigest()

            # 构造multipart/form-data格式表单
            data = '------WebKitFormBoundary07275RIUwbGzEyIZ\r\nContent' \
                   '-Disposition: form-data; name="client_id"\r\n\r\n%s\r\n---' \
                   '---WebKitFormBoundary07275RIUwbGzEyIZ\r\nContent-Dispositio' \
                   'n: form-data; name="grant_type"\r\n\r\npassword\r\n------WebKit' \
                   'FormBoundary07275RIUwbGzEyIZ\r\nContent-Disposition: form-data; n' \
                   'ame="timestamp"\r\n\r\n%s\r\n------WebKitFormBoundary07275RIUwbGzEy' \
                   'IZ\r\nContent-Disposition: form-data; name="source"\r\n\r\ncom.zhi' \
                   'hu.web\r\n------WebKitFormBoundary07275RIUwbGzEyIZ\r\nContent-Dispos' \
                   'ition: form-data; name="signature"\r\n\r\n%s\r\n------WebKitFormBounda' \
                   'ry07275RIUwbGzEyIZ\r\nContent-Disposition: form-data; ' \
                   'name="username"\r\n\r\n+86%s\r\n------WebKitFormBoundary07275RIUwb' \
                   'GzEyIZ\r\nContent-Disposition: form-data; name="password"\r\n\r\n%s\r\n------W' \
                   'ebKitFormBoundary07275RIUwbGzEyIZ\r\nContent-Disposition: form-d' \
                   'ata; name="captcha"\r\n\r\n%s\r\n------WebKitFormBoundary07275RIUwbGzEyIZ\r\nContent-Dispositio' \
                   'n: form-data; name="lang"\r\n\r\nen\r\n------WebKitFormBoundary07275RIUwbGzEyIZ\r\nContent-Disposi' \
                   'tion: form-data; name="ref_source"\r\n\r\nhomepage\r\n------WebKitFormBoundary07275RIUwbGzEyIZ\r\nCont' \
                   'ent-Disposition: form-data; name="utm_source"\r\n\r\n\r\n------WebKitFormBoundary07275RIUwbGzEyIZ--' % (
                       client_id, timestamp, signature, username, password, captcha)

            # 用post方式登陆，multipart/form-data格式表单, 参数z_c0为验证登陆的必备参数
            req_6 = self.url_5
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0',
                       'Cookie': 'aliyungf_tc=%s; _xsrf=%s; q_c1=%s; d_c0=%s; capsion_ticket=%s; __DAYU_PP=%s' % (
                           self.aliyungf_tc, self._xsrf, self.q_c1, self.d_c0, self.capsion_ticket, self.__DAYU_PP),
                       'authorization': 'oauth %s' % self.authorization,
                       'Content-Type': 'multipart/form-data; boundary=----WebKitFormBoundary07275RIUwbGzEyIZ',
                       'Referer': 'https://www.zhihu.com/signup?next=%2F'}
            with requests.post(req_6, data=data, headers=headers) as f:
                temp_6 = str(f.headers)
                f.encoding = 'utf-8'
                try:
                    self.z_c0 = re.findall(r'z_c0=(.*?=/)', temp_6)[0]
                    flag_1 = f.status_code
                except:
                    flag_1 = f.status_code
                    if flag_1 != 201 and flag_1 != 200:
                        print(f.text)

        # 保存cookie
        self.save_cookie()


if __name__ == '__main__':
    url = 'https://www.zhihu.com'
    myLoad = Load()
    myMainLoad = MainLoad()
    if myLoad.load_by_cookie():
        myLoad.load_url_by_cookie(url)
    else:
        username_0 = input('请输入用户名：')
        password_0 = input('请输入密码：')
        myMainLoad.main_load(username_0, password_0)
        myLoad.load_url_by_cookie(url)
