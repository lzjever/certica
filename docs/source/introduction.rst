Introduction
============

Certica is a user-friendly CA certificate generation tool designed for local development and testing. It provides both an interactive UI and a command-line interface for managing certificates.

Key Features
------------

- **Root CA Creation**: Generate self-signed root certificates and private keys
- **Certificate Signing**: Sign server and client certificates with configurable DNS names and IP addresses
- **Template Support**: Save common configurations in templates to reduce repetitive input
- **Interactive UI**: Beautiful terminal graphical interface using Rich library with emoji icons
- **Command Line Interface**: Full CLI support for automation and scripting
- **System Integration**: Install/remove CA certificates from system trust store
- **Multi-Language**: Support for English, Chinese, French, Russian, Japanese, and Korean
- **Smart Organization**: Certificates automatically organized by CA for easy management
- **Installation Verification**: Automatic verification of certificate installation and removal
- **Multi-Distribution**: Automatic Linux distribution detection with appropriate installation methods

Use Cases
---------

Certica is ideal for:

- Local web development with HTTPS
- etcd cluster certificate management
- Docker container certificate generation
- Development and testing environments
- Any scenario requiring self-signed certificates

Requirements
------------

- Python 3.8 or higher
- OpenSSL (usually pre-installed on Linux/macOS)
- Linux, macOS, or Windows

