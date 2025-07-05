import requests
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from collections import deque
import logging
from colorlog import ColoredFormatter

# 配置日志输出的颜色
LOG_FORMAT = "%(log_color)s%(asctime)s - %(message)s"
formatter = ColoredFormatter(
    LOG_FORMAT,
    datefmt="%Y-%m-%d %H:%M:%S",
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    }
)

# 配置日志
logger = logging.getLogger()
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)

# 配置API地址
API_URL = "https://sscz.gdedu.gov.cn/qtrack/answer-api/generateValidateCode?_t={}"


# 企业微信Webhook链接
WECHAT_WEBHOOK_URL = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=026568f1-239d-490a-9f87-1d7f6620e94e"


# 配置邮件
SENDER_EMAIL = '281534481@qq.com'  # 你的 QQ 邮箱
SENDER_PASSWORD = ''  # 你的 QQ 邮箱授权码
# RECEIVER_EMAIL = '281534481@qq.com'  # 接收邮件的邮箱
RECEIVER_EMAILS = ['281534481@qq.com']  # 多个收件人

# 配置邮件发送间隔
EMAIL_SEND_INTERVAL = 3 * 60 # 默认3分钟，你可以自由调整

# 存储最近100次调用记录
history = deque(maxlen=100)

# 配置异常时间间隔（可以随时修改）
EXCEPTION_INTERVAL = 3  # 默认5秒，你可以自由调整

# 发送邮件函数
def send_email(subject, body):
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['Subject'] = subject

    # 设置邮件正文
    msg.attach(MIMEText(body, 'plain'))

    # 如果你要使用 Bcc 发送邮件，注释掉下面这行并取消下面的 Bcc 设置
    msg['To'] = ', '.join(RECEIVER_EMAILS)  # 直接发送给多个收件人

    try:
        # 使用 QQ 邮箱的 SMTP 服务器
        with smtplib.SMTP_SSL('smtp.qq.com', 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAILS, msg.as_string())
            server.quit() # 发送邮件后退出连接
        logger.info("🚨 预警邮件已发送 🚨")
    except Exception as e:
        logger.error(f"❌ 邮件发送失败: {e}")

# 发送企业微信消息函数
def send_wechat_message(content):
    # 测试消息不需要@所有人
    is_test_message = content.startswith("这是一个测试消息")

    # 构建消息内容
    message_content = content if is_test_message else "@所有人\n\n" + content + "\n\n请及时处理！"

    data = {
        "msgtype": "text",
        "text": {
            "content": message_content,
        }
    }

    try:
        response = requests.post(WECHAT_WEBHOOK_URL, json=data)
        if response.status_code == 200:
            logger.info("🚨 企业微信预警消息已发送 🚨")
        else:
            logger.error(f"❌ 企业微信消息发送失败: {response.text}")
    except Exception as e:
        logger.error(f"❌ 企业微信消息发送异常: {e}")

    # 如果是测试消息，记录测试成功日志
    if is_test_message:
        logger.info("✅ 测试消息发送成功")




# 调用API并记录状态
def monitor_api():
    while True:
        timestamp = int(time.time() * 1000)
        url = API_URL.format(timestamp)
        start_time = time.time()

        try:
            response = requests.get(url)
            response_time = time.time() - start_time
            status = response.status_code
            history.append({
                'time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time)),
                'status': status,
                'response_time': response_time
            })

            # 打印调用状态和消耗的时间
            if status == 200 and response_time <= EXCEPTION_INTERVAL:
                logger.info(f"✅ 调用成功 - 状态: {status}, 耗时: {response_time:.2f}s")
            else:
                logger.warning(f"⚠️ 调用成功，但响应时间过长 - 状态: {status}, 耗时: {response_time:.2f}s")

            # 检查异常情况
            if status != 200 or response_time > EXCEPTION_INTERVAL:
                # 检查是否需要发送预警邮件
                if len([h for h in history if h['status'] != 200 or h['response_time'] > EXCEPTION_INTERVAL]) >= 3:
                    body = "\n".join([f"调用时间: {h['time']}, 状态: {h['status']}, 耗时: {h['response_time']:.2f}s" for h in history])
                    # send_email("🚨 API 调用异常预警 🚨", body)
                    send_wechat_message(f"🚨 API 调用异常预警 🚨\n\n{body}")
                    # 等待10分钟再继续发送邮件
                    time.sleep(EMAIL_SEND_INTERVAL)

        except Exception as e:
            logger.error(f"❌ API 调用失败: {e}")
            history.append({
                'time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time)),
                'status': 'Failed',
                'response_time': time.time() - start_time
            })
            # 发生异常时发送邮件
            # send_email("⚠️ API 调用失败预警 ⚠️", f"调用时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}, 错误: {e}")

            send_wechat_message(f"⚠️ API 调用失败预警 ⚠️\n\n调用时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}, 错误: {e}")

        # 等待10秒钟
        time.sleep(5)

# 测试邮件发送功能
def test_send_email():
    subject = "教育测评项目api监控测试邮件"
    body = "这是一个测试邮件，确保邮件功能正常。"
    send_email(subject, body)

# 测试企业微信消息发送功能
def test_send_wechat_message():
    content = "这是一个测试消息，确保企业微信消息功能正常。"
    send_wechat_message(content)

if __name__ == '__main__':
    # 测试邮件发送，方便你验证邮件是否能发送成功
    # test_send_email()
    # 测试企业微信消息发送，方便你验证企业微信消息是否能发送成功
    # test_send_wechat_message()
    # 运行API监控
    monitor_api()
