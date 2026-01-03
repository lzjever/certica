# Certica Quick Start Guide

## Installation

### Quick Install

```bash
pip install certica
```

### Development Setup

For development, install dependencies:

```bash
# Using uv (recommended)
uv sync --group docs

# Or using pip
pip install -r requirements.txt
```

## Quick Usage

### Method 1: Interactive UI (Recommended for Beginners) ✨

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

Then follow the menu prompts. The interface features:
- 🎨 Beautiful graphical interface
- 🔒 Clear menu options with emoji icons
- 📋 Formatted table displays
- 🖥️ Automatic certificate type recognition

**Menu Options:**
- `0` ❌ Exit
- `1` 🔐 Create root CA certificate
- `2` 📜 Sign certificate (server/client)
- `3` 📋 List all CA certificates
- `4` 📑 List signed certificates (filter by CA)
- `5` 📝 Manage template files
- `6` 🔧 Install CA certificate to system
- `7` 🗑️ Remove CA certificate from system

### Method 2: Command Line (Suitable for Scripts and Automation)

#### Create Root CA

```bash
certica create-ca --name myca
```

#### Sign Certificate

```bash
# Sign server certificate
certica sign --ca myca --name nginx-server --type server \
    --dns localhost --dns example.com --ip 127.0.0.1

# Sign client certificate
certica sign --ca myca --name client1 --type client
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
sudo certica install --ca myca

# Remove CA from system (requires sudo privileges)
sudo certica remove --ca myca
```

## Common Use Cases

### Use Case 1: Local Nginx Development

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

### Use Case 2: etcd Cluster

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

### Use Case 3: Using Templates

```bash
# 1. Create template
certica create-template --name myorg \
    --org "My Organization" --country US

# 2. Use template to create CA
certica create-ca --template myorg --name myca

# 3. Use template to sign certificate
certica sign --ca myca --name server1 \
    --template myorg --type server --dns server1.example.com
```

## Output File Structure

All generated files are saved in the `output/` directory, automatically organized by CA:

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

## Important Notes

- **Language Support**: The `--lang` option is only available in UI mode (`certica ui --lang <code>`)
- **CLI Commands**: Always use English for script compatibility
- **Help**: Run `certica --help` to see all available commands
- **System Requirements**: Python 3.8+, OpenSSL (usually pre-installed)

## Getting Help

```bash
# General help
certica --help

# Command-specific help
certica create-ca --help
certica sign --help
certica ui --help
```

For more detailed documentation, see [README.md](README.md).

