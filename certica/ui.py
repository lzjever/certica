"""
Interactive UI using questionary and rich libraries for terminal interface
"""

from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from typing import Dict
import questionary
from .i18n import t
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


class CAUITool:
    """Interactive UI for CA certificate tool"""

    def __init__(self, base_dir: str = "output"):
        self.console = Console()
        self.base_dir = base_dir
        self.ca_manager = CAManager(base_dir)
        self.cert_manager = CertManager(base_dir)
        self.template_manager = TemplateManager(base_dir)
        self.system_cert_manager = SystemCertManager()
        self.template = None

    def _format_path(self, path: str) -> str:
        """Format path for display"""
        return _format_path(path, self.base_dir)

    def _get_select_instruction(self) -> str:
        """Get instruction text for select prompts"""
        return t("ui.instruction.arrow_keys")

    def _show_input_hint(self):
        """Show hint about Ctrl+C cancellation before text input"""
        self.console.print(f"[dim]{t('ui.instruction.ctrl_c')}[/dim]\n")

    def _safe_text_input(self, message: str, default: str = "", **kwargs):
        """Wrapper for questionary.text that handles KeyboardInterrupt"""
        try:
            return questionary.text(message, default=default, **kwargs).ask()
        except KeyboardInterrupt:
            # Return None to indicate cancellation
            return None

    def _safe_select(self, message: str, choices, default=None, **kwargs):
        """Wrapper for questionary.select that handles KeyboardInterrupt"""
        try:
            return questionary.select(message, choices=choices, default=default, **kwargs).ask()
        except KeyboardInterrupt:
            # Return None to indicate cancellation
            return None

    def _safe_confirm(self, message: str, default=False, **kwargs):
        """Wrapper for questionary.confirm that handles KeyboardInterrupt"""
        try:
            return questionary.confirm(message, default=default, **kwargs).ask()
        except KeyboardInterrupt:
            # Return None to indicate cancellation
            return None

    def _clear_and_show_header(self, title: str):
        """Clear screen and show header"""
        self.console.clear()
        self.console.print(
            Panel(f"[bold green]{title}[/bold green]", border_style="green", expand=False)
        )
        self.console.print()

    def _wait_for_continue(self, message: str = None):
        """Wait for user to continue"""
        if message is None:
            message = t("ui.wait_continue")
        questionary.press_any_key_to_continue(message=message).ask()

    def _show_result_panel(self, title: str, content: str, success: bool = True):
        """Show result in a panel"""
        style = "green" if success else "red"
        self.console.print()
        self.console.print(
            Panel(
                content,
                title=f"[bold {style}]{title}[/bold {style}]",
                border_style=style,
                expand=False,
            )
        )
        self.console.print()

    def run(self):
        """Main menu loop"""
        while True:
            self.console.clear()
            self.console.print(
                Panel(
                    f"[bold green]{t('ui.menu.title')}[/bold green]",
                    border_style="green",
                    expand=False,
                )
            )
            self.console.print()

            # 使用方向键选择菜单
            choice = self._safe_select(
                t("ui.menu.select_operation"),
                choices=[
                    questionary.Choice(t("ui.menu.exit"), value="0"),
                    questionary.Choice(t("ui.menu.create_ca"), value="1"),
                    questionary.Choice(t("ui.menu.sign_cert"), value="2"),
                    questionary.Choice(t("ui.menu.manage_cas"), value="3"),
                    questionary.Choice(t("ui.menu.manage_certs"), value="4"),
                    questionary.Choice(t("ui.menu.manage_templates"), value="5"),
                    questionary.Choice(t("ui.menu.install_cert"), value="6"),
                    questionary.Choice(t("ui.menu.remove_cert"), value="7"),
                ],
                default="0",
                instruction=self._get_select_instruction(),
            )

            if not choice or choice == "0":
                self.console.print(f"\n[green]{t('ui.goodbye')}[/green]")
                break
            elif choice == "1":
                self._create_root_ca()
            elif choice == "2":
                self._sign_certificate()
            elif choice == "3":
                self._manage_cas()
            elif choice == "4":
                self._manage_certificates()
            elif choice == "5":
                self._manage_templates()
            elif choice == "6":
                self._install_certificate()
            elif choice == "7":
                self._remove_certificate()

    def _create_root_ca(self):
        """Create root CA certificate"""
        self._clear_and_show_header(t("ui.create_ca.title"))
        self._show_input_hint()

        # Load template if available
        if self.template is None:
            self.template = self.template_manager.load_template()

        # 使用questionary收集输入
        ca_name = self._safe_text_input(t("ui.create_ca.ca_name"), default="myca")
        if not ca_name:
            return

        organization = self._safe_text_input(
            t("ui.create_ca.organization"),
            default=self.template.get("organization", "Development CA"),
        )
        if organization is None:
            return

        country = self._safe_text_input(
            t("ui.create_ca.country"), default=self.template.get("country", "CN")
        )
        if country is None:
            return

        state = self._safe_text_input(
            t("ui.create_ca.state"), default=self.template.get("state", "Beijing")
        )
        if state is None:
            return

        city = self._safe_text_input(
            t("ui.create_ca.city"), default=self.template.get("city", "Beijing")
        )
        if city is None:
            return

        validity_str = self._safe_text_input(
            t("ui.create_ca.validity"),
            default=str(self.template.get("default_validity_days", 3650)),
        )
        if validity_str is None:
            return

        key_size_str = self._safe_text_input(
            t("ui.create_ca.key_size"), default=str(self.template.get("default_key_size", 2048))
        )
        if key_size_str is None:
            return

        try:
            validity = int(validity_str) if validity_str else 3650
            key_size = int(key_size_str) if key_size_str else 2048
        except ValueError:
            self._show_result_panel(
                t("ui.create_ca.error"), t("ui.create_ca.error_invalid"), success=False
            )
            self._wait_for_continue()
            return

        try:
            self.console.print(f"\n[yellow]{t('ui.create_ca.creating')}[/yellow]")
            result = self.ca_manager.create_root_ca(
                ca_name=ca_name,
                organization=organization,
                country=country,
                state=state,
                city=city,
                validity_days=validity,
                key_size=key_size,
            )

            content = t(
                "ui.create_ca.success_content",
                ca_name=ca_name,
                key_path=self._format_path(result["ca_key"]),
                cert_path=self._format_path(result["ca_cert"]),
                validity=validity,
                key_size=key_size,
            )

            self._show_result_panel(t("ui.create_ca.success"), content, success=True)

        except FileExistsError as e:
            self._show_result_panel(
                t("ui.create_ca.error"), t("ui.create_ca.error_exists", error=str(e)), success=False
            )
        except Exception as e:
            self._show_result_panel(
                t("ui.create_ca.error"), t("ui.create_ca.error_failed", error=str(e)), success=False
            )

        self._wait_for_continue()

    def _sign_certificate(self):
        """Sign a certificate"""
        self._clear_and_show_header(t("ui.sign_cert.title"))

        # Select CA
        cas = self.ca_manager.list_cas()
        if not cas:
            self._show_result_panel(
                t("ui.sign_cert.no_ca"), t("ui.sign_cert.no_ca_msg"), success=False
            )
            self._wait_for_continue()
            return

        # 使用方向键选择CA
        ca_choices = [
            questionary.Choice(f"🔑 {ca['name']}", value=str(i)) for i, ca in enumerate(cas)
        ]
        ca_index_str = self._safe_select(
            t("ui.sign_cert.select_ca"),
            choices=ca_choices,
            instruction=self._get_select_instruction(),
        )

        if ca_index_str is None:
            return

        ca_index = int(ca_index_str)
        if ca_index < 0 or ca_index >= len(cas):
            return

        selected_ca = cas[ca_index]

        # Load template
        if self.template is None:
            self.template = self.template_manager.load_template()

        # Certificate type - 使用方向键选择
        cert_type = self._safe_select(
            t("ui.sign_cert.cert_type"),
            choices=[
                questionary.Choice(t("ui.sign_cert.cert_type_server"), value="server"),
                questionary.Choice(t("ui.sign_cert.cert_type_client"), value="client"),
            ],
            default="server",
            instruction=self._get_select_instruction(),
        )

        if cert_type is None:
            return

        self._show_input_hint()
        cert_name = self._safe_text_input(t("ui.sign_cert.cert_name"))
        if not cert_name:
            return

        common_name = self._safe_text_input(t("ui.sign_cert.common_name"), default=cert_name)
        if common_name is None:
            return

        # DNS names
        dns_input = self._safe_text_input(t("ui.sign_cert.dns_names"), default="") or ""
        if dns_input is None:
            return
        dns_names = [d.strip() for d in dns_input.split(",") if d.strip()]

        # IP addresses
        ip_input = self._safe_text_input(t("ui.sign_cert.ip_addresses"), default="") or ""
        if ip_input is None:
            return
        ip_addresses = [ip.strip() for ip in ip_input.split(",") if ip.strip()]

        organization = self._safe_text_input(
            t("ui.create_ca.organization"), default=self.template.get("organization", "Development")
        )
        if organization is None:
            return

        country = self._safe_text_input(
            t("ui.create_ca.country"), default=self.template.get("country", "CN")
        )
        if country is None:
            return

        state = self._safe_text_input(
            t("ui.create_ca.state"), default=self.template.get("state", "Beijing")
        )
        if state is None:
            return

        city = self._safe_text_input(
            t("ui.create_ca.city"), default=self.template.get("city", "Beijing")
        )
        if city is None:
            return

        validity_str = self._safe_text_input(
            t("ui.create_ca.validity"), default=str(self.template.get("default_validity_days", 365))
        )
        if validity_str is None:
            return

        key_size_str = self._safe_text_input(
            t("ui.create_ca.key_size"), default=str(self.template.get("default_key_size", 2048))
        )
        if key_size_str is None:
            return

        try:
            validity = int(validity_str) if validity_str else 365
            key_size = int(key_size_str) if key_size_str else 2048
        except ValueError:
            self._show_result_panel(
                t("ui.create_ca.error"), t("ui.create_ca.error_invalid"), success=False
            )
            self._wait_for_continue()
            return

        try:
            self.console.print(f"\n[yellow]{t('ui.sign_cert.signing')}[/yellow]")
            result = self.cert_manager.sign_certificate(
                ca_key=selected_ca["key"],
                ca_cert=selected_ca["cert"],
                ca_name=selected_ca["name"],
                cert_name=cert_name,
                cert_type=cert_type,
                common_name=common_name,
                dns_names=dns_names,
                ip_addresses=ip_addresses,
                organization=organization,
                country=country,
                state=state,
                city=city,
                validity_days=validity,
                key_size=key_size,
            )

            dns_info = ", ".join(dns_names) if dns_names else "None"
            ip_info = ", ".join(ip_addresses) if ip_addresses else "None"
            cert_type_display = (
                t("ui.sign_cert.type_server")
                if cert_type == "server"
                else t("ui.sign_cert.type_client")
            )

            content = t(
                "ui.sign_cert.success_content",
                cert_name=cert_name,
                cert_type=cert_type_display,
                ca_name=selected_ca["name"],
                key_path=self._format_path(result["key"]),
                cert_path=self._format_path(result["cert"]),
                dns_info=dns_info,
                ip_info=ip_info,
                validity=validity,
            )

            self._show_result_panel(t("ui.sign_cert.success"), content, success=True)

        except Exception as e:
            self._show_result_panel(
                t("ui.sign_cert.error"), t("ui.sign_cert.error_failed", error=str(e)), success=False
            )

        self._wait_for_continue()

    def _manage_cas(self):
        """Manage CA certificates - view details or delete"""
        while True:
            self._clear_and_show_header(t("ui.manage_cas.title"))

            cas = self.ca_manager.list_cas()
            if not cas:
                self._show_result_panel(
                    t("ui.manage_cas.no_cas"), t("ui.manage_cas.no_cas_msg"), success=False
                )
                self._wait_for_continue()
                return

            # 显示说明
            self.console.print(f"[dim]💡 {t('ui.manage_cas.hint')}[/dim]")
            self.console.print()

            # 使用方向键选择CA
            ca_choices = [
                questionary.Choice(f"🔑 {ca['name']}", value=str(i)) for i, ca in enumerate(cas)
            ]
            ca_choices.append(questionary.Choice(t("ui.manage_cas.back"), value="back"))

            ca_index_str = self._safe_select(
                t("ui.manage_cas.select_ca"),
                choices=ca_choices,
                instruction=self._get_select_instruction(),
            )

            if ca_index_str is None or ca_index_str == "back":
                return

            try:
                ca_index = int(ca_index_str)
                if ca_index < 0 or ca_index >= len(cas):
                    continue

                selected_ca = cas[ca_index]

                # 选择操作
                action = self._safe_select(
                    t("ui.manage_cas.select_action", ca_name=selected_ca["name"]),
                    choices=[
                        questionary.Choice(t("ui.manage_cas.action_view"), value="view"),
                        questionary.Choice(t("ui.manage_cas.action_delete"), value="delete"),
                        questionary.Choice(t("ui.manage_cas.action_back"), value="back"),
                    ],
                    instruction=self._get_select_instruction(),
                )

                if action is None or action == "back":
                    continue

                if action == "view":
                    self._show_ca_details(selected_ca)
                elif action == "delete":
                    self._delete_ca(selected_ca)

            except ValueError:
                continue

    def _show_ca_details(self, ca: Dict[str, str]):
        """Show detailed information about a CA certificate"""
        self._clear_and_show_header(t("ui.manage_cas.details.title", ca_name=ca["name"]))

        info = self.ca_manager.get_ca_info(ca["cert"])

        # 显示基本信息
        table = Table(box=box.ROUNDED, show_header=False, show_edge=False)
        table.add_column(t("ui.manage_cas.details.attribute"), style="cyan", width=20)
        table.add_column(t("ui.manage_cas.details.value"), style="green")

        table.add_row(t("ui.manage_cas.details.ca_name"), f"🔑 {ca['name']}")
        table.add_row(t("ui.manage_cas.details.key_path"), self._format_path(ca["key"]))
        table.add_row(t("ui.manage_cas.details.cert_path"), self._format_path(ca["cert"]))

        self.console.print(table)
        self.console.print()

        # 显示证书详细信息
        cert_info_text = info.get("info", t("ui.manage_cas.details.cert_info_error"))
        # 创建一个临时 Console 实例，禁用 emoji 渲染，避免证书信息中的字符被误识别为 emoji
        no_emoji_console = Console(emoji=False)
        no_emoji_console.print(
            Panel(
                cert_info_text,
                title=f"[bold]{t('ui.manage_cas.details.cert_info')}[/bold]",
                border_style="blue",
            )
        )

        self._wait_for_continue()

    def _delete_ca(self, ca: Dict[str, str]):
        """Delete a CA certificate"""
        self._clear_and_show_header(t("ui.manage_cas.delete.title", ca_name=ca["name"]))

        # 检查是否有签发的证书
        certs = self.ca_manager.get_certs_by_ca(ca["name"])
        cert_count = len(certs)

        if cert_count > 0:
            warning_msg = t(
                "ui.manage_cas.delete.warning", ca_name=ca["name"], cert_count=cert_count
            )
        else:
            warning_msg = t("ui.manage_cas.delete.warning_no_certs", ca_name=ca["name"])

        self.console.print(
            Panel(warning_msg, border_style="red", title="[bold red]⚠️  Warning[/bold red]")
        )
        self.console.print()

        confirm = self._safe_confirm(
            t("ui.manage_cas.delete.confirm", ca_name=ca["name"]), default=False
        )

        if not confirm:
            self._show_result_panel(
                t("ui.manage_cas.delete.cancelled"),
                t("ui.manage_cas.delete.cancelled_msg"),
                success=True,
            )
            self._wait_for_continue()
            return

        if self.ca_manager.delete_ca(ca["name"]):
            self._show_result_panel(
                t("ui.manage_cas.delete.success"),
                t("ui.manage_cas.delete.success_msg", ca_name=ca["name"]),
                success=True,
            )
        else:
            self._show_result_panel(
                t("ui.manage_cas.delete.error"),
                t("ui.manage_cas.delete.error_msg", ca_name=ca["name"]),
                success=False,
            )

        self._wait_for_continue()

    def _manage_certificates(self):
        """Manage certificates - view details or delete"""
        while True:
            self._clear_and_show_header(t("ui.manage_certs.title"))

            # First, select which CA to query
            cas = self.ca_manager.list_cas()
            if not cas:
                self._show_result_panel(
                    t("ui.manage_cas.no_cas"), t("ui.manage_cas.no_cas_msg"), success=False
                )
                self._wait_for_continue()
                return

            # 显示说明
            self.console.print(f"[dim]💡 {t('ui.manage_certs.hint')}[/dim]")
            self.console.print()

            # 使用方向键选择CA
            ca_choices = [
                questionary.Choice(f"🔑 {ca['name']}", value=str(i)) for i, ca in enumerate(cas)
            ]
            ca_choices.append(questionary.Choice(t("ui.manage_certs.back_to_main"), value="back"))

            ca_index_str = self._safe_select(
                t("ui.manage_certs.select_ca"),
                choices=ca_choices,
                instruction=self._get_select_instruction(),
            )

            if ca_index_str is None or ca_index_str == "back":
                return

            try:
                ca_index = int(ca_index_str)
                if ca_index < 0 or ca_index >= len(cas):
                    continue

                selected_ca = cas[ca_index]

                # Get certificates signed by this CA
                certs = self.ca_manager.get_certs_by_ca(selected_ca["name"])

                if not certs:
                    self._show_result_panel(
                        t("ui.manage_certs.no_certs"),
                        t("ui.manage_certs.no_certs_msg", ca_name=selected_ca["name"]),
                        success=False,
                    )
                    self._wait_for_continue()
                    continue

                # 选择要管理的证书
                cert_choices = []
                for cert in certs:
                    # Try to determine certificate type
                    cert_type = t("ui.manage_certs.cert_type_unknown")
                    try:
                        import subprocess

                        result = subprocess.run(
                            [
                                "openssl",
                                "x509",
                                "-in",
                                cert["cert"],
                                "-noout",
                                "-ext",
                                "extendedKeyUsage",
                            ],
                            capture_output=True,
                            text=True,
                            check=True,
                        )
                        output = result.stdout.lower()
                        if "serverauth" in output or "server authentication" in output:
                            if "clientauth" in output or "client authentication" in output:
                                cert_type = t("ui.manage_certs.cert_type_both")
                            else:
                                cert_type = t("ui.manage_certs.cert_type_server")
                        elif "clientauth" in output or "client authentication" in output:
                            cert_type = t("ui.manage_certs.cert_type_client")
                    except Exception:
                        pass

                    cert_choices.append(
                        questionary.Choice(
                            f"📜 {cert['name']} ({cert_type})", value=str(certs.index(cert))
                        )
                    )

                cert_choices.append(questionary.Choice(t("ui.manage_certs.back"), value="back"))

                cert_index_str = self._safe_select(
                    t("ui.manage_certs.select_cert", ca_name=selected_ca["name"]),
                    choices=cert_choices,
                    instruction=self._get_select_instruction(),
                )

                if cert_index_str is None or cert_index_str == "back":
                    continue

                cert_index = int(cert_index_str)
                if cert_index < 0 or cert_index >= len(certs):
                    continue

                selected_cert = certs[cert_index]

                # 选择操作
                action = self._safe_select(
                    t("ui.manage_certs.select_action", cert_name=selected_cert["name"]),
                    choices=[
                        questionary.Choice(t("ui.manage_certs.action_view"), value="view"),
                        questionary.Choice(t("ui.manage_certs.action_delete"), value="delete"),
                        questionary.Choice(t("ui.manage_cas.action_back"), value="back"),
                    ],
                    instruction=self._get_select_instruction(),
                )

                if action is None or action == "back":
                    continue

                if action == "view":
                    self._show_cert_details(selected_cert, selected_ca["name"])
                elif action == "delete":
                    self._delete_certificate(selected_cert, selected_ca["name"])

            except ValueError:
                continue

    def _show_cert_details(self, cert: Dict[str, str], ca_name: str):
        """Show detailed information about a certificate"""
        self._clear_and_show_header(t("ui.manage_certs.details.title", cert_name=cert["name"]))

        info = self.cert_manager.get_certificate_info(cert["cert"])

        # 显示基本信息
        table = Table(box=box.ROUNDED, show_header=False, show_edge=False)
        table.add_column(t("ui.manage_certs.details.attribute"), style="cyan", width=20)
        table.add_column(t("ui.manage_certs.details.value"), style="green")

        table.add_row(t("ui.manage_certs.details.cert_name"), f"📜 {cert['name']}")
        table.add_row(t("ui.manage_certs.details.ca_name"), f"🔑 {ca_name}")
        table.add_row(t("ui.manage_certs.details.key_path"), self._format_path(cert["key"]))
        table.add_row(t("ui.manage_certs.details.cert_path"), self._format_path(cert["cert"]))

        self.console.print(table)
        self.console.print()

        # 显示证书详细信息
        cert_info_text = info.get("info", t("ui.manage_certs.details.cert_info_error"))
        # 创建一个临时 Console 实例，禁用 emoji 渲染，避免证书信息中的字符被误识别为 emoji
        no_emoji_console = Console(emoji=False)
        no_emoji_console.print(
            Panel(
                cert_info_text,
                title=f"[bold]{t('ui.manage_certs.details.cert_info')}[/bold]",
                border_style="blue",
            )
        )

        self._wait_for_continue()

    def _delete_certificate(self, cert: Dict[str, str], ca_name: str):
        """Delete a certificate"""
        self._clear_and_show_header(t("ui.manage_certs.delete.title", cert_name=cert["name"]))

        warning_msg = t("ui.manage_certs.delete.warning", cert_name=cert["name"])

        self.console.print(
            Panel(
                warning_msg,
                border_style="red",
                title=f"[bold red]{t('ui.manage_certs.delete.panel_title')}[/bold red]",
            )
        )
        self.console.print()

        confirm = self._safe_confirm(
            t("ui.manage_certs.delete.confirm", cert_name=cert["name"]), default=False
        )

        if not confirm:
            self._show_result_panel(
                t("ui.manage_certs.delete.cancelled"),
                t("ui.manage_certs.delete.cancelled_msg"),
                success=True,
            )
            self._wait_for_continue()
            return

        if self.cert_manager.delete_certificate(ca_name, cert["name"]):
            self._show_result_panel(
                t("ui.manage_certs.delete.success"),
                t("ui.manage_certs.delete.success_msg", cert_name=cert["name"]),
                success=True,
            )
        else:
            self._show_result_panel(
                t("ui.manage_certs.delete.error"),
                t("ui.manage_certs.delete.error_msg", cert_name=cert["name"]),
                success=False,
            )

        self._wait_for_continue()

    def _manage_templates(self):
        """Manage template files"""
        while True:
            self._clear_and_show_header(t("ui.manage_templates.title"))

            # 使用方向键选择
            choice = self._safe_select(
                t("ui.manage_templates.select_operation"),
                choices=[
                    questionary.Choice(t("ui.manage_templates.back"), value="0"),
                    questionary.Choice(t("ui.manage_templates.create"), value="1"),
                    questionary.Choice(t("ui.manage_templates.list"), value="2"),
                    questionary.Choice(t("ui.manage_templates.load"), value="3"),
                    questionary.Choice(t("ui.manage_templates.delete"), value="4"),
                ],
                default="0",
                instruction=self._get_select_instruction(),
            )

            if not choice or choice == "0":
                break
            elif choice == "1":
                self._create_template()
            elif choice == "2":
                self._list_templates()
            elif choice == "3":
                self._load_template()
            elif choice == "4":
                self._delete_template()

    def _create_template(self):
        """Create a new template"""
        self._clear_and_show_header(t("ui.manage_templates.create.title"))

        self._show_input_hint()
        template_name = self._safe_text_input(t("ui.manage_templates.create.name"))
        if not template_name:
            return

        organization = self._safe_text_input(
            t("ui.manage_templates.create.org"), default="Development"
        )
        if organization is None:
            return
        country = self._safe_text_input(t("ui.manage_templates.create.country"), default="CN")
        if country is None:
            return
        state = self._safe_text_input(t("ui.manage_templates.create.state"), default="Beijing")
        if state is None:
            return
        city = self._safe_text_input(t("ui.manage_templates.create.city"), default="Beijing")
        if city is None:
            return

        validity_str = self._safe_text_input(
            t("ui.manage_templates.create.validity"), default="365"
        )
        if validity_str is None:
            return
        key_size_str = self._safe_text_input(
            t("ui.manage_templates.create.key_size"), default="2048"
        )
        if key_size_str is None:
            return

        try:
            validity = int(validity_str) if validity_str else 365
            key_size = int(key_size_str) if key_size_str else 2048
        except ValueError:
            self._show_result_panel(
                t("ui.install_cert.error"), t("ui.create_ca.error_invalid"), success=False
            )
            self._wait_for_continue()
            return

        path = self.template_manager.create_template(
            template_name, organization, country, state, city, validity, key_size
        )

        content = t(
            "ui.manage_templates.create.success_content",
            template_name=template_name,
            template_path=self._format_path(path),
            organization=organization,
            validity=validity,
            key_size=key_size,
        )

        self._show_result_panel(t("ui.install_cert.success"), content, success=True)
        self._wait_for_continue()

    def _list_templates(self):
        """List all templates"""
        self._clear_and_show_header(t("ui.manage_templates.list.title"))

        templates = self.template_manager.list_templates()
        if not templates:
            self._show_result_panel(
                t("ui.manage_templates.list.no_templates"),
                t("ui.manage_templates.list.no_templates_msg"),
                success=False,
            )
            self._wait_for_continue()
            return

        # 显示模板列表
        table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta")
        table.add_column(t("ui.manage_templates.list.template_name"), style="green")

        for template in templates:
            table.add_row(f"📝 {template}")

        self.console.print(table)
        self.console.print(
            f"\n[dim]{t('ui.manage_templates.list.count', count=len(templates))}[/dim]"
        )
        self._wait_for_continue()

    def _load_template(self):
        """Load a template"""
        self._clear_and_show_header(t("ui.manage_templates.load.title"))

        templates = self.template_manager.list_templates()
        if not templates:
            self._show_result_panel(
                t("ui.manage_templates.load.no_templates"),
                t("ui.manage_templates.load.no_templates_msg"),
                success=False,
            )
            self._wait_for_continue()
            return

        # 使用方向键选择模板
        template_choices = [
            questionary.Choice(f"📝 {template}", value=str(i))
            for i, template in enumerate(templates)
        ]
        index_str = self._safe_select(
            t("ui.manage_templates.load.select"),
            choices=template_choices,
            instruction=self._get_select_instruction(),
        )

        if index_str is None:
            return

        try:
            index = int(index_str)
            if 0 <= index < len(templates):
                self.template = self.template_manager.load_template(templates[index])

                content = t(
                    "ui.manage_templates.load.success_content",
                    template_name=templates[index],
                    organization=self.template.get("organization", "N/A"),
                    validity=self.template.get("default_validity_days", "N/A"),
                    key_size=self.template.get("default_key_size", "N/A"),
                )

                self._show_result_panel(t("ui.install_cert.success"), content, success=True)
            else:
                self._show_result_panel(
                    t("ui.install_cert.error"),
                    t("ui.manage_templates.load.error_invalid"),
                    success=False,
                )
        except ValueError:
            self._show_result_panel(
                t("ui.install_cert.error"), t("ui.manage_templates.load.error_input"), success=False
            )

        self._wait_for_continue()

    def _delete_template(self):
        """Delete a template"""
        self._clear_and_show_header(t("ui.manage_templates.delete.title"))

        templates = self.template_manager.list_templates()
        if not templates:
            self._show_result_panel(
                t("ui.manage_templates.list.no_templates"),
                t("ui.manage_templates.delete.no_templates_msg"),
                success=False,
            )
            self._wait_for_continue()
            return

        # 使用方向键选择模板
        template_choices = [
            questionary.Choice(f"📝 {template}", value=str(i))
            for i, template in enumerate(templates)
        ]
        index_str = self._safe_select(
            t("ui.manage_templates.delete.select"),
            choices=template_choices,
            instruction=self._get_select_instruction(),
        )

        if index_str is None:
            return

        try:
            index = int(index_str)
            if 0 <= index < len(templates):
                template_name = templates[index]

                if self._safe_confirm(
                    t("ui.manage_templates.delete.confirm", template_name=template_name),
                    default=False,
                ):
                    if self.template_manager.delete_template(template_name):
                        self._show_result_panel(
                            t("ui.install_cert.success"),
                            t(
                                "ui.manage_templates.delete.success_msg",
                                template_name=template_name,
                            ),
                            success=True,
                        )
                    else:
                        self._show_result_panel(
                            t("ui.install_cert.error"),
                            t("ui.manage_templates.delete.error_failed"),
                            success=False,
                        )
            else:
                self._show_result_panel(
                    t("ui.install_cert.error"),
                    t("ui.manage_templates.load.error_invalid"),
                    success=False,
                )
        except ValueError:
            self._show_result_panel(
                t("ui.install_cert.error"), t("ui.manage_templates.load.error_input"), success=False
            )

        self._wait_for_continue()

    def _install_certificate(self):
        """Install CA certificate to system"""
        self._clear_and_show_header(t("ui.install_cert.title"))

        cas = self.ca_manager.list_cas()
        if not cas:
            self._show_result_panel(
                t("ui.install_cert.no_cas"), t("ui.install_cert.no_cas_msg"), success=False
            )
            self._wait_for_continue()
            return

        # 使用方向键选择CA
        ca_choices = [
            questionary.Choice(f"🔑 {ca['name']}", value=str(i)) for i, ca in enumerate(cas)
        ]
        ca_index_str = self._safe_select(
            t("ui.install_cert.select_ca"),
            choices=ca_choices,
            instruction=self._get_select_instruction(),
        )

        if ca_index_str is None:
            return

        try:
            ca_index = int(ca_index_str)
            if 0 <= ca_index < len(cas):
                selected_ca = cas[ca_index]

                if self._safe_confirm(
                    t("ui.install_cert.confirm", ca_name=selected_ca["name"]),
                    default=False,
                ):
                    # Get sudo password
                    password = questionary.password(
                        t("ui.install_cert.password"),
                        instruction=t("ui.install_cert.password_hint"),
                    ).ask()

                    if password is None:
                        self._show_result_panel(
                            t("ui.install_cert.cancelled"),
                            t("ui.install_cert.cancelled_msg"),
                            success=True,
                        )
                        self._wait_for_continue()
                        return

                    self.console.print(f"\n[yellow]{t('ui.install_cert.installing')}[/yellow]")
                    if self.system_cert_manager.install_ca_cert(
                        selected_ca["cert"], selected_ca["name"], password
                    ):
                        self._show_result_panel(
                            t("ui.install_cert.success"),
                            t("ui.install_cert.success_msg", ca_name=selected_ca["name"]),
                            success=True,
                        )
                    else:
                        self._show_result_panel(
                            t("ui.install_cert.error"),
                            t("ui.install_cert.error_msg"),
                            success=False,
                        )
            else:
                self._show_result_panel(
                    t("ui.install_cert.error"), t("ui.install_cert.error_invalid"), success=False
                )
        except ValueError:
            self._show_result_panel(
                t("ui.install_cert.error"), t("ui.install_cert.error_input"), success=False
            )

        self._wait_for_continue()

    def _remove_certificate(self):
        """Remove CA certificate from system"""
        self._clear_and_show_header(t("ui.remove_cert.title"))

        self._show_input_hint()
        ca_name = self._safe_text_input(t("ui.remove_cert.ca_name"))
        if not ca_name:
            return

        if self._safe_confirm(t("ui.remove_cert.confirm", ca_name=ca_name), default=False):
            # Get sudo password
            password = questionary.password(
                t("ui.remove_cert.password"), instruction=t("ui.install_cert.password_hint")
            ).ask()

            if password is None:
                self._show_result_panel(
                    t("ui.install_cert.cancelled"), t("ui.remove_cert.cancelled_msg"), success=True
                )
                self._wait_for_continue()
                return

            self.console.print(f"\n[yellow]{t('ui.remove_cert.removing')}[/yellow]")
            if self.system_cert_manager.remove_ca_cert(ca_name, password):
                self._show_result_panel(
                    t("ui.install_cert.success"),
                    t("ui.remove_cert.success_msg", ca_name=ca_name),
                    success=True,
                )
            else:
                self._show_result_panel(
                    t("ui.install_cert.error"), t("ui.remove_cert.error_msg"), success=False
                )

        self._wait_for_continue()
