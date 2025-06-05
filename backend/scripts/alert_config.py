"""
监控告警配置
支持邮件、钉钉、企业微信等告警方式
"""
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class AlertManager:
    def __init__(self):
        self.email_config = {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'username': 'your-email@gmail.com',
            'password': 'your-app-password',
            'recipients': ['admin@example.com']
        }
        
        self.dingtalk_webhook = 'https://oapi.dingtalk.com/robot/send?access_token=xxx'
    
    def send_email_alert(self, subject, message):
        """发送邮件告警"""
        msg = MIMEMultipart()
        msg['From'] = self.email_config['username']
        msg['To'] = ', '.join(self.email_config['recipients'])
        msg['Subject'] = f"[台账系统告警] {subject}"
        
        msg.attach(MIMEText(message, 'plain'))
        
        try:
            server = smtplib.SMTP(
                self.email_config['smtp_server'], 
                self.email_config['smtp_port']
            )
            server.starttls()
            server.login(
                self.email_config['username'], 
                self.email_config['password']
            )
            server.send_message(msg)
            server.quit()
            return True
        except Exception as e:
            print(f"发送邮件失败: {e}")
            return False
    
    def send_dingtalk_alert(self, title, message):
        """发送钉钉告警"""
        data = {
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": f"## {title}\n\n{message}"
            }
        }
        
        try:
            response = requests.post(
                self.dingtalk_webhook,
                json=data,
                headers={'Content-Type': 'application/json'}
            )
            return response.status_code == 200
        except Exception as e:
            print(f"发送钉钉消息失败: {e}")
            return False