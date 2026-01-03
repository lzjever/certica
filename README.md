# Certica 🔒

[![PyPI version](https://img.shields.io/pypi/v/certica.svg)](https://pypi.org/project/certica/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![CI](https://github.com/lzjever/certica/workflows/CI/badge.svg)](https://github.com/lzjever/certica/actions)
[![codecov](https://codecov.io/gh/lzjever/certica/branch/main/graph/badge.svg)](https://codecov.io/gh/lzjever/certica)

**Certica** is a user-friendly CA certificate generation tool for local development and testing with multi-language support.

## ✨ Features

- 🔐 **Root CA Creation** - Generate self-signed root certificates and private keys
- 📜 **Certificate Signing** - Sign server and client certificates with configurable DNS names and IP addresses
- 📝 **Template Support** - Save common configurations in templates to reduce repetitive input
- 🎨 **Interactive UI** - Beautiful terminal graphical interface using Rich library with emoji icons
- 💻 **Command Line Interface** - Full CLI support for automation and scripting
- 🔧 **System Integration** - Install/remove CA certificates from system trust store
- 🌍 **Multi-Language** - Support for English, Chinese, French, Russian, Japanese, and Korean
- 🗂️ **Smart Organization** - Certificates automatically organized by CA for easy management
- ✅ **Installation Verification** - Automatic verification of certificate installation and removal
- 🐧 **Multi-Distribution** - Automatic Linux distribution detection with appropriate installation methods

## 📦 Installation

### For End Users

#### Option 1: Install with pip (Standard Method)

```bash
pip install certica
```

#### Option 2: Install with uv (Fast and Recommended)

[uv](https://github.com/astral-sh/uv) is a fast Python package installer. First, install uv:

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then install certica from PyPI:

```bash
# Install certica using uv
uv pip install certica
```

Or if you prefer to use uv in a virtual environment:

```bash
# Create a virtual environment
uv venv

# Activate the virtual environment
# On Linux/macOS:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install certica
uv pip install certica
```

#### Verify Installation

After installation, verify that certica is installed correctly:

```bash
certica --help
```

You should see the help message with available commands.

#### Quick Start After Installation

Once installed, you can immediately start using certica:

```bash
# Launch interactive UI (recommended for beginners)
certica ui

# Or use command line mode
certica create-ca --name myca
```

### For Developers

#### Development Setup with uv (Recommended)

This project uses [uv](https://github.com/astral-sh/uv) for fast dependency management. Install uv first:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then set up the development environment:

**Recommended: For active development**

```bash
# Install package with all development dependencies (recommended)
make dev-install

# Or manually with uv (dev group is installed by default)
uv sync --group docs
```

**Alternative: Dependencies only (for CI/CD or code review)**

```bash
# Create virtual environment and install dependencies only (without installing the package)
# Useful for: CI/CD pipelines, code review, or when you only need development tools
make setup-venv

# Later, if you need to install the package:
make install
```

All `make` commands will automatically use `uv` if available, otherwise fall back to `pip`.

For detailed setup instructions, see [SETUP.md](SETUP.md).

## 🚀 Quick Start

### Interactive UI Mode (Recommended for Beginners)

To launch the interactive UI, use the `ui` command:

```bash
certica ui
```

Or with a specific language:

```bash
certica ui --lang zh  # Chinese
certica ui --lang fr  # French
certica ui --lang ru  # Russian
certica ui --lang ja  # Japanese
certica ui --lang ko  # Korean
```

**Important Notes:**
- The `--lang` option is **only available in UI mode** (`certica ui --lang <code>`)
- CLI commands always use English for script compatibility
- Running `certica` without any command shows help information

The interactive interface provides:
- 🎨 Beautiful graphical interface
- 🔒 Clear menu options with emoji icons
- 📋 Formatted table displays
- 🖥️ Automatic certificate type recognition
- 📑 Filter certificates by CA

### Command Line Mode

**Important**: 
- Running `certica` without any command shows help information
- Use `certica ui` to enter interactive mode
- The `--lang` option is **only available in UI mode** (`certica ui --lang <code>`)
- CLI commands always use English for script compatibility

#### Create Root CA Certificate

```bash
# Use default values
certica create-ca

# Custom parameters
certica create-ca --name myca --org "My Company" --validity 3650

# Use template
certica create-ca --template myorg --name myca
```

#### Sign Certificate

```bash
# Sign server certificate
certica sign --ca myca --name nginx-server --type server \
    --dns localhost --dns example.com --ip 127.0.0.1

# Sign client certificate
certica sign --ca myca --name client1 --type client

# Use template
certica sign --ca myca --name server1 --template myorg --type server
```

#### List Certificates

```bash
# List all CAs
certica list-cas

# List all signed certificates
certica list-certs

# List certificates for a specific CA
certica list-certs --ca myca
```

#### System Certificate Management

```bash
# Install CA to system (requires sudo privileges)
certica install --ca myca

# Remove CA from system (requires sudo privileges)
certica remove --ca myca
```

## 🌍 Language Support

Certica supports multiple languages in **UI mode only**. Use the `--lang` or `-l` option with the `ui` command:

```bash
# Launch UI with English (default)
certica ui

# Launch UI with Chinese
certica ui --lang zh

# Launch UI with French
certica ui --lang fr

# Launch UI with Russian
certica ui --lang ru

# Launch UI with Japanese
certica ui --lang ja

# Launch UI with Korean
certica ui --lang ko
```

**Supported languages:**
- `en` - English (default)
- `zh` - Chinese (中文)
- `fr` - French (Français)
- `ru` - Russian (Русский)
- `ja` - Japanese (日本語)
- `ko` - Korean (한국어)

**Important Notes:**
- The `--lang` option is **only available in UI mode** (`certica ui --lang <code>`)
- CLI commands always use English for script compatibility
- If an unsupported language is specified, the tool will warn and fall back to English

## 📁 Output File Structure

All generated files are saved in the `output/` directory (or the directory specified by `--base-dir`), **automatically organized by CA**:

```
output/
├── ca/                          # Root CA certificate directory
│   └── {ca_name}/               # Each CA has its own directory
│       ├── {ca_name}.key.pem    # CA private key
│       └── {ca_name}.cert.pem   # CA certificate
├── certs/                       # Signed certificate directory
│   └── {ca_name}/               # Organized by CA name
│       └── {cert_name}/         # Each certificate has its own directory
│           ├── key.pem          # Certificate private key
│           └── cert.pem         # Certificate
└── templates/                   # Template file directory
    ├── default.json
    ├── etcd.json
    └── nginx.json
```

### Directory Organization Benefits

- ✅ **Clear Separation**: Certificates signed by different CAs are automatically stored separately
- ✅ **Easy to Find**: The directory structure clearly shows the certificate ownership relationship
- ✅ **Easy to Manage**: Can easily delete a CA and all its certificates
- ✅ **Clean Paths**: Automatically removes `output/` prefix when displaying

## 📖 Usage Examples

### Example 1: Create Certificate for Local Nginx

```bash
# 1. Create root CA
certica create-ca --name local-ca

# 2. Sign server certificate
certica sign --ca local-ca --name nginx \
    --type server --dns localhost --ip 127.0.0.1

# 3. Install CA to system (so browsers won't complain)
sudo certica install --ca local-ca

# 4. Use in nginx configuration
# ssl_certificate output/certs/local-ca/nginx/cert.pem;
# ssl_certificate_key output/certs/local-ca/nginx/key.pem;
```

### Example 2: Create Certificates for etcd

```bash
# 1. Create root CA
certica create-ca --name etcd-ca

# 2. Sign server certificate
certica sign --ca etcd-ca --name etcd-server \
    --type server --dns etcd.local --dns etcd-0.etcd.local \
    --ip 10.0.0.1 --ip 10.0.0.2

# 3. Sign client certificate
certica sign --ca etcd-ca --name etcd-client --type client
```

### Example 3: Using Templates

```bash
# 1. Create template
certica create-template --name myorg \
    --org "My Organization" --country CN

# 2. Use template to create CA
certica create-ca --template myorg --name myca

# 3. Use template to sign certificate
certica sign --ca myca --name server1 \
    --template myorg --type server --dns server1.example.com
```

## 🔧 Using Generated Certificates

### For Web Servers (Nginx, Apache)

1. **Install CA to system** (so browsers trust it):
   ```bash
   sudo certica install --ca your-ca-name
   ```

2. **Configure your web server**:
   
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

### For etcd

Use the certificates in your etcd configuration:

```yaml
# etcd server
peer-cert-file: /path/to/output/certs/etcd-ca/etcd-server/cert.pem
peer-key-file: /path/to/output/certs/etcd-ca/etcd-server/key.pem

# etcd client
cert-file: /path/to/output/certs/etcd-ca/etcd-client/cert.pem
key-file: /path/to/output/certs/etcd-ca/etcd-client/key.pem
```

### For Docker

Copy certificates into your Docker containers:

```dockerfile
COPY output/certs/myca/myserver/ /etc/ssl/certs/
```

Or mount as volumes:

```bash
docker run -v /path/to/output/certs/myca/myserver:/etc/ssl/certs your-image
```

## 🖥️ System Requirements

- **Python**: 3.8 or higher
- **OpenSSL**: Usually pre-installed on Linux/macOS
- **Operating System**: Linux, macOS, or Windows

## 🐧 Supported Linux Distributions

The tool automatically detects Linux distributions and uses the appropriate certificate installation method:

- **Debian/Ubuntu**: `/usr/local/share/ca-certificates/` + `update-ca-certificates`
- **Fedora/RHEL/CentOS**: `/etc/pki/ca-trust/source/anchors/` + `update-ca-trust extract`
- **Arch/Manjaro**: `/etc/ca-certificates/trust-source/anchors/` + `trust extract-compat`
- **openSUSE/SLES**: `/etc/pki/trust/anchors/` + `update-ca-certificates`

## 📋 Command Reference

### Global Options

- `--base-dir`: Base directory for output files (default: `output`)
- `--skip-check`: Skip system requirements check
- `--check-only`: Only check system requirements and exit

### Commands

- `ui`: Launch interactive UI mode (use `--lang` option here for language selection)
- `create-ca`: Create a root CA certificate
- `sign`: Sign a certificate using the specified CA
- `list-cas`: List all available CA certificates
- `list-certs`: List all signed certificates, optionally filtered by CA
- `create-template`: Create a template file
- `list-templates`: List all available templates
- `install`: Install CA certificate to system trust store
- `remove`: Remove CA certificate from system trust store
- `info`: Show certificate information

For detailed help on any command:

```bash
certica --help              # Show all commands
certica ui --help           # Show UI mode options
certica create-ca --help    # Show create-ca options
certica sign --help         # Show sign options
```

## 🧪 Development

### Running Tests

```bash
make test          # Run all tests
make test-cov      # Run tests with coverage
```

### Code Quality

```bash
make lint          # Run linting
make format        # Format code
make check         # Run all checks
```

### Building

```bash
make build         # Build distributions
make sdist         # Build source distribution
make wheel         # Build wheel distribution
```

For more information, see:
- [SETUP.md](SETUP.md) - Development setup
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contributing guidelines
- [I18N_GUIDE.md](I18N_GUIDE.md) - Adding new languages

## 📚 Documentation

- [Quick Start Guide](CA_TOOL_QUICKSTART.md) - Quick start guide
- [Quick Start Guide (中文)](CA_TOOL_QUICKSTART_cn.md) - 快速开始指南
- [I18N Guide](I18N_GUIDE.md) - How to add or improve translations
- [Development Setup](SETUP.md) - Development environment setup
- [Contributing](CONTRIBUTING.md) - How to contribute

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

### Adding New Languages

To add support for a new language, see [I18N_GUIDE.md](I18N_GUIDE.md).

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Click](https://click.palletsprojects.com/) for CLI
- Beautiful UI powered by [Rich](https://github.com/Textualize/rich)
- Interactive prompts by [Questionary](https://github.com/tmbo/questionary)

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/metarigin/certica/issues)
- **Documentation**: [README](README.md) and [docs](CA_TOOL_README.md)

---

Made with ❤️ by [Metarigin](https://github.com/metarigin)
