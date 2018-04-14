#! /usr/bin/env python
# -*- coding: utf-8 -*-

import smtplib
import json

from email import encoders
from email.header import Header
from email.mime.multipart import MIMEBase, MIMEMultipart
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr


class SendEmail(object):

    # 登录账户和口令 目标服务器网站
    # from_addr = '1003594835@qq.com'
    # password = '**********'
    # smtp_server = 'smtp.qq.com'

    # 126账号和口令
    from_addr = '13849182150@163.com'
    password = 'lanfang123'
    smtp_server = 'smtp.163.com'

    server = None

    def __init__(self, from_name):
        self.from_name = from_name

    def _format_addr(self, addrs):
        """
        格式化邮件地址
        :param addrs: type [(name,addr),(name,addr)]
        :return:
        """
        format_addrs = []
        for addr_str in addrs:
            addr_str = '%s<%s>'%(addr_str[0],addr_str[1])
            # parseaddr：解析字符串中的email地址
            name, addr = parseaddr(addr_str)
            # name中包含中文，需要通过Header对象进行编码
            # formataddr:parseaddr函数的逆函数
            format_addrs.append(formataddr((Header(name, 'utf-8').encode(), addr)))
        return format_addrs

    def send_email_base(self, to_users, msg_obj, subject_test):
        """
        发送邮件
        :param to_users: [(name,addr),(name,addr)]
        :param msg_obj: 发送msg的对象
        :param subject_test: 发送的主题
        :return: 发送成功 ：{},
                 发送失败：{addr:(code,info),...},except_info:str
        """
        msg_obj['From'] = ','.join(self._format_addr([(self.from_name,self.from_addr)]))
        msg_obj['To'] = ','.join(self._format_addr(to_users))
        msg_obj['Subject'] = Header(subject_test, 'utf-8').encode()
        to_addrs = [item[1] for item in to_users]
        try:
            server = smtplib.SMTP_SSL(self.smtp_server, 465)
            server.login(self.from_addr, self.password)
            # 发件账户，收件账户，内容
            result = server.sendmail(self.from_addr, to_addrs, msg_obj.as_string())
            #print(result)
            return result
        except smtplib.SMTPRecipientsRefused as e:
            print(e)
            return json.loads(json.dumps(str(e)))
        except smtplib.SMTPException as e:
            print('Send Fail,%s' % e)
            return str(e)
        finally:
            server.quit()

    def send_email_text(self, to_addrs, msg, subject_test='来自SMTP的问候'):
        """
        发送文本信息邮件
        :param to_addr: [(name,addr),(name,addr)]
        :param msg:发送的信息
        :param subject_test:发送主题
        :return: True/False
        """
        # msg对象
        msg = MIMEText(msg, 'plain', 'utf-8')
        return self.send_email_base(to_addrs, msg, subject_test)

    def send_email_html(self, to_addrs, msg, subject_test='来自SMTP的问候'):
        """
        发送文本信息邮件
        :param to_addr: [(name,addr),(name,addr)]
        :param msg:发送的信息
        :param subject_test:发送主题
        :return: True/False
        """
        # HTML邮件
        msg = MIMEText(msg, 'html', 'utf-8')
        return self.send_email_base(to_addrs, msg, subject_test)

    def send_email_image(self, to_addrs, msg_text, file_path, subject_test='来自SMTP的问候'):
        # 邮件对象
        msg = MIMEMultipart('alternative')
        # 邮件正文是MIMEText:
        msg.attach(MIMEText(msg_text, 'plain', 'utf-8'))

        msg.attach(MIMEText('<html><body><h1>%s</h1>'%msg_text +
                            '<p><img src="cid:0"></p>' +
                            '</body></html>', 'html', 'utf-8'))
        with open(file_path, 'rb') as f:
            # 设置附件和MIME，从本地读取一个图片
            mime = MIMEBase('image', 'jpeg', filename=file_path.split('/')[-1])
            # 加上必要的头信息：
            mime.add_header('Content-Disposition', 'attachment', filename=file_path.split('/')[-1])
            mime.add_header('Content-ID', '<0>')
            mime.add_header('X-Attachment-Id', '0')
            # 把附件的内容读进来：
            mime.set_payload(f.read())
            # 用Base64编码：
            encoders.encode_base64(mime)
            # 添加到MIMEMultipart:
            msg.attach(mime)
        return self.send_email_base(to_addrs, msg, subject_test)

    def send_email_file(self, to_addrs, msg_text, file_path, subject_test='来自SMTP的问候'):
        # 邮件对象
        msg = MIMEMultipart('alternative')
        # 邮件正文是MIMEText:
        msg.attach(MIMEText(msg_text, 'plain', 'utf-8'))

        with open(file_path, 'rb') as f:
            # 设置附件和MIME，从本地读取一个图片
            mime = MIMEBase('image', 'jpeg', filename=file_path.split('/')[-1])
            # 加上必要的头信息：
            mime.add_header('Content-Disposition', 'attachment', filename=file_path.split('/')[-1])
            mime.add_header('Content-ID', '<0>')
            mime.add_header('X-Attachment-Id', '0')
            # 把附件的内容读进来：
            mime.set_payload(f.read())
            # 用Base64编码：
            encoders.encode_base64(mime)
            # 添加到MIMEMultipart:
            msg.attach(mime)
        return self.send_email_base(to_addrs, msg, subject_test)




if __name__ == '__main__':
    html_str = '<html><body><h1>Hello</h1><p>send by ' \
               '<a href="http://www.python.org">Python</a>' \
               '...</p></body></html>'
    to_addrs = [('lanfang','13849182150@163.com'), ('lanfang','138491821@163.com')]
    send_obj = SendEmail(from_name='python')
    send_obj.send_email_text(to_addrs,'hello~~~~')
    # send_obj.send_email_image(to_addrs,'hello~~~~','/Users/mrs/Documents/test.jpg')
    # send_obj.send_email_html(to_addrs,html_str)
    # send_obj.send_email_file(to_addrs, 'hi','/Users/mrs/Documents/test.jpg')
