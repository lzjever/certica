# Certica 项目结构说明

## 目录结构

```
certica/
├── main.py                 # 主入口脚本
├── certica/                # 主包目录
│   ├── __init__.py        # 包初始化文件
│   ├── ui.py              # 交互式界面
│   ├── cli.py             # 命令行接口
│   ├── ca_manager.py      # CA管理模块
│   ├── cert_manager.py    # 证书管理模块
│   ├── template_manager.py # 模板管理模块
│   └── system_cert.py     # 系统证书管理模块
├── requirements.txt        # 依赖文件
├── CA_TOOL_README.md      # 完整文档
├── CA_TOOL_QUICKSTART.md  # 快速开始指南
└── output/                # 输出目录（自动创建）
    ├── ca/                 # CA证书目录
    │   └── {ca_name}/      # 每个CA一个目录
    │       ├── {ca_name}.key.pem
    │       └── {ca_name}.cert.pem
    ├── certs/              # 签发的证书目录
    │   └── {ca_name}/      # 按CA组织
    │       └── {cert_name}/ # 每个证书一个目录
    │           ├── key.pem
    │           └── cert.pem
    └── templates/           # 模板文件目录
        └── *.json
```

## 文件说明

### 核心模块
- **main.py**: 主入口脚本，可以直接运行 `python main.py` 或 `certica`
- **certica/ui.py**: 交互式图形界面（使用Rich库）
- **certica/cli.py**: 命令行接口（使用Click库）

### 功能模块
- **ca_manager.py**: CA证书的创建和管理
- **cert_manager.py**: 证书的签发和管理
- **template_manager.py**: 模板文件的管理
- **system_cert.py**: 系统证书的安装和移除

### 文档
- **CA_TOOL_README.md**: 完整的使用文档
- **CA_TOOL_QUICKSTART.md**: 快速开始指南

## 使用方式

### 从项目目录内运行
```bash
python main.py
```

### 安装后运行（推荐）
```bash
pip install -e .
certica
```

## 注意事项

1. **output目录**: 所有生成的文件都保存在 `output/` 目录下
2. **目录组织**: CA和证书都按名称组织，不同CA的证书不会混淆
3. **路径显示**: 工具会自动简化路径显示，去掉 `output/` 前缀
4. **旧格式文件**: 如果发现 `output/ca/` 目录下直接有 `.pem` 文件（而不是在子目录中），这些是旧格式，可以删除

## 清理旧格式文件

如果发现旧格式文件，可以运行：
```bash
# 手动清理旧格式文件（谨慎操作）
# rm output/ca/*.pem  # 仅删除直接放在ca目录下的.pem文件
```

