# 知了青年 - 文创经营决策系统

## 🚀 一键部署到 Vercel

### 方法一：网页上传（最简单）

1. 打开 [vercel.com](https://vercel.com)，用 GitHub/邮箱 登录
2. 点击「Add New...」→「Project」
3. 选择「Import Third-Party Git Repository」或直接上传文件夹
4. 上传这个文件夹的所有文件
5. 点击「Deploy」
6. 等待1分钟，获得在线地址！

### 方法二：命令行部署

```bash
# 安装 Vercel CLI
npm i -g vercel

# 登录
vercel login

# 部署
cd zhiliao-vercel
vercel --prod
```

---

## 📁 文件结构

```
zhiliao-vercel/
├── api/
│   └── dashboard.js    # 后端API（连接飞书）
├── public/
│   └── index.html      # 前端页面
├── package.json
├── vercel.json         # Vercel配置（含飞书密钥）
└── README.md
```

---

## ⚙️ 飞书配置（已填入）

| 参数 | 值 |
|------|-----|
| App ID | cli_a9f85a3bc2f85bd9 |
| App Secret | LCAnNoRSHN4pOZKDIMMpXdC4YamqDcLz |
| App Token | CTGAbIKYYap81Msk8iVc5ELOn4b |
| Table ID | tblGN0MqO6YtoaqT |

---

## ✅ 飞书权限检查

部署后如果显示错误，请确认：

1. **应用已发布**：飞书开放平台 → 版本管理 → 申请发布
2. **权限已开启**：权限管理 → 开启 `bitable:record:read`
3. **表格已授权**：在多维表格中 → ... → 添加文档应用 → 选择你的应用

---

## 🔗 部署成功后

访问：`https://你的项目名.vercel.app`

即可看到实时数据面板！

---

## 📱 分享给团队

部署成功后，把链接分享给团队成员，他们可以：
- 随时查看最新销售数据
- 点击「刷新」获取最新数据
- 手机电脑都能访问
