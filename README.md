# Certica - CA Certificate Generation Tool

一个简单易用的CA证书生成工具，用于本地开发和测试。

## 功能特性

1. **创建根CA证书** - 生成自签名根证书和私钥
2. **签发证书** - 支持服务器和客户端证书签发，可配置DNS名称、IP地址等
3. **模板支持** - 使用模板文件保存常用配置，减少重复输入
4. **交互式界面** - 提供友好的终端图形界面（使用Rich库，支持emoji图标）
5. **命令行接口** - 支持完整的命令行操作
6. **系统集成** - 可以将CA证书安装到系统信任存储，或从系统中移除
7. **智能目录组织** - 证书按CA自动分类存储，清晰易管理
8. **路径简化显示** - 自动去掉冗长的路径前缀，显示更简洁
9. **多发行版支持** - 自动检测Linux发行版，使用相应的证书安装方法
10. **安装验证** - 自动验证证书安装和卸载是否成功

## 安装

### 从源码安装

```bash
# 克隆仓库
git clone https://github.com/metarigin/certica.git
cd certica

# 安装依赖
pip install -r requirements.txt

# 或者使用 pip 安装
pip install -e .
```

### 使用 pip 安装（如果已发布到 PyPI）

```bash
pip install certica
```

## 快速开始

### 交互式界面（推荐）

直接运行脚本（不带参数）进入交互式界面：

```bash
python main.py
```

或者如果已安装：

```bash
certica
```

交互式界面提供：
- 🎨 美观的图形界面（使用Rich库）
- 🔒 清晰的菜单选项（带emoji图标）
- 📋 格式化的表格显示
- 🖥️ 自动识别证书类型（服务器/客户端）
- 📑 按CA筛选证书列表

### 命令行模式

#### 创建根CA证书

```bash
# 使用默认值
certica create-ca

# 自定义参数
certica create-ca --name myca --org "My Company" --validity 3650

# 使用模板
certica create-ca --template default
```

#### 签发证书

```bash
# 签发服务器证书
certica sign --ca myca --name nginx-server --type server \
    --dns localhost --dns example.com --ip 127.0.0.1

# 签发客户端证书
certica sign --ca myca --name client1 --type client

# 使用模板
certica sign --ca myca --name etcd-server --type server \
    --template etcd --dns etcd.local --ip 10.0.0.1
```

#### 管理证书

```bash
# 列出所有CA
certica list-cas

# 列出所有已签发的证书
certica list-certs

# 列出特定CA签发的证书
certica list-certs --ca myca
```

#### 系统证书管理

```bash
# 安装CA到系统（需要sudo权限）
certica install --ca myca

# 从系统移除CA（需要sudo权限）
certica remove --ca myca
```

## 文件结构

所有生成的文件都保存在 `output/` 目录下，**按CA自动组织**：

```
output/
├── ca/                          # 根CA证书目录
│   └── {ca_name}/               # 每个CA有自己的目录
│       ├── {ca_name}.key.pem    # CA私钥
│       └── {ca_name}.cert.pem   # CA证书
├── certs/                       # 签发的证书目录
│   └── {ca_name}/               # 按CA名称组织
│       └── {cert_name}/         # 每个证书有自己的目录
│           ├── key.pem          # 证书私钥
│           └── cert.pem         # 证书
└── templates/                   # 模板文件目录
    ├── default.json
    ├── etcd.json
    └── nginx.json
```

### 目录组织优势

- ✅ **清晰分离**：不同CA签发的证书自动分开存储
- ✅ **易于查找**：从目录结构就能看出证书的归属关系
- ✅ **便于管理**：可以轻松删除某个CA及其所有证书
- ✅ **路径简洁**：显示时自动去掉 `output/` 前缀

## 系统要求

- Python 3.8+
- OpenSSL（系统自带）
- Linux/macOS/Windows

## 支持的Linux发行版

工具会自动检测Linux发行版并使用相应的证书安装方法：

- **Debian/Ubuntu**: `/usr/local/share/ca-certificates/` + `update-ca-certificates`
- **Fedora/RHEL/CentOS**: `/etc/pki/ca-trust/source/anchors/` + `update-ca-trust extract`
- **Arch/Manjaro**: `/etc/ca-certificates/trust-source/anchors/` + `trust extract-compat`
- **openSUSE/SLES**: `/etc/pki/trust/anchors/` + `update-ca-certificates`

## 依赖

- `click>=7.0.0` - 命令行接口
- `rich>=10.0.0` - 终端美化
- `questionary>=1.10.0` - 交互式提示

## 系统检查

工具在启动时会自动检查所需的系统工具是否可用：

- **必需工具**：OpenSSL（用于证书生成）
- **可选工具**：系统证书管理工具（用于安装证书到系统）
  - Linux: `update-ca-certificates`, `update-ca-trust`, `trust`, `sudo`
  - macOS: `security`, `sudo`
  - Windows: `certutil`

### 手动检查系统要求

```bash
# 仅检查系统要求
certica --check-only

# 跳过系统检查（不推荐）
certica --skip-check <command>
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 更多文档

- [快速开始指南](CA_TOOL_QUICKSTART.md)
- [详细文档](CA_TOOL_README.md)
- [项目结构说明](STRUCTURE.md)

