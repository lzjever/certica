# 项目结构

```
certica/
├── main.py                  # 主入口点，处理UI和CLI模式切换
├── certica/                 # 主包目录
│   ├── __init__.py         # 包初始化文件，包含版本信息
│   ├── ca_manager.py       # CA证书管理核心功能
│   ├── cert_manager.py     # 证书签发管理
│   ├── template_manager.py # 模板文件管理
│   ├── system_cert.py      # 系统证书安装/卸载
│   ├── ui.py               # 交互式UI界面
│   └── cli.py              # 命令行接口
├── pyproject.toml          # 项目配置和依赖管理（PEP 518）
├── requirements.txt        # 依赖列表
├── MANIFEST.in             # 打包时包含的文件清单
├── LICENSE                 # MIT许可证
├── README.md               # 项目主文档
├── CA_TOOL_README.md       # 详细文档
├── CA_TOOL_QUICKSTART.md   # 快速开始指南
├── STRUCTURE.md            # 目录结构说明
├── PROJECT_STRUCTURE.md    # 项目结构说明
├── .gitignore              # Git忽略规则
└── output/                 # 用户生成的文件（不提交到Git）
    ├── ca/                 # CA证书目录
    ├── certs/              # 签发的证书目录
    └── templates/          # 模板文件目录
```

## 文件说明

### 核心模块
- `ca_manager.py`: 管理根CA证书的创建、列表、删除
- `cert_manager.py`: 管理证书的签发、信息查询、删除
- `template_manager.py`: 管理模板文件的创建、加载、删除
- `system_cert.py`: 管理系统证书的安装和卸载，支持多发行版

### 接口模块
- `ui.py`: 提供交互式图形界面（使用Rich和Questionary）
- `cli.py`: 提供命令行接口（使用Click）
- `main.py`: 主入口，根据参数选择UI或CLI模式

### 配置文件
- `pyproject.toml`: 现代Python项目标准配置文件，包含项目元数据、依赖、构建配置
- `requirements.txt`: 依赖文件
- `MANIFEST.in`: 指定打包时包含的额外文件

### 文档
- `README.md`: 项目主文档，包含安装、使用说明
- `CA_TOOL_README.md`: 详细功能文档
- `CA_TOOL_QUICKSTART.md`: 快速开始指南
- `STRUCTURE.md`: 目录结构详细说明

## 最佳实践

1. **包结构**: 使用标准的Python包结构，`__init__.py` 包含版本信息
2. **依赖管理**: 使用 `pyproject.toml` 进行现代依赖管理
3. **文档**: 提供完整的README和详细文档
4. **许可证**: 包含MIT许可证文件
5. **Git忽略**: 排除输出文件、缓存文件等
6. **可执行脚本**: `main.py` 作为可执行入口点，安装后可通过 `certica` 命令运行
