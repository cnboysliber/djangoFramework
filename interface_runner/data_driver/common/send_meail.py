import smtplib
import os
from email.mime.text import MIMEText
from email.header import Header
from email.mime.multipart import MIMEMultipart
from loguru import logger


class SendEmail():

    def __init__(self, mailHost, mailUser, mailPassword):
        '''
        初始化
        :param mailHost: 邮箱host
        :param mailUser: 邮箱用户名
        :param mailPass: 邮箱密码
        '''
        self.mailHost = mailHost
        self.mailUser = mailUser
        self.mailPass = mailPassword

    def send_text_email(self, sender, receivers, subject=None, msg=None, port=465):
        '''
        发送纯文本邮件,支持多用户发送,sender为list
        :param sender: 发送者，多个为list
        :param receivers: 接收者，可以是多个
        :param subject: 主题
        :param msg: 文本信息
        :param port: 端口
        :return: None
        '''
        message = MIMEText(msg, "plain", "utf-8")
        message["From"] = Header(sender, "utf-8")
        strReceivers = ""
        for i in range(len(receivers)):  # 此循环是兼容多个收件人地址均显示在邮件中
            strReceivers = strReceivers + receivers[i] + ","
        message["To"] = strReceivers
        message["Subject"] = Header(subject, "utf-8")
        try:
            smtpobj = smtplib.SMTP_SSL()
            smtpobj.connect(self.mailHost, port=465)
            smtpobj.login(self.mailUser, self.mailPass)
            smtpobj.sendmail(sender, receivers, message.as_string())
            logger.info("邮件发送成功")
            smtpobj.quit()
        except smtplib.SMTPException as error:
            logger.error("error:发送邮件失败:%s" % error)

    def send_html_email(self, sender, receivers, subject=None, msg=None, port=465):
        '''
        发送HTML类邮件，支持批量用户发送，sender为list
        :param sender: 发送者，多个为list
        :param receivers: 接收者，可以是多个
        :param subject: 主题
        :param msg: 文本信息
        :param port: 端口
        :return: None
        '''
        message = MIMEText(msg, "html", "utf-8")
        message["From"] = Header(sender, "utf-8")
        strReceivers = ""
        for i in range(len(receivers)):  # 此循环是兼容多个收件人地址均显示在邮件中
            strReceivers = strReceivers + receivers[i] + ","
        message["To"] = strReceivers
        message["Subject"] = Header(subject, "utf-8")
        try:
            smtpobj = smtplib.SMTP_SSL(self.mailHost, port)
            smtpobj.login(self.mailUser, self.mailPass)
            smtpobj.sendmail(sender, receivers, message.as_string())
            logger.info("邮件发送成功")
            smtpobj.quit()
        except smtplib.SMTPException as error:
            logger.error("error:发送邮件失败:%s" % error)

    def send_attach_email(self, sender, receivers, filePaths, subject=None, msg=None, port=465):
        '''
        发送附件类邮件，支持批量发送附件、用户，sender、filePaths为list
        :param sender: 发送者，多个为list
        :param receivers: 接收者，可以是多个
        :param filePaths: 需要发送的文件地址
        :param subject: 主题
        :param msg: 信息
        :param port: 端口
        :return:
        '''
        message = MIMEMultipart()
        message.attach(MIMEText(msg, "plain", "utf-8"))
        message["From"] = Header(sender, "utf-8")
        strReceivers = ""
        for i in range(len(receivers)):  # 批量发送邮件，接收者全部显示在收件人处
            strReceivers = strReceivers + receivers[i] + ","
        message["To"] = strReceivers
        message["Subject"] = Header(subject, "utf-8")
        for filePath in filePaths:  # 支持多附件发送
            att = MIMEText(open(filePath, "rb").read(), "base64", "utf-8")
            att["Content-Type"] = 'application/octet-stream'
            filename = os.path.split(filePath)
            att["Content-Disposition"] = 'attachment; filename=%s' % filename[1]
            message.attach(att)
        try:
            smtpobj = smtplib.SMTP_SSL(self.mailHost, port)
            smtpobj.login(self.mailUser, self.mailPass)
            smtpobj.sendmail(sender, receivers, message.as_string())
            logger.info("邮件发送成功")
        except smtplib.SMTPException as error:
            logger.error("error:发送邮件失败：%s" % error)
        smtpobj.quit()
