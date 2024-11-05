# raisecard.py

# encoding:utf-8
import requests
import os
import plugins
from io import BytesIO
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from common.log import logger
from plugins import *

@plugins.register(
    name="RaiseCard",
    desire_priority=100,
    hidden=False,
    desc="A simple plugin that raises a card with a given message",
    version="0.1",
    author="金永勋 微信：xun900207",
)
class RaiseCardPlugin(Plugin):
    def __init__(self):
        super().__init__()
        try:
            self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
            logger.info("[RaiseCardPlugin] inited.")
        except Exception as e:
            logger.warn("[RaiseCardPlugin] init failed, ignore.")
            raise e

    def on_handle_context(self, e_context: EventContext):
        if e_context["context"].type != ContextType.TEXT:
            return

        content = e_context["context"].content.strip()
        
        if content.startswith("举牌"):
            message = content.replace("举牌", "").strip()
            image_url = self.get_card_image_url(message)
            if image_url:
                image_data = self.download_image(image_url)
                if image_data:
                    reply = Reply(ReplyType.IMAGE, image_data)
                    e_context["reply"] = reply
                    e_context.action = EventAction.BREAK_PASS
                else:
                    reply = Reply(ReplyType.TEXT, "无法保存卡片图片，请稍后再试。")
                    e_context["reply"] = reply
            else:
                reply = Reply(ReplyType.TEXT, "无法生成卡片图片，请稍后再试。")
                e_context["reply"] = reply

    def get_help_text(self, **kwargs):
        help_text = "输入【举牌 [消息]】 来生成带有指定消息的卡片图片。"
        return help_text

    def get_card_image_url(self, message):
        api_url = "https://api.suyanw.cn/api/zt.php"
        try:
            response = requests.get(api_url, params={"msg": message})
            response.raise_for_status()
            
            # 检查响应内容类型是否为图片
            content_type = response.headers.get('Content-Type')
            if 'image' in content_type:
                logger.debug("Image content detected")
                return response.url  # 直接使用请求的URL
            
            data = response.json()
            return data.get("image")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return None
        except ValueError:
            logger.error("Failed to parse JSON response")
            return None

    def download_image(self, image_url):
        try:
            response = requests.get(image_url)
            response.raise_for_status()
            image_data = BytesIO(response.content)
            logger.info("Image downloaded successfully")
            return image_data
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to download image: {e}")
            return None

# 示例调用
if __name__ == "__main__":
    plugin = RaiseCardPlugin()
    print(plugin.get_card_image_url("上班996别墅靠大海"))
