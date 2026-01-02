"""
Interactive UI using questionary and rich libraries for terminal interface
"""
import os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from typing import List, Optional, Dict
import questionary
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
            return path_str[len(base_dir) + 1:]
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
    
    def _clear_and_show_header(self, title: str):
        """Clear screen and show header"""
        self.console.clear()
        self.console.print(Panel(
            f"[bold green]{title}[/bold green]",
            border_style="green",
            expand=False
        ))
        self.console.print()
    
    def _wait_for_continue(self, message: str = "按回车键继续..."):
        """Wait for user to continue"""
        questionary.press_any_key_to_continue(message=message).ask()
    
    def _show_result_panel(self, title: str, content: str, success: bool = True):
        """Show result in a panel"""
        style = "green" if success else "red"
        self.console.print()
        self.console.print(Panel(
            content,
            title=f"[bold {style}]{title}[/bold {style}]",
            border_style=style,
            expand=False
        ))
        self.console.print()
    
    def run(self):
        """Main menu loop"""
        while True:
            self.console.clear()
            self.console.print(Panel(
                "[bold green]🔒 CA证书工具[/bold green]",
                border_style="green",
                expand=False
            ))
            self.console.print()
            
            # 使用方向键选择菜单
            choice = questionary.select(
                "请选择操作:",
                choices=[
                    questionary.Choice("❌ 退出", value="0"),
                    questionary.Choice("🔐 创建根CA证书", value="1"),
                    questionary.Choice("📜 签发证书（服务器/客户端）", value="2"),
                    questionary.Choice("🔑 管理根CA证书（查看/删除）", value="3"),
                    questionary.Choice("📜 管理已签发的证书（查看/删除）", value="4"),
                    questionary.Choice("📝 管理模板文件", value="5"),
                    questionary.Choice("🔧 安装CA证书到系统", value="6"),
                    questionary.Choice("🗑️  从系统移除CA证书", value="7"),
                ],
                default="0"
            ).ask()
            
            if not choice or choice == "0":
                self.console.print("\n[green]再见！[/green]")
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
        self._clear_and_show_header("🔐 创建根CA证书")
        
        # Load template if available
        if self.template is None:
            self.template = self.template_manager.load_template()
        
        # 使用questionary收集输入
        ca_name = questionary.text("CA名称:", default="myca").ask()
        if not ca_name:
            return
        
        organization = questionary.text(
            "机构名称:",
            default=self.template.get("organization", "Development CA")
        ).ask()
        
        country = questionary.text(
            "国家代码:",
            default=self.template.get("country", "CN")
        ).ask()
        
        state = questionary.text(
            "省/州:",
            default=self.template.get("state", "Beijing")
        ).ask()
        
        city = questionary.text(
            "城市:",
            default=self.template.get("city", "Beijing")
        ).ask()
        
        validity_str = questionary.text(
            "有效期（天）:",
            default=str(self.template.get("default_validity_days", 3650))
        ).ask()
        
        key_size_str = questionary.text(
            "密钥长度:",
            default=str(self.template.get("default_key_size", 2048))
        ).ask()
        
        try:
            validity = int(validity_str) if validity_str else 3650
            key_size = int(key_size_str) if key_size_str else 2048
        except ValueError:
            self._show_result_panel("❌ 错误", "无效的数值", success=False)
            self._wait_for_continue()
            return
        
        try:
            self.console.print("\n[yellow]正在创建CA证书...[/yellow]")
            result = self.ca_manager.create_root_ca(
                ca_name=ca_name,
                organization=organization,
                country=country,
                state=state,
                city=city,
                validity_days=validity,
                key_size=key_size
            )
            
            content = f"""✓ 根CA创建成功！

**CA名称:** {ca_name}
**密钥路径:** {self._format_path(result['ca_key'])}
**证书路径:** {self._format_path(result['ca_cert'])}
**有效期:** {validity} 天
**密钥长度:** {key_size} 位"""
            
            self._show_result_panel("✅ 成功", content, success=True)
            
        except FileExistsError as e:
            self._show_result_panel("❌ 错误", f"CA已存在: {e}", success=False)
        except Exception as e:
            self._show_result_panel("❌ 错误", f"创建失败: {e}", success=False)
        
        self._wait_for_continue()
    
    def _sign_certificate(self):
        """Sign a certificate"""
        self._clear_and_show_header("📜 签发证书")
        
        # Select CA
        cas = self.ca_manager.list_cas()
        if not cas:
            self._show_result_panel("⚠️  提示", "没有可用的CA证书，请先创建根CA", success=False)
            self._wait_for_continue()
            return
        
        # 使用方向键选择CA
        ca_choices = [
            questionary.Choice(f"🔑 {ca['name']}", value=str(i))
            for i, ca in enumerate(cas)
        ]
        ca_index_str = questionary.select(
            "选择CA:",
            choices=ca_choices
        ).ask()
        
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
        cert_type = questionary.select(
            "证书类型:",
            choices=[
                questionary.Choice("🖥️  服务器证书", value="server"),
                questionary.Choice("👤 客户端证书", value="client"),
            ],
            default="server"
        ).ask()
        
        if cert_type is None:
            return
        
        cert_name = questionary.text("证书名称:").ask()
        if not cert_name:
            return
        
        common_name = questionary.text("Common Name (CN):", default=cert_name).ask()
        
        # DNS names
        dns_input = questionary.text(
            "DNS名称 (多个用逗号分隔，直接回车跳过):",
            default=""
        ).ask() or ""
        dns_names = [d.strip() for d in dns_input.split(",") if d.strip()]
        
        # IP addresses
        ip_input = questionary.text(
            "IP地址 (多个用逗号分隔，直接回车跳过):",
            default=""
        ).ask() or ""
        ip_addresses = [ip.strip() for ip in ip_input.split(",") if ip.strip()]
        
        organization = questionary.text(
            "机构名称:",
            default=self.template.get("organization", "Development")
        ).ask()
        
        country = questionary.text(
            "国家代码:",
            default=self.template.get("country", "CN")
        ).ask()
        
        state = questionary.text(
            "省/州:",
            default=self.template.get("state", "Beijing")
        ).ask()
        
        city = questionary.text(
            "城市:",
            default=self.template.get("city", "Beijing")
        ).ask()
        
        validity_str = questionary.text(
            "有效期（天）:",
            default=str(self.template.get("default_validity_days", 365))
        ).ask()
        
        key_size_str = questionary.text(
            "密钥长度:",
            default=str(self.template.get("default_key_size", 2048))
        ).ask()
        
        try:
            validity = int(validity_str) if validity_str else 365
            key_size = int(key_size_str) if key_size_str else 2048
        except ValueError:
            self._show_result_panel("❌ 错误", "无效的数值", success=False)
            self._wait_for_continue()
            return
        
        try:
            self.console.print("\n[yellow]正在签发证书...[/yellow]")
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
                key_size=key_size
            )
            
            dns_info = ", ".join(dns_names) if dns_names else "无"
            ip_info = ", ".join(ip_addresses) if ip_addresses else "无"
            
            content = f"""✓ 证书签发成功！

**证书名称:** {cert_name}
**证书类型:** {'🖥️  服务器' if cert_type == 'server' else '👤 客户端'}
**CA:** {selected_ca['name']}
**密钥路径:** {self._format_path(result['key'])}
**证书路径:** {self._format_path(result['cert'])}
**DNS名称:** {dns_info}
**IP地址:** {ip_info}
**有效期:** {validity} 天"""
            
            self._show_result_panel("✅ 成功", content, success=True)
            
        except Exception as e:
            self._show_result_panel("❌ 错误", f"签发失败: {e}", success=False)
        
        self._wait_for_continue()
    
    def _manage_cas(self):
        """Manage CA certificates - view details or delete"""
        while True:
            self._clear_and_show_header("🔑 管理根CA证书")
            
            cas = self.ca_manager.list_cas()
            if not cas:
                self._show_result_panel("⚠️  提示", "没有找到根CA证书", success=False)
                self._wait_for_continue()
                return
            
            # 显示说明
            self.console.print("[dim]💡 说明: 选择要管理的根CA证书，可以查看详细信息或删除。[/dim]")
            self.console.print()
            
            # 使用方向键选择CA
            ca_choices = [
                questionary.Choice(f"🔑 {ca['name']}", value=str(i))
                for i, ca in enumerate(cas)
            ]
            ca_choices.append(questionary.Choice("⬅️  返回主菜单", value="back"))
            
            ca_index_str = questionary.select(
                "选择要管理的根CA:",
                choices=ca_choices
            ).ask()
            
            if ca_index_str is None or ca_index_str == "back":
                return
            
            try:
                ca_index = int(ca_index_str)
                if ca_index < 0 or ca_index >= len(cas):
                    continue
                
                selected_ca = cas[ca_index]
                
                # 选择操作
                action = questionary.select(
                    f"对根CA '{selected_ca['name']}' 执行什么操作?",
                    choices=[
                        questionary.Choice("📄 查看证书详细信息", value="view"),
                        questionary.Choice("🗑️  删除CA证书（包括所有签发的证书）", value="delete"),
                        questionary.Choice("⬅️  返回", value="back")
                    ]
                ).ask()
                
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
        self._clear_and_show_header(f"📄 根CA证书详情: {ca['name']}")
        
        info = self.ca_manager.get_ca_info(ca["cert"])
        
        # 显示基本信息
        table = Table(box=box.ROUNDED, show_header=False, show_edge=False)
        table.add_column("属性", style="cyan", width=20)
        table.add_column("值", style="green")
        
        table.add_row("CA名称", f"🔑 {ca['name']}")
        table.add_row("密钥路径", self._format_path(ca["key"]))
        table.add_row("证书路径", self._format_path(ca["cert"]))
        
        self.console.print(table)
        self.console.print()
        
        # 显示证书详细信息
        self.console.print(Panel(
            info.get("info", "无法读取证书信息"),
            title="[bold]证书详细信息[/bold]",
            border_style="blue"
        ))
        
        self._wait_for_continue()
    
    def _delete_ca(self, ca: Dict[str, str]):
        """Delete a CA certificate"""
        self._clear_and_show_header(f"🗑️  删除根CA: {ca['name']}")
        
        # 检查是否有签发的证书
        certs = self.ca_manager.get_certs_by_ca(ca["name"])
        cert_count = len(certs)
        
        warning_msg = f"⚠️  警告: 删除根CA '{ca['name']}' 将同时删除:\n"
        warning_msg += f"  • CA证书和密钥\n"
        if cert_count > 0:
            warning_msg += f"  • {cert_count} 个已签发的证书\n"
        warning_msg += f"\n此操作不可恢复！"
        
        self.console.print(Panel(
            warning_msg,
            border_style="red",
            title="[bold red]确认删除[/bold red]"
        ))
        self.console.print()
        
        confirm = questionary.confirm(
            f"确定要删除根CA '{ca['name']}' 吗?",
            default=False
        ).ask()
        
        if not confirm:
            self._show_result_panel("ℹ️  提示", "已取消删除操作", success=True)
            self._wait_for_continue()
            return
        
        if self.ca_manager.delete_ca(ca["name"]):
            self._show_result_panel(
                "✅ 成功",
                f"根CA '{ca['name']}' 及其所有证书已删除",
                success=True
            )
        else:
            self._show_result_panel(
                "❌ 错误",
                f"删除根CA '{ca['name']}' 失败",
                success=False
            )
        
        self._wait_for_continue()
    
    def _manage_certificates(self):
        """Manage certificates - view details or delete"""
        while True:
            self._clear_and_show_header("📜 管理已签发的证书")
            
            # First, select which CA to query
            cas = self.ca_manager.list_cas()
            if not cas:
                self._show_result_panel("⚠️  提示", "没有找到根CA证书", success=False)
                self._wait_for_continue()
                return
            
            # 显示说明
            self.console.print("[dim]💡 说明: 选择要查看的根CA，将显示由该CA签发的所有证书。[/dim]")
            self.console.print()
            
            # 使用方向键选择CA
            ca_choices = [
                questionary.Choice(f"🔑 {ca['name']}", value=str(i))
                for i, ca in enumerate(cas)
            ]
            ca_choices.append(questionary.Choice("⬅️  返回主菜单", value="back"))
            
            ca_index_str = questionary.select(
                "选择要查询的根CA:",
                choices=ca_choices
            ).ask()
            
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
                        "⚠️  提示",
                        f"根CA '{selected_ca['name']}' 还没有签发任何证书\n\n💡 提示: 使用菜单选项 '📜 签发证书（服务器/客户端）' 来创建新证书",
                        success=False
                    )
                    self._wait_for_continue()
                    continue
                
                # 选择要管理的证书
                cert_choices = []
                for cert in certs:
                    # Try to determine certificate type
                    cert_type = "❓ 未知"
                    try:
                        import subprocess
                        result = subprocess.run(
                            ["openssl", "x509", "-in", cert["cert"], "-noout", "-ext", "extendedKeyUsage"],
                            capture_output=True,
                            text=True,
                            check=True
                        )
                        output = result.stdout.lower()
                        if "serverauth" in output or "server authentication" in output:
                            if "clientauth" in output or "client authentication" in output:
                                cert_type = "🖥️  服务器/客户端"
                            else:
                                cert_type = "🖥️  服务器"
                        elif "clientauth" in output or "client authentication" in output:
                            cert_type = "👤 客户端"
                    except:
                        pass
                    
                    cert_choices.append(
                        questionary.Choice(
                            f"📜 {cert['name']} ({cert_type})",
                            value=str(certs.index(cert))
                        )
                    )
                
                cert_choices.append(questionary.Choice("⬅️  返回", value="back"))
                
                cert_index_str = questionary.select(
                    f"选择要管理的证书（由根CA '{selected_ca['name']}' 签发）:",
                    choices=cert_choices
                ).ask()
                
                if cert_index_str is None or cert_index_str == "back":
                    continue
                
                cert_index = int(cert_index_str)
                if cert_index < 0 or cert_index >= len(certs):
                    continue
                
                selected_cert = certs[cert_index]
                
                # 选择操作
                action = questionary.select(
                    f"对证书 '{selected_cert['name']}' 执行什么操作?",
                    choices=[
                        questionary.Choice("📄 查看证书详细信息", value="view"),
                        questionary.Choice("🗑️  删除证书", value="delete"),
                        questionary.Choice("⬅️  返回", value="back")
                    ]
                ).ask()
                
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
        self._clear_and_show_header(f"📄 证书详情: {cert['name']}")
        
        info = self.cert_manager.get_certificate_info(cert["cert"])
        
        # 显示基本信息
        table = Table(box=box.ROUNDED, show_header=False, show_edge=False)
        table.add_column("属性", style="cyan", width=20)
        table.add_column("值", style="green")
        
        table.add_row("证书名称", f"📜 {cert['name']}")
        table.add_row("所属CA", f"🔑 {ca_name}")
        table.add_row("密钥路径", self._format_path(cert["key"]))
        table.add_row("证书路径", self._format_path(cert["cert"]))
        
        self.console.print(table)
        self.console.print()
        
        # 显示证书详细信息
        self.console.print(Panel(
            info.get("info", "无法读取证书信息"),
            title="[bold]证书详细信息[/bold]",
            border_style="blue"
        ))
        
        self._wait_for_continue()
    
    def _delete_certificate(self, cert: Dict[str, str], ca_name: str):
        """Delete a certificate"""
        self._clear_and_show_header(f"🗑️  删除证书: {cert['name']}")
        
        warning_msg = f"⚠️  警告: 删除证书 '{cert['name']}'\n"
        warning_msg += f"  • 证书和密钥将被永久删除\n"
        warning_msg += f"\n此操作不可恢复！"
        
        self.console.print(Panel(
            warning_msg,
            border_style="red",
            title="[bold red]确认删除[/bold red]"
        ))
        self.console.print()
        
        confirm = questionary.confirm(
            f"确定要删除证书 '{cert['name']}' 吗?",
            default=False
        ).ask()
        
        if not confirm:
            self._show_result_panel("ℹ️  提示", "已取消删除操作", success=True)
            self._wait_for_continue()
            return
        
        if self.cert_manager.delete_certificate(ca_name, cert["name"]):
            self._show_result_panel(
                "✅ 成功",
                f"证书 '{cert['name']}' 已删除",
                success=True
            )
        else:
            self._show_result_panel(
                "❌ 错误",
                f"删除证书 '{cert['name']}' 失败",
                success=False
            )
        
        self._wait_for_continue()
    
    def _manage_templates(self):
        """Manage template files"""
        while True:
            self._clear_and_show_header("📝 模板管理")
            
            # 使用方向键选择
            choice = questionary.select(
                "请选择操作:",
                choices=[
                    questionary.Choice("🔙 返回", value="0"),
                    questionary.Choice("➕ 创建模板", value="1"),
                    questionary.Choice("📋 列出模板", value="2"),
                    questionary.Choice("📥 加载模板", value="3"),
                    questionary.Choice("🗑️  删除模板", value="4"),
                ],
                default="0"
            ).ask()
            
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
        self._clear_and_show_header("➕ 创建模板")
        
        template_name = questionary.text("模板名称:").ask()
        if not template_name:
            return
        
        organization = questionary.text("默认机构名称:", default="Development").ask()
        country = questionary.text("默认国家代码:", default="CN").ask()
        state = questionary.text("默认省/州:", default="Beijing").ask()
        city = questionary.text("默认城市:", default="Beijing").ask()
        
        validity_str = questionary.text("默认有效期（天）:", default="365").ask()
        key_size_str = questionary.text("默认密钥长度:", default="2048").ask()
        
        try:
            validity = int(validity_str) if validity_str else 365
            key_size = int(key_size_str) if key_size_str else 2048
        except ValueError:
            self._show_result_panel("❌ 错误", "无效的数值", success=False)
            self._wait_for_continue()
            return
        
        path = self.template_manager.create_template(
            template_name, organization, country, state, city, validity, key_size
        )
        
        content = f"""✓ 模板创建成功！

**模板名称:** {template_name}
**模板路径:** {self._format_path(path)}
**默认机构:** {organization}
**默认有效期:** {validity} 天
**默认密钥长度:** {key_size} 位"""
        
        self._show_result_panel("✅ 成功", content, success=True)
        self._wait_for_continue()
    
    def _list_templates(self):
        """List all templates"""
        self._clear_and_show_header("📋 模板列表")
        
        templates = self.template_manager.list_templates()
        if not templates:
            self._show_result_panel("⚠️  提示", "没有找到模板文件", success=False)
            self._wait_for_continue()
            return
        
        # 显示模板列表
        table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta")
        table.add_column("模板名称", style="green")
        
        for template in templates:
            table.add_row(f"📝 {template}")
        
        self.console.print(table)
        self.console.print(f"\n[dim]共找到 {len(templates)} 个模板[/dim]")
        self._wait_for_continue()
    
    def _load_template(self):
        """Load a template"""
        self._clear_and_show_header("📥 加载模板")
        
        templates = self.template_manager.list_templates()
        if not templates:
            self._show_result_panel("⚠️  提示", "没有可用的模板", success=False)
            self._wait_for_continue()
            return
        
        # 使用方向键选择模板
        template_choices = [
            questionary.Choice(f"📝 {template}", value=str(i))
            for i, template in enumerate(templates)
        ]
        index_str = questionary.select(
            "选择模板:",
            choices=template_choices
        ).ask()
        
        if index_str is None:
            return
        
        try:
            index = int(index_str)
            if 0 <= index < len(templates):
                self.template = self.template_manager.load_template(templates[index])
                
                content = f"""✓ 模板加载成功！

**模板名称:** {templates[index]}
**默认机构:** {self.template.get('organization', 'N/A')}
**默认有效期:** {self.template.get('default_validity_days', 'N/A')} 天
**默认密钥长度:** {self.template.get('default_key_size', 'N/A')} 位"""
                
                self._show_result_panel("✅ 成功", content, success=True)
            else:
                self._show_result_panel("❌ 错误", "无效的选择", success=False)
        except ValueError:
            self._show_result_panel("❌ 错误", "无效的输入", success=False)
        
        self._wait_for_continue()
    
    def _delete_template(self):
        """Delete a template"""
        self._clear_and_show_header("🗑️  删除模板")
        
        templates = self.template_manager.list_templates()
        if not templates:
            self._show_result_panel("⚠️  提示", "没有可用的模板", success=False)
            self._wait_for_continue()
            return
        
        # 使用方向键选择模板
        template_choices = [
            questionary.Choice(f"📝 {template}", value=str(i))
            for i, template in enumerate(templates)
        ]
        index_str = questionary.select(
            "选择要删除的模板:",
            choices=template_choices
        ).ask()
        
        if index_str is None:
            return
        
        try:
            index = int(index_str)
            if 0 <= index < len(templates):
                template_name = templates[index]
                
                if questionary.confirm(f"确认删除模板 '{template_name}'?", default=False).ask():
                    if self.template_manager.delete_template(template_name):
                        self._show_result_panel("✅ 成功", f"模板 '{template_name}' 已删除", success=True)
                    else:
                        self._show_result_panel("❌ 错误", "删除失败", success=False)
            else:
                self._show_result_panel("❌ 错误", "无效的选择", success=False)
        except ValueError:
            self._show_result_panel("❌ 错误", "无效的输入", success=False)
        
        self._wait_for_continue()
    
    def _install_certificate(self):
        """Install CA certificate to system"""
        self._clear_and_show_header("🔧 安装CA证书到系统")
        
        cas = self.ca_manager.list_cas()
        if not cas:
            self._show_result_panel("⚠️  提示", "没有可用的CA证书", success=False)
            self._wait_for_continue()
            return
        
        # 使用方向键选择CA
        ca_choices = [
            questionary.Choice(f"🔑 {ca['name']}", value=str(i))
            for i, ca in enumerate(cas)
        ]
        ca_index_str = questionary.select(
            "选择要安装的CA:",
            choices=ca_choices
        ).ask()
        
        if ca_index_str is None:
            return
        
        try:
            ca_index = int(ca_index_str)
            if 0 <= ca_index < len(cas):
                selected_ca = cas[ca_index]
                
                if questionary.confirm(
                    f"确认安装CA '{selected_ca['name']}' 到系统?\n[注意: 需要sudo权限]",
                    default=False
                ).ask():
                    # Get sudo password
                    password = questionary.password(
                        "请输入sudo密码:",
                        instruction="(密码输入时不会显示)"
                    ).ask()
                    
                    if password is None:
                        self._show_result_panel("ℹ️  提示", "已取消安装操作", success=True)
                        self._wait_for_continue()
                        return
                    
                    self.console.print("\n[yellow]正在安装CA证书到系统...[/yellow]")
                    if self.system_cert_manager.install_ca_cert(selected_ca["cert"], selected_ca["name"], password):
                        self._show_result_panel(
                            "✅ 成功",
                            f"CA证书 '{selected_ca['name']}' 已安装到系统",
                            success=True
                        )
                    else:
                        self._show_result_panel(
                            "❌ 错误",
                            "安装失败，请检查密码是否正确或是否有sudo权限",
                            success=False
                        )
            else:
                self._show_result_panel("❌ 错误", "无效的选择", success=False)
        except ValueError:
            self._show_result_panel("❌ 错误", "无效的输入", success=False)
        
        self._wait_for_continue()
    
    def _remove_certificate(self):
        """Remove CA certificate from system"""
        self._clear_and_show_header("🗑️  从系统移除CA证书")
        
        ca_name = questionary.text("输入要移除的CA名称:").ask()
        if not ca_name:
            return
        
        if questionary.confirm(
            f"确认从系统移除CA '{ca_name}'?\n[注意: 需要sudo权限]",
            default=False
        ).ask():
            # Get sudo password
            password = questionary.password(
                "请输入sudo密码:",
                instruction="(密码输入时不会显示)"
            ).ask()
            
            if password is None:
                self._show_result_panel("ℹ️  提示", "已取消移除操作", success=True)
                self._wait_for_continue()
                return
            
            self.console.print("\n[yellow]正在从系统移除CA证书...[/yellow]")
            if self.system_cert_manager.remove_ca_cert(ca_name, password):
                self._show_result_panel(
                    "✅ 成功",
                    f"CA证书 '{ca_name}' 已从系统移除",
                    success=True
                )
            else:
                self._show_result_panel(
                    "❌ 错误",
                    "移除失败，请检查密码是否正确或证书是否存在",
                    success=False
                )
        
        self._wait_for_continue()
