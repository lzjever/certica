"""
Command-line interface for CA certificate tool
"""

import sys
import click
from pathlib import Path
from typing import List, Optional
from .i18n import set_language, t, get_supported_languages
from .system_check import check_system_requirements
from .ca_manager import CAManager
from .cert_manager import CertManager
from .template_manager import TemplateManager
from .system_cert import SystemCertManager


def _format_path(path: str, base_dir: str = "output") -> str:
    """Format path by removing base_dir prefix for display"""
    try:
        path_str = str(path)
        # Remove base_dir prefix if present
        if path_str.startswith(base_dir + "/") or path_str.startswith(base_dir + "\\"):
            return path_str[len(base_dir) + 1 :]
        # Try with resolved absolute paths
        path_obj = Path(path).resolve()
        base_path = Path(base_dir).resolve()
        try:
            if base_path in path_obj.parents or path_obj == base_path:
                return str(path_obj.relative_to(base_path))
        except ValueError:
            pass
        # If path contains base_dir as substring, try to extract relative part
        path_parts = path_str.split(base_dir)
        if len(path_parts) > 1:
            remaining = path_parts[1].lstrip("/\\")
            return remaining if remaining else path_str
        return path_str
    except Exception:
        # If anything fails, return original path
        return str(path)


@click.group()
@click.option("--base-dir", default="output", help="Base directory for output files")
@click.option("--skip-check", is_flag=True, help="Skip system requirements check")
@click.option("--check-only", is_flag=True, help="Only check system requirements and exit")
@click.pass_context
def cli(ctx, base_dir, skip_check, check_only):
    """CA Certificate Generation Tool - Command Line Interface"""
    # If check-only flag is set, just run check and exit
    if check_only:
        success = check_system_requirements()
        sys.exit(0 if success else 1)

    # Check system requirements unless skipped
    if not skip_check:
        if not check_system_requirements():
            click.echo(f"\n{t('cli.error.system_check_failed')}", err=True)
            click.echo(t("cli.error.system_check_hint"), err=True)
            sys.exit(1)

    ctx.ensure_object(dict)
    ctx.obj["base_dir"] = base_dir
    ctx.obj["ca_manager"] = CAManager(base_dir)
    ctx.obj["cert_manager"] = CertManager(base_dir)
    ctx.obj["template_manager"] = TemplateManager(base_dir)
    ctx.obj["system_cert_manager"] = SystemCertManager()


@cli.command()
@click.option("--name", default="myca", help="CA name")
@click.option("--org", default="Development CA", help="Organization name")
@click.option("--country", default="CN", help="Country code")
@click.option("--state", default="Beijing", help="State/Province")
@click.option("--city", default="Beijing", help="City")
@click.option("--validity", default=3650, type=int, help="Validity in days")
@click.option("--key-size", default=2048, type=int, help="Key size in bits")
@click.option("--template", help="Template file to use for defaults")
@click.pass_context
def create_ca(ctx, name, org, country, state, city, validity, key_size, template):
    """Create a root CA certificate"""
    template_manager = ctx.obj["template_manager"]
    ca_manager = ctx.obj["ca_manager"]

    # Load template if provided
    if template:
        template_data = template_manager.load_template(template)
        org = template_data.get("organization", org)
        country = template_data.get("country", country)
        state = template_data.get("state", state)
        city = template_data.get("city", city)
        validity = template_data.get("default_validity_days", validity)
        key_size = template_data.get("default_key_size", key_size)

    try:
        result = ca_manager.create_root_ca(
            ca_name=name,
            organization=org,
            country=country,
            state=state,
            city=city,
            validity_days=validity,
            key_size=key_size,
        )
        base_dir = ctx.obj["base_dir"]
        click.echo(t("cli.create_ca.success"))
        click.echo(t("cli.create_ca.key", path=_format_path(result["ca_key"], base_dir)))
        click.echo(t("cli.create_ca.cert", path=_format_path(result["ca_cert"], base_dir)))
    except FileExistsError as e:
        click.echo(t("cli.create_ca.error", error=str(e)), err=True)
    except Exception as e:
        click.echo(t("cli.create_ca.error_failed", error=str(e)), err=True)


@cli.command()
@click.option("--ca", required=True, help="CA name to use for signing")
@click.option("--name", required=True, help="Certificate name")
@click.option(
    "--type", type=click.Choice(["server", "client"]), default="server", help="Certificate type"
)
@click.option("--cn", help="Common Name (defaults to certificate name)")
@click.option("--dns", multiple=True, help="DNS names (can be specified multiple times)")
@click.option("--ip", multiple=True, help="IP addresses (can be specified multiple times)")
@click.option("--org", default="Development", help="Organization name")
@click.option("--country", default="CN", help="Country code")
@click.option("--state", default="Beijing", help="State/Province")
@click.option("--city", default="Beijing", help="City")
@click.option("--validity", default=365, type=int, help="Validity in days")
@click.option("--key-size", default=2048, type=int, help="Key size in bits")
@click.option("--template", help="Template file to use for defaults")
@click.pass_context
def sign(ctx, ca, name, type, cn, dns, ip, org, country, state, city, validity, key_size, template):
    """Sign a certificate using the specified CA"""
    template_manager = ctx.obj["template_manager"]
    ca_manager = ctx.obj["ca_manager"]
    cert_manager = ctx.obj["cert_manager"]

    # Get CA
    ca_info = ca_manager.get_ca(ca)
    if not ca_info:
        click.echo(t("cli.sign.error", ca=ca), err=True)
        return

    # Load template if provided
    if template:
        template_data = template_manager.load_template(template)
        org = template_data.get("organization", org)
        country = template_data.get("country", country)
        state = template_data.get("state", state)
        city = template_data.get("city", city)
        validity = template_data.get("default_validity_days", validity)
        key_size = template_data.get("default_key_size", key_size)

    try:
        result = cert_manager.sign_certificate(
            ca_key=ca_info["key"],
            ca_cert=ca_info["cert"],
            ca_name=ca_info["name"],
            cert_name=name,
            cert_type=type,
            common_name=cn or name,
            dns_names=list(dns),
            ip_addresses=list(ip),
            organization=org,
            country=country,
            state=state,
            city=city,
            validity_days=validity,
            key_size=key_size,
        )
        base_dir = ctx.obj["base_dir"]
        click.echo(t("cli.sign.success"))
        click.echo(t("cli.create_ca.key", path=_format_path(result["key"], base_dir)))
        click.echo(t("cli.create_ca.cert", path=_format_path(result["cert"], base_dir)))
    except Exception as e:
        click.echo(t("cli.sign.error_failed", error=str(e)), err=True)


@cli.command()
@click.pass_context
def list_cas(ctx):
    """List all available CA certificates"""
    ca_manager = ctx.obj["ca_manager"]
    cas = ca_manager.list_cas()

    if not cas:
        click.echo(t("cli.list_cas.empty"))
        return

    base_dir = ctx.obj["base_dir"]
    click.echo(f"\n{t('cli.list_cas.title')}")
    for i, ca in enumerate(cas):
        click.echo(f"  {i}. 🔑 {ca['name']}")
        click.echo(f"     Key: {_format_path(ca['key'], base_dir)}")
        click.echo(f"     Cert: {_format_path(ca['cert'], base_dir)}")


@cli.command()
@click.option("--ca", help="Filter certificates by CA name")
@click.pass_context
def list_certs(ctx, ca):
    """List all signed certificates, optionally filtered by CA"""
    ca_manager = ctx.obj["ca_manager"]
    cert_manager = ctx.obj["cert_manager"]

    if ca:
        # List certificates for specific CA
        ca_info = ca_manager.get_ca(ca)
        if not ca_info:
            click.echo(t("cli.sign.error", ca=ca), err=True)
            return

        certs = ca_manager.get_certs_by_ca(ca)
        if not certs:
            click.echo(t("cli.list_certs.empty_for_ca", ca=ca))
            return

        base_dir = ctx.obj["base_dir"]
        click.echo(f"\n{t('cli.list_certs.title', ca=ca)}")
        for cert in certs:
            click.echo(f"  📜 {cert['name']}")
            click.echo(f"     Key: {_format_path(cert['key'], base_dir)}")
            click.echo(f"     Cert: {_format_path(cert['cert'], base_dir)}")
    else:
        # List all certificates
        certs = cert_manager.list_certificates()
        if not certs:
            click.echo(t("cli.list_certs.empty"))
            return

        base_dir = ctx.obj["base_dir"]
        click.echo(f"\n{t('cli.list_certs.title_all')}")
        for cert in certs:
            ca_name = cert.get("ca_name", t("cli.list_certs.ca_unknown"))
            click.echo(f"  📜 {cert['name']} (CA: {ca_name})")
            click.echo(f"     Key: {_format_path(cert['key'], base_dir)}")
            click.echo(f"     Cert: {_format_path(cert['cert'], base_dir)}")


@cli.command()
@click.option("--name", required=True, help="Template name")
@click.option("--org", default="Development", help="Organization name")
@click.option("--country", default="CN", help="Country code")
@click.option("--state", default="Beijing", help="State/Province")
@click.option("--city", default="Beijing", help="City")
@click.option("--validity", default=365, type=int, help="Default validity in days")
@click.option("--key-size", default=2048, type=int, help="Default key size in bits")
@click.pass_context
def create_template(ctx, name, org, country, state, city, validity, key_size):
    """Create a template file"""
    template_manager = ctx.obj["template_manager"]
    base_dir = ctx.obj["base_dir"]
    path = template_manager.create_template(name, org, country, state, city, validity, key_size)
    click.echo(t("cli.create_template.success", path=_format_path(path, base_dir)))


@cli.command()
@click.pass_context
def list_templates(ctx):
    """List all available templates"""
    template_manager = ctx.obj["template_manager"]
    templates = template_manager.list_templates()

    if not templates:
        click.echo(t("cli.list_templates.empty"))
        return

    click.echo(f"\n{t('cli.list_templates.title')}")
    for template in templates:
        click.echo(f"  📝 {template}")


@cli.command()
@click.option("--ca", required=True, help="CA name to install")
@click.option("--password", help="Sudo password (will prompt if not provided)")
@click.pass_context
def install(ctx, ca, password):
    """Install CA certificate to system trust store"""
    ca_manager = ctx.obj["ca_manager"]
    system_cert_manager = ctx.obj["system_cert_manager"]

    ca_info = ca_manager.get_ca(ca)
    if not ca_info:
        click.echo(t("cli.install.error", ca=ca), err=True)
        return

    # Get password if not provided
    if password is None:
        password = click.prompt(t("cli.install.password_prompt"), hide_input=True, default="")
        if not password:
            click.echo(t("cli.install.password_required"), err=True)
            return

    if system_cert_manager.install_ca_cert(ca_info["cert"], ca_info["name"], password):
        click.echo(t("cli.install.success", ca=ca))
    else:
        click.echo(t("cli.install.error_failed"), err=True)


@cli.command()
@click.option("--ca", required=True, help="CA name to remove")
@click.option("--password", help="Sudo password (will prompt if not provided)")
@click.pass_context
def remove(ctx, ca, password):
    """Remove CA certificate from system trust store"""
    system_cert_manager = ctx.obj["system_cert_manager"]

    # Get password if not provided
    if password is None:
        password = click.prompt(t("cli.install.password_prompt"), hide_input=True, default="")
        if not password:
            click.echo(t("cli.install.password_required"), err=True)
            return

    if system_cert_manager.remove_ca_cert(ca, password):
        click.echo(t("cli.remove.success", ca=ca))
    else:
        click.echo(t("cli.remove.error_failed"), err=True)


@cli.command()
@click.option("--cert", required=True, help="Certificate path to show info")
@click.pass_context
def info(ctx, cert):
    """Show certificate information"""
    cert_manager = ctx.obj["cert_manager"]
    info = cert_manager.get_certificate_info(cert)
    click.echo(info["info"])


@cli.command()
@click.option("--lang", "-l", default="en", help="Language code for UI (en, zh, fr, ru, ja, ko)")
@click.pass_context
def ui(ctx, lang):
    """Launch interactive UI mode"""
    from .ui import CAUITool

    # Set language for UI
    if not set_language(lang):
        click.echo(t("lang.unsupported", lang=lang), err=True)
        set_language("en")

    # Check system requirements
    if not check_system_requirements():
        click.echo(f"\n{t('main.error.system_check')}", err=True)
        click.echo(t("main.error.system_check_hint"), err=True)
        sys.exit(1)

    # Launch UI
    base_dir = ctx.obj["base_dir"]
    tool = CAUITool(base_dir=base_dir)
    try:
        tool.run()
    except KeyboardInterrupt:
        click.echo(f"\n\n{t('main.exiting')}")
        sys.exit(0)


def main():
    """Main entry point for CLI"""
    cli()
