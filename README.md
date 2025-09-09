# 微信热搜自动推送器

通过GitHub Actions自动获取微信热搜榜并推送到WxPusher。

## 功能特性

- 🔥 自动获取微信热搜榜（天行API）
- 📱 推送到WxPusher（微信消息推送平台）  
- ⏰ GitHub Actions定时任务（每天3次）
- 📝 Markdown格式美观展示
- 🛡️ 环境变量安全配置

## 快速开始

### 1. Fork本项目

### 2. 获取API密钥

**天行API密钥：**
1. 访问 [天行API](https://www.tianapi.com/)
2. 注册并获取API密钥
3. 找到"微信热门话题"接口

**WxPusher配置：**
1. 访问 [WxPusher](https://wxpusher.zjiecode.com/)
2. 微信扫码注册登录
3. 创建应用获取AppToken
4. 关注公众号获取UID

### 3. 配置GitHub Secrets

在你的GitHub仓库中设置以下Secrets：

- `TIANAPI_KEY`: 天行API密钥
- `WXPUSHER_APP_TOKEN`: WxPusher应用令牌
- `TARGET_UIDS`: 目标用户UID（多个用逗号分隔，如：`uid1,uid2,uid3`）

**设置方法：**
`Settings` → `Secrets and variables` → `Actions` → `New repository secret`

### 4. 启用GitHub Actions

在你的Fork仓库中：
1. 点击 `Actions` 选项卡
2. 点击绿色按钮启用工作流

## 推送时间

- 🌅 每天上午10点（北京时间）

## 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 设置环境变量
export TIANAPI_KEY="你的天行API密钥"
export WXPUSHER_APP_TOKEN="你的WxPusher应用令牌"
export TARGET_UIDS="用户UID1,用户UID2"

# 运行程序
python wx_trend_pusher.py
```

## 文件结构

```
.
├── wx_trend_pusher.py          # 主程序
├── vxtrendAPI.py               # 原始API测试文件
├── requirements.txt            # Python依赖
├── config_example.py          # 本地配置示例（已弃用）
├── .github/workflows/
│   └── daily-trend-push.yml   # GitHub Actions工作流
└── README.md                  # 说明文档
```

## 推送效果

推送的消息格式如下：

```
📱 **微信热搜榜** (2024-01-01 12:00:00)

🔥 **1.** 热搜标题1
   热度: 1234567

🔥 **2.** 热搜标题2  
   热度: 987654

...
```

## 注意事项

- WxPusher单个UID每天最多接收2000条消息
- 天行API有调用频率限制，请合理安排推送频率
- GitHub Actions免费版有使用时长限制

## 故障排除

1. **推送失败**：检查WxPusher AppToken和用户UID是否正确
2. **获取热搜失败**：检查天行API密钥是否有效
3. **Actions不运行**：确保已启用工作流且设置了所有必需的Secrets

## License

MIT