# 📚 Novel Online Web  
## TXT 小说一键生成静态在线阅读网站（适配老人机）

这是一个使用 **Python** 编写的静态小说网站生成脚本。  
可将本地 TXT 小说文件自动转换为 **纯 HTML 小说阅读网站**，并打包为 ZIP。

特点是 **极简 HTML + 无依赖 + 低浏览器要求**，非常适合：
- 老人机 / 功能机
- 无网络环境
- 本地离线阅读

---

## ✨ 功能说明

- 📖 自动读取 `novels/` 目录下所有 TXT 小说
- 🧠 TXT 第一行自动识别为小说名
- 📄 按固定行数自动分页生成章节
- 🔗 章节导航：上一章 / 下一章 / 返回目录
- 🧓 使用 `<font>` 标签，兼容老旧浏览器
- 📦 自动生成整站并打包为 ZIP 文件

---

## 🚀 运行环境准备

### 1. 系统要求
- 操作系统：Windows/macOS/Linux
- Python 版本：3.6 或更高版本

### 2. 安装 Python
如果你尚未安装 Python，请按以下步骤操作：

#### Windows
1. 访问 [Python 官方网站](https://www.python.org/downloads/)
2. 下载最新的 Python 3.x 版本
3. 安装时请勾选 "Add Python to PATH"
4. 安装完成后，打开命令提示符验证：
   ```bash
   python --version
   ```

#### macOS
1. 使用 Homebrew 安装：
   ```bash
   brew install python3
   ```
2. 验证安装：
   ```bash
   python3 --version
   ```

#### Linux (Ubuntu/Debian)
1. 安装 Python 3：
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip
   ```
2. 验证安装：
   ```bash
   python3 --version
   ```

### 3. 克隆项目
```bash
git clone https://github.com/yxyyds666/txt-novel-to-html.git
cd --novel-online-web
```

---

## 📖 使用方法

### 1. 准备小说文件
1. 将您的 TXT 小说文件放入 `novels/` 目录
2. 确保每本小说的第一行为小说标题（第一行会自动识别为书名）

### 2. 运行脚本
在项目根目录下运行：
```bash
python tool-novel-onlineweb.py
```

### 3. 查看输出
- 生成的网站位于 `output/site/` 目录
- 打包的 ZIP 文件位于 `output/novel_site.zip`

---

## ☁️ Cloudflare Workers 部署教程

本教程将指导您如何将生成的小说网站部署到 Cloudflare Workers，实现免费且快速的在线访问。

### 1. 准备工作
- 注册 [Cloudflare](https://www.cloudflare.com/) 账户
- 安装 [Wrangler CLI](https://developers.cloudflare.com/workers/wrangler/install-and-update/)：
  ```bash
  npm install -g wrangler
  ```

### 2. 登录 Cloudflare
```bash
wrangler login
```
这将打开浏览器让您可以授权 Wrangler 访问您的 Cloudflare 账户。

### 3. 创建 Workers 项目
```bash
wrangler init novel-reader --type javascript
cd novel-reader
```

### 4. 替换 Worker 脚本
编辑 `src/index.js` 文件，替换为以下内容（用于提供静态文件服务）：

```javascript
import { getAssetFromKV, mapRequestToAsset } from '@cloudflare/kv-asset-handler';

/**
 * 简单的静态文件服务 Worker
 */
export default {
  async fetch(request, env, ctx) {
    try {
      // 获取静态资源
      const page = await getAssetFromKV(ctx, {
        ASSET_NAMESPACE: env.ASSETS,
        ASSET_MANIFEST: env.ASSET_MANIFEST,
        mapRequestToAsset: request => {
          // 如果是根路径，返回首页
          if (request.url.endsWith('/')) {
            return new Request(`${request.url}index.html`, request);
          }
          return mapRequestToAsset(request);
        }
      });
      
      const response = new Response(page.body, page);
      response.headers.set("Content-Type", "text/html; charset=utf-8");
      response.headers.set("Cache-Control", "public, max-age=3600");
      
      return response;
    } catch (e) {
      // 如果找不到文件，则返回 404
      return new Response('File not found', { status: 404 });
    }
  }
};
```

### 5. 安装依赖
```bash
npm install @cloudflare/kv-asset-handler
```

### 6. 配置 wrangler.toml
编辑 `wrangler.toml` 文件：

```toml
name = "novel-reader"
main = "src/index.js"
compatibility_date = "2023-10-25"

[env.production]
account_id = "YOUR_ACCOUNT_ID"  # 替换为您的 Cloudflare 账户 ID
workers_dev = true
compatibility_date = "2023-10-25"

# 静态资源配置
[[routes]]
pattern = "your-domain.com/*"  # 替换为您的自定义域名
zone_id = "YOUR_ZONE_ID"      # 替换为您的 Zone ID

# 或者使用 workers.dev 域名
workers_dev = true

[site]
bucket = "./public"
entry-point = "."

# 环境变量
[vars]
ENVIRONMENT = "production"
```

### 7. 准备静态文件
1. 创建 `public` 目录并将生成的网站文件复制进去：
   ```bash
   mkdir -p public
   cp -r ../output/site/* public/
   ```

### 8. 部署到 Workers
```bash
wrangler deploy --env production
```

### 9. 高级部署方式（推荐）
对于更简单的静态文件部署，您可以使用 Cloudflare Pages：

1. 在 Cloudflare 控制台创建一个新项目
2. 选择 "Connect to Git"
3. 选择您的 GitHub 仓库
4. 配置构建设置：
   - 构建命令：`python tool-novel-onlineweb.py && cp -r output/site/* ./`
   - 构建输出目录：`.`
   - 环境变量：如果需要，可以添加环境变量

### 10. 自定义域名（可选）
1. 在 Cloudflare 控制台添加您的自定义域名
2. 按照 Cloudflare 的指引配置 DNS 记录
3. 在 Workers 配置中添加路由规则

---

## 📁 项目目录结构

```text
.
├── novels/                 # 存放 TXT 小说
│   └── example.txt
├── output/
│   ├── site/               # 生成的静态网站
│   │   ├── index.html      # 小说列表首页
│   │   └── novel_id/
│   │       ├── index.html  # 单本小说首页
│   │       ├── 001.html    # 章节页
│   │       └── ...
│   └── novel_site.zip      # 打包后的整站 ZIP
├── tool-novel-onlineweb.py # 主脚本
└── README.md               # 本说明文件（全部内容集中在这里）

