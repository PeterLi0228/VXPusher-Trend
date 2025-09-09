# -*- coding: utf-8 -*-
import http.client
import urllib.parse
import json
import requests
import os
from datetime import datetime

class HotTrendPusher:
    def __init__(self, tianapi_key, wxpusher_app_token, target_uids=None):
        """
        初始化热搜推送器
        
        Args:
            tianapi_key (str): 天行API的密钥
            wxpusher_app_token (str): WxPusher的AppToken
            target_uids (list): 目标用户UID列表
        """
        self.tianapi_key = tianapi_key
        self.wxpusher_app_token = wxpusher_app_token
        self.target_uids = target_uids or []
        self.wxpusher_url = "https://wxpusher.zjiecode.com/api/send/message"
    
    def get_hot_trends(self, platform="weixin"):
        """
        获取热搜数据
        
        Args:
            platform (str): 平台类型 'weixin', 'weibo', 'douyin'
            
        Returns:
            dict: API返回的热搜数据，如果失败返回None
        """
        try:
            conn = http.client.HTTPSConnection('apis.tianapi.com')
            params = urllib.parse.urlencode({'key': self.tianapi_key})
            headers = {'Content-type': 'application/x-www-form-urlencoded'}
            
            # 根据平台选择接口
            endpoints = {
                'weixin': '/wxhottopic/index',
                'weibo': '/weibohot/index', 
                'douyin': '/douyinhot/index'
            }
            
            endpoint = endpoints.get(platform, '/wxhottopic/index')
            conn.request('POST', endpoint, params, headers)
            response = conn.getresponse()
            result = response.read()
            data = result.decode('utf-8')
            
            conn.close()
            
            dict_data = json.loads(data)
            return dict_data
            
        except Exception as e:
            print(f"获取{platform}热搜失败: {e}")
            return None
    
    def format_trend_content(self, trend_data, platform="weixin"):
        """
        格式化热搜数据为推送内容
        
        Args:
            trend_data (dict): 天行API返回的热搜数据
            platform (str): 平台类型 'weixin', 'weibo', 'douyin'
            
        Returns:
            str: 格式化后的推送内容
        """
        if not trend_data or trend_data.get('code') != 200:
            platform_names = {'weixin': '微信', 'weibo': '微博', 'douyin': '抖音'}
            platform_name = platform_names.get(platform, platform)
            return f"❌ 获取{platform_name}热搜失败"
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        platform_names = {'weixin': '微信', 'weibo': '微博', 'douyin': '抖音'}
        platform_icons = {'weixin': '📱', 'weibo': '🔥', 'douyin': '🎵'}
        platform_name = platform_names.get(platform, platform)
        platform_icon = platform_icons.get(platform, '📱')
        
        content = f"{platform_icon} **{platform_name}热搜榜** ({current_time})\n\n"
        
        news_list = trend_data.get('result', {}).get('list', [])
        
        if not news_list:
            return f"{platform_icon} 暂无{platform_name}热搜数据"
        
        for i, item in enumerate(news_list[:15], 1):  # 取前15条避免推送过长
            if platform == 'weixin':
                title = item.get('word', '无标题')
                content += f"🔥 **{i}.** {title}\n\n"
            elif platform == 'weibo':
                title = item.get('hotword', '无标题')
                hot_num = item.get('hotwordnum', '').strip()
                if hot_num:
                    content += f"🔥 **{i}.** {title}\n   热度: {hot_num}\n\n"
                else:
                    content += f"🔥 **{i}.** {title}\n\n"
            elif platform == 'douyin':
                title = item.get('word', '无标题')
                hot_index = item.get('hotindex', 0)
                content += f"🔥 **{i}.** {title}\n   热度: {hot_index:,}\n\n"
        
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
    
    def push_platform_trends(self, platform="weixin"):
        """
        推送指定平台的热搜
        """
        platform_names = {'weixin': '微信', 'weibo': '微博', 'douyin': '抖音'}
        platform_name = platform_names.get(platform, platform)
        
        print(f"🔄 开始获取{platform_name}热搜...")
        
        # 获取热搜数据
        trend_data = self.get_hot_trends(platform)
        
        if not trend_data:
            print(f"❌ 无法获取{platform_name}热搜数据")
            return False
        
        # 格式化内容
        content = self.format_trend_content(trend_data, platform)
        print(f"📝 {platform_name}热搜内容格式化完成")
        
        # 推送到WxPusher
        print("📤 开始推送...")
        success = self.send_to_wxpusher(content)
        
        return success
    
    def push_all_platforms_trends(self):
        """
        推送所有平台的热搜（合并推送）
        """
        platforms = ['weixin', 'weibo', 'douyin']
        all_content = []
        
        print("🔄 开始获取所有平台热搜...")
        
        for platform in platforms:
            platform_names = {'weixin': '微信', 'weibo': '微博', 'douyin': '抖音'}
            platform_name = platform_names.get(platform, platform)
            
            print(f"🔄 获取{platform_name}热搜...")
            trend_data = self.get_hot_trends(platform)
            
            if trend_data:
                content = self.format_trend_content(trend_data, platform)
                all_content.append(content)
                print(f"✅ {platform_name}热搜获取成功")
            else:
                print(f"❌ {platform_name}热搜获取失败")
        
        if not all_content:
            print("❌ 无法获取任何平台的热搜数据")
            return False
        
        # 合并所有平台内容，使用分隔符区分
        separator = "\n\n" + "="*50 + "\n\n"
        combined_content = separator.join(all_content)
        
        print("📝 所有平台热搜内容格式化完成")
        print("📤 开始推送...")
        
        success = self.send_to_wxpusher(combined_content)
        return success


def main():
    """
    主函数 - 配置和运行热搜推送
    """
    import sys
    
    # 从环境变量获取配置
    TIANAPI_KEY = os.getenv('TIANAPI_KEY')
    WXPUSHER_APP_TOKEN = os.getenv('WXPUSHER_APP_TOKEN')
    TARGET_UIDS_STR = os.getenv('TARGET_UIDS')
    PUSH_MODE = os.getenv('PUSH_MODE', 'all')  # all, weixin, weibo, douyin
    
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
    pusher = HotTrendPusher(
        tianapi_key=TIANAPI_KEY,
        wxpusher_app_token=WXPUSHER_APP_TOKEN,
        target_uids=TARGET_UIDS
    )
    
    # 根据命令行参数或环境变量选择推送模式
    if len(sys.argv) > 1:
        mode = sys.argv[1]
    else:
        mode = PUSH_MODE
    
    print(f"🚀 启动热搜推送器，推送模式: {mode}")
    
    # 执行推送
    if mode == 'all':
        success = pusher.push_all_platforms_trends()
    elif mode in ['weixin', 'weibo', 'douyin']:
        success = pusher.push_platform_trends(mode)
    else:
        print(f"❌ 不支持的推送模式: {mode}")
        print("支持的模式: all, weixin, weibo, douyin")
        print("使用方法: python wx_trend_pusher.py [mode]")
        return
    
    if success:
        print("🎉 推送完成！")
    else:
        print("❌ 推送失败！")


if __name__ == "__main__":
    main()