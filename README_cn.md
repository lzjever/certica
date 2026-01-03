# Certica 🔒

[![PyPI version](https://img.shields.io/pypi/v/certica.svg)](https://pypi.org/project/certica/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**Certica** 是一个用户友好的 CA 证书生成工具，用于本地开发和测试，支持多语言。

## ✨ 功能特性

- 🔐 **根 CA 创建** - 生成自签名根证书和私钥
- 📜 **证书签发** - 签发服务器和客户端证书，可配置 DNS 名称和 IP 地址
- 📝 **模板支持** - 在模板中保存常用配置，减少重复输入
- 🎨 **交互式界面** - 使用 Rich 库的美观终端图形界面，带 emoji 图标
- 💻 **命令行接口** - 完整的 CLI 支持，用于自动化和脚本
- 🔧 **系统集成** - 安装/移除系统信任存储中的 CA 证书
- 🌍 **多语言支持** - 支持英语、中文、法语、俄语、日语和韩语
- 🗂️ **智能组织** - 证书按 CA 自动组织，便于管理
- ✅ **安装验证** - 自动验证证书安装和移除
- 🐧 **多发行版支持** - 自动检测 Linux 发行版并使用相应的安装方法

## 📦 安装

### 快速安装

```bash
pip install certica
```

### 使用 uv 进行开发设置（推荐）

本项目使用 [uv](https://github.com/astral-sh/uv) 进行快速依赖管理。首先安装 uv：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

然后设置开发环境：

**推荐：用于活跃开发**

```bash
# 安装包及所有开发依赖（推荐）
make dev-install

# 或手动使用 uv（默认安装 dev 组）
uv sync --group docs
```

**替代方案：仅依赖（用于 CI/CD 或代码审查）**

```bash
# 创建虚拟环境并仅安装依赖（不安装包）
# 适用于：CI/CD 流水线、代码审查，或仅需要开发工具时
make setup-venv

# 之后，如果需要安装包：
make install
```

所有 `make` 命令会自动使用 `uv`（如果可用），否则回退到 `pip`。

详细设置说明，请参阅 [SETUP.md](SETUP.md)。

## 🚀 快速开始

### 交互式 UI 模式（推荐新手）

要启动交互式 UI，使用 `ui` 命令：

```bash
certica ui
```

或使用特定语言：

```bash
certica ui --lang zh  # 中文
certica ui --lang fr  # 法语
certica ui --lang ru  # 俄语
certica ui --lang ja  # 日语
certica ui --lang ko  # 韩语
```

**重要提示：**
- `--lang` 选项**仅在 UI 模式可用**（`certica ui --lang <code>`）
- CLI 命令始终使用英语以确保脚本兼容性
- 运行 `certica` 不带任何命令会显示帮助信息

交互式界面提供：
- 🎨 美观的图形界面
- 🔒 清晰的菜单选项，带 emoji 图标
- 📋 格式化的表格显示
- 🖥️ 自动证书类型识别
- 📑 按 CA 筛选证书

### 命令行模式

**重要提示：**
- 运行 `certica` 不带任何命令会显示帮助信息
- 使用 `certica ui` 进入交互模式
- `--lang` 选项**仅在 UI 模式可用**（`certica ui --lang <code>`）
- CLI 命令始终使用英语以确保脚本兼容性

#### 创建根 CA 证书

```bash
# 使用默认值
certica create-ca

# 自定义参数
certica create-ca --name myca --org "我的公司" --validity 3650

# 使用模板
certica create-ca --template myorg --name myca
```

#### 签发证书

```bash
# 签发服务器证书
certica sign --ca myca --name nginx-server --type server \
    --dns localhost --dns example.com --ip 127.0.0.1

# 签发客户端证书
certica sign --ca myca --name client1 --type client

# 使用模板
certica sign --ca myca --name server1 --template myorg --type server --dns server1.example.com
```

#### 列出证书

```bash
# 列出所有 CA
certica list-cas

# 列出所有已签发的证书
certica list-certs

# 列出特定 CA 的证书
certica list-certs --ca myca
```

#### 系统证书管理

```bash
# 安装 CA 到系统（需要 sudo 权限）
certica install --ca myca

# 从系统移除 CA（需要 sudo 权限）
certica remove --ca myca
```

## 🌍 语言支持

Certica 在**仅 UI 模式**支持多种语言。使用 `ui` 命令的 `--lang` 或 `-l` 选项：

```bash
# 使用英语启动 UI（默认）
certica ui

# 使用中文启动 UI
certica ui --lang zh

# 使用法语启动 UI
certica ui --lang fr

# 使用俄语启动 UI
certica ui --lang ru

# 使用日语启动 UI
certica ui --lang ja

# 使用韩语启动 UI
certica ui --lang ko
```

**支持的语言：**
- `en` - 英语（默认）
- `zh` - 中文
- `fr` - 法语（Français）
- `ru` - 俄语（Русский）
- `ja` - 日语（日本語）
- `ko` - 韩语（한국어）

**重要提示：**
- `--lang` 选项**仅在 UI 模式可用**（`certica ui --lang <code>`）
- CLI 命令始终使用英语以确保脚本兼容性
- 如果指定了不支持的语言，工具会警告并回退到英语

## 📁 输出文件结构

所有生成的文件保存在 `output/` 目录（或通过 `--base-dir` 指定的目录），**按 CA 自动组织**：

```
output/
├── ca/                          # 根 CA 证书目录
│   └── {ca_name}/               # 每个 CA 有自己的目录
│       ├── {ca_name}.key.pem    # CA 私钥
│       └── {ca_name}.cert.pem   # CA 证书
├── certs/                       # 已签发的证书目录
│   └── {ca_name}/               # 按 CA 名称组织
│       └── {cert_name}/         # 每个证书有自己的目录
│           ├── key.pem          # 证书私钥
│           └── cert.pem         # 证书
└── templates/                   # 模板文件目录
    ├── default.json
    ├── etcd.json
    └── nginx.json
```

### 目录组织优势

- ✅ **清晰分离**：不同 CA 签发的证书自动分开存储
- ✅ **易于查找**：目录结构清晰显示证书的归属关系
- ✅ **便于管理**：可以轻松删除 CA 及其所有证书
- ✅ **路径简洁**：显示时自动去掉 `output/` 前缀

## 📖 使用示例

### 示例 1：为本地 Nginx 创建证书

```bash
# 1. 创建根 CA
certica create-ca --name local-ca

# 2. 签发服务器证书
certica sign --ca local-ca --name nginx \
    --type server --dns localhost --ip 127.0.0.1

# 3. 安装 CA 到系统（这样浏览器不会报错）
sudo certica install --ca local-ca

# 4. 在 nginx 配置中使用
# ssl_certificate output/certs/local-ca/nginx/cert.pem;
# ssl_certificate_key output/certs/local-ca/nginx/key.pem;
```

### 示例 2：为 etcd 创建证书

```bash
# 1. 创建根 CA
certica create-ca --name etcd-ca

# 2. 签发服务器证书
certica sign --ca etcd-ca --name etcd-server \
    --type server --dns etcd.local --dns etcd-0.etcd.local \
    --ip 10.0.0.1 --ip 10.0.0.2

# 3. 签发客户端证书
certica sign --ca etcd-ca --name etcd-client --type client
```

### 示例 3：使用模板

```bash
# 1. 创建模板
certica create-template --name myorg \
    --org "我的组织" --country CN

# 2. 使用模板创建 CA
certica create-ca --template myorg --name myca

# 3. 使用模板签发证书
certica sign --ca myca --name server1 \
    --template myorg --type server --dns server1.example.com
```

## 🔧 使用生成的证书

### 用于 Web 服务器（Nginx、Apache）

1. **安装 CA 到系统**（让浏览器信任它）：
   ```bash
   sudo certica install --ca your-ca-name
   ```

2. **配置您的 Web 服务器**：
   
   **Nginx:**
   ```nginx
   server {
       listen 443 ssl;
       ssl_certificate /path/to/output/certs/your-ca/your-cert/cert.pem;
       ssl_certificate_key /path/to/output/certs/your-ca/your-cert/key.pem;
   }
   ```
   
   **Apache:**
   ```apache
   <VirtualHost *:443>
       SSLEngine on
       SSLCertificateFile /path/to/output/certs/your-ca/your-cert/cert.pem
       SSLCertificateKeyFile /path/to/output/certs/your-ca/your-cert/key.pem
   </VirtualHost>
   ```

### 用于 etcd

在 etcd 配置中使用证书：

```yaml
# etcd 服务器
peer-cert-file: /path/to/output/certs/etcd-ca/etcd-server/cert.pem
peer-key-file: /path/to/output/certs/etcd-ca/etcd-server/key.pem

# etcd 客户端
cert-file: /path/to/output/certs/etcd-ca/etcd-client/cert.pem
key-file: /path/to/output/certs/etcd-ca/etcd-client/key.pem
```

### 用于 Docker

将证书复制到 Docker 容器中：

```dockerfile
COPY output/certs/myca/myserver/ /etc/ssl/certs/
```

或作为卷挂载：

```bash
docker run -v /path/to/output/certs/myca/myserver:/etc/ssl/certs your-image
```

## 🖥️ 系统要求

- **Python**：3.8 或更高版本
- **OpenSSL**：通常在 Linux/macOS 上已预装
- **操作系统**：Linux、macOS 或 Windows

## 🐧 支持的 Linux 发行版

工具会自动检测 Linux 发行版并使用相应的证书安装方法：

- **Debian/Ubuntu**：`/usr/local/share/ca-certificates/` + `update-ca-certificates`
- **Fedora/RHEL/CentOS**：`/etc/pki/ca-trust/source/anchors/` + `update-ca-trust extract`
- **Arch/Manjaro**：`/etc/ca-certificates/trust-source/anchors/` + `trust extract-compat`
- **openSUSE/SLES**：`/etc/pki/trust/anchors/` + `update-ca-certificates`

## 📋 命令参考

### 全局选项

- `--base-dir`：输出文件的基础目录（默认：`output`）
- `--skip-check`：跳过系统要求检查
- `--check-only`：仅检查系统要求并退出

### 命令

- `ui`：启动交互式 UI 模式（在此处使用 `--lang` 选项进行语言选择）
- `create-ca`：创建根 CA 证书
- `sign`：使用指定的 CA 签发证书
- `list-cas`：列出所有可用的 CA 证书
- `list-certs`：列出所有已签发的证书，可按 CA 筛选
- `create-template`：创建模板文件
- `list-templates`：列出所有可用的模板
- `install`：将 CA 证书安装到系统信任存储
- `remove`：从系统信任存储移除 CA 证书
- `info`：显示证书信息

查看任何命令的详细帮助：

```bash
certica --help              # 显示所有命令
certica ui --help           # 显示 UI 模式选项
certica create-ca --help    # 显示 create-ca 选项
certica sign --help         # 显示 sign 选项
```

## 🧪 开发

### 运行测试

```bash
make test          # 运行所有测试
make test-cov      # 运行测试并查看覆盖率
```

### 代码质量

```bash
make lint          # 运行代码检查
make format        # 格式化代码
make check         # 运行所有检查
```

### 构建

```bash
make build         # 构建分发包
make sdist         # 构建源码分发包
make wheel         # 构建 wheel 分发包
```

更多信息，请参阅：
- [SETUP.md](SETUP.md) - 开发设置
- [CONTRIBUTING.md](CONTRIBUTING.md) - 贡献指南
- [I18N_GUIDE.md](I18N_GUIDE.md) - 添加新语言

## 📚 文档

- [快速开始指南](CA_TOOL_QUICKSTART_cn.md) (中文)
- [I18N 指南](I18N_GUIDE.md) - 如何添加或改进翻译
- [开发设置](SETUP.md) - 开发环境设置
- [贡献指南](CONTRIBUTING.md) - 如何贡献

## 🤝 贡献

我们欢迎贡献！详情请参阅 [CONTRIBUTING.md](CONTRIBUTING.md)。

### 添加新语言

要添加对新语言的支持，请参阅 [I18N_GUIDE.md](I18N_GUIDE.md)。

## 📝 许可证

MIT 许可证 - 详情请参阅 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- 使用 [Click](https://click.palletsprojects.com/) 构建 CLI
- 美观的 UI 由 [Rich](https://github.com/Textualize/rich) 提供支持
- 交互式提示由 [Questionary](https://github.com/tmbo/questionary) 提供

## 📞 支持

- **Issues**：[GitHub Issues](https://github.com/metarigin/certica/issues)
- **文档**：[README](README.md) 和 [docs](README.md)

---

由 [Metarigin](https://github.com/metarigin) 用 ❤️ 制作
