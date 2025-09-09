# -*- coding: utf-8 -*-
import http.client
import urllib.parse
import json
import requests
import os
from datetime import datetime

class WxTrendPusher:
    def __init__(self, tianapi_key, wxpusher_app_token, target_uids=None):
        """
        初始化微信热搜推送器
        
        Args:
            tianapi_key (str): 天行API的密钥
            wxpusher_app_token (str): WxPusher的AppToken
            target_uids (list): 目标用户UID列表
        """
        self.tianapi_key = tianapi_key
        self.wxpusher_app_token = wxpusher_app_token
        self.target_uids = target_uids or []
        self.wxpusher_url = "https://wxpusher.zjiecode.com/api/send/message"
    
    def get_wx_hot_trends(self):
        """
        获取微信热搜数据
        
        Returns:
            dict: API返回的热搜数据，如果失败返回None
        """
        try:
            conn = http.client.HTTPSConnection('apis.tianapi.com')
            params = urllib.parse.urlencode({'key': self.tianapi_key})
            headers = {'Content-type': 'application/x-www-form-urlencoded'}
            
            conn.request('POST', '/wxhottopic/index', params, headers)
            response = conn.getresponse()
            result = response.read()
            data = result.decode('utf-8')
            
            conn.close()
            
            dict_data = json.loads(data)
            return dict_data
            
        except Exception as e:
            print(f"获取微信热搜失败: {e}")
            return None
    
    def format_trend_content(self, trend_data):
        """
        格式化热搜数据为推送内容
        
        Args:
            trend_data (dict): 天行API返回的热搜数据
            
        Returns:
            str: 格式化后的推送内容
        """
        if not trend_data or trend_data.get('code') != 200:
            return "❌ 获取微信热搜失败"
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        content = f"📱 **微信热搜榜** ({current_time})\n\n"
        
        news_list = trend_data.get('result', {}).get('list', [])
        
        if not news_list:
            return "📱 暂无热搜数据"
        
        for i, item in enumerate(news_list[:20], 1):  # 只取前20条
            title = item.get('word', '无标题')
            content += f"🔥 **{i}.** {title}\n\n"
        
        return content
    
    def send_to_wxpusher(self, content, content_type=3):
        """
        发送消息到WxPusher
        
        Args:
            content (str): 要发送的内容
            content_type (int): 内容类型，1=文字，2=html，3=markdown
            
        Returns:
            bool: 发送是否成功
        """
        if not self.target_uids:
            print("❌ 未设置目标用户UID")
            return False
        
        payload = {
            "appToken": self.wxpusher_app_token,
            "content": content,
            "summary": "微信热搜榜更新",
            "contentType": content_type,
            "uids": self.target_uids
        }
        
        try:
            headers = {
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                self.wxpusher_url, 
                data=json.dumps(payload), 
                headers=headers,
                timeout=30
            )
            
            result = response.json()
            
            if result.get('code') == 1000:
                print("✅ 推送成功")
                return True
            else:
                print(f"❌ 推送失败: {result.get('msg', '未知错误')}")
                return False
                
        except Exception as e:
            print(f"❌ 推送异常: {e}")
            return False
    
    def push_daily_trends(self):
        """
        执行每日热搜推送
        """
        print("🔄 开始获取微信热搜...")
        
        # 获取热搜数据
        trend_data = self.get_wx_hot_trends()
        
        if not trend_data:
            print("❌ 无法获取热搜数据")
            return False
        
        # 格式化内容
        content = self.format_trend_content(trend_data)
        print("📝 热搜内容格式化完成")
        
        # 推送到WxPusher
        print("📤 开始推送...")
        success = self.send_to_wxpusher(content)
        
        return success


def main():
    """
    主函数 - 配置和运行热搜推送
    """
    # 从环境变量获取配置
    TIANAPI_KEY = os.getenv('TIANAPI_KEY')
    WXPUSHER_APP_TOKEN = os.getenv('WXPUSHER_APP_TOKEN')
    TARGET_UIDS_STR = os.getenv('TARGET_UIDS')
    
    # 检查配置
    if not TIANAPI_KEY:
        print("❌ 请设置环境变量 TIANAPI_KEY")
        return
    
    if not WXPUSHER_APP_TOKEN:
        print("❌ 请设置环境变量 WXPUSHER_APP_TOKEN")
        return
    
    if not TARGET_UIDS_STR:
        print("❌ 请设置环境变量 TARGET_UIDS (用逗号分隔多个UID)")
        return
    
    # 解析目标用户UID列表
    TARGET_UIDS = [uid.strip() for uid in TARGET_UIDS_STR.split(',')]
    
    # 创建推送器实例
    pusher = WxTrendPusher(
        tianapi_key=TIANAPI_KEY,
        wxpusher_app_token=WXPUSHER_APP_TOKEN,
        target_uids=TARGET_UIDS
    )
    
    # 执行推送
    pusher.push_daily_trends()


if __name__ == "__main__":
    main()