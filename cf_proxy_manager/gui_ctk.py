"""
CF Proxy Manager - CustomTkinter GUI
现代化图形用户界面
"""
import customtkinter as ctk
from tkinter import messagebox
import threading
from typing import Optional, List

from .models import Config, IPEntry, DEFAULT_IPS, DEFAULT_TARGET_NODE
from .config_manager import ConfigManager
from .parsers import URLParser, IPParser
from .speed_tester import SpeedTester
from .hosts_manager import HostsManager
from .admin_helper import AdminHelper
from .logger import logger
from .components.theme import AppTheme
from .components.ip_card import IPCard
from .components.comparison_section import ComparisonSection


class CFProxyManagerCTk(ctk.CTk):
    """CF Proxy Manager - CustomTkinter 版本"""
    
    def __init__(self):
        super().__init__()
        
        # 窗口配置
        self.title(f"🐯 虎哥API反代 v{self._get_version()}")
        self.geometry("1200x700")
        self.minsize(1000, 600)
        
        # 初始化组件
        self.config_manager = ConfigManager()
        self.speed_tester = SpeedTester(timeout=3.0)
        self.hosts_manager = HostsManager()
        
        # 加载配置
        self.config = self.config_manager.load()
        
        # 设置主题
        theme_mode = getattr(self.config, 'theme_mode', 'system')
        if theme_mode not in AppTheme.THEME_MODES:
            theme_mode = 'system'
        ctk.set_appearance_mode(theme_mode)
        ctk.set_default_color_theme("blue")
        
        # 测试结果缓存
        self.test_results = {}
        
        # IP 卡片列表
        self.ip_cards: List[IPCard] = []
        
        # 最后选中的卡片（用于 Shift 批量选中）
        self._last_selected_card: Optional[IPCard] = None
        
        # 测速状态
        self.is_testing = False
        
        # 创建界面
        self._create_widgets()
        self._load_config_to_ui()
    
    def _create_widgets(self):
        """创建所有界面组件 - 左右两栏布局"""
        # 主容器
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 配置 grid 权重，使左右两栏可以自适应
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # 左侧面板：配置 + 优选IP
        self.left_panel = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        # 右侧面板：效果对比 + 状态
        self.right_panel = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        
        # === 左侧内容 ===
        # 1. 目标反代节点区域
        self._create_target_node_section()
        
        # 2. CF 反代配置区域
        self._create_cf_proxy_section()
        
        # 3. 优选 IP 管理区域
        self._create_ip_management_section()
        
        # === 右侧内容 ===
        # 4. 效果对比区域
        self._create_comparison_section()
        
        # 5. 状态显示区域
        self._create_status_section()
    
    def _create_target_node_section(self):
        """创建目标反代节点区域"""
        frame = ctk.CTkFrame(self.left_panel)
        frame.pack(fill="x", pady=(0, 10))
        
        # 标题
        title = ctk.CTkLabel(frame, text="📡 目标反代节点", font=AppTheme.FONT_BOLD)
        title.pack(anchor="w", padx=15, pady=(10, 5))
        
        # 内容行
        row = ctk.CTkFrame(frame, fg_color="transparent")
        row.pack(fill="x", padx=15, pady=(0, 10))
        
        ctk.CTkLabel(row, text="当前节点:", font=AppTheme.FONT_DEFAULT).pack(side="left")
        
        self.target_node_var = ctk.StringVar()
        self.target_node_combo = ctk.CTkComboBox(
            row,
            variable=self.target_node_var,
            width=200,
            font=AppTheme.FONT_DEFAULT,
            command=self._on_target_node_changed
        )
        self.target_node_combo.pack(side="left", padx=10, fill="x", expand=True)
        
        ctk.CTkButton(
            row, text="添加", width=60,
            command=self._on_add_target_node
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            row, text="删除", width=60,
            fg_color="gray50", hover_color="gray40",
            command=self._on_delete_target_node
        ).pack(side="left", padx=2)
    
    def _create_cf_proxy_section(self):
        """创建 CF 反代配置区域"""
        frame = ctk.CTkFrame(self.left_panel)
        frame.pack(fill="x", pady=(0, 10))
        
        # 标题
        title = ctk.CTkLabel(frame, text="🌐 CF 反代配置", font=AppTheme.FONT_BOLD)
        title.pack(anchor="w", padx=15, pady=(10, 5))
        
        # 反代域名输入
        row1 = ctk.CTkFrame(frame, fg_color="transparent")
        row1.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(row1, text="反代域名/URL:", font=AppTheme.FONT_DEFAULT).pack(side="left")
        
        self.cf_domain_var = ctk.StringVar()
        self.cf_domain_entry = ctk.CTkEntry(
            row1,
            textvariable=self.cf_domain_var,
            width=250,
            font=AppTheme.FONT_DEFAULT
        )
        self.cf_domain_entry.pack(side="left", padx=10, fill="x", expand=True)
        self.cf_domain_var.trace_add('write', self._on_cf_domain_changed)
        
        # 完整代理地址显示
        row2 = ctk.CTkFrame(frame, fg_color="transparent")
        row2.pack(fill="x", padx=15, pady=(0, 10))
        
        ctk.CTkLabel(row2, text="完整代理地址:", font=AppTheme.FONT_DEFAULT).pack(side="left")
        
        self.full_proxy_url_var = ctk.StringVar()
        self.full_proxy_url_label = ctk.CTkLabel(
            row2,
            textvariable=self.full_proxy_url_var,
            text_color=AppTheme.COLORS["primary"],
            font=AppTheme.FONT_DEFAULT
        )
        self.full_proxy_url_label.pack(side="left", padx=10)

    def _create_comparison_section(self):
        """创建效果对比区域"""
        frame = ctk.CTkFrame(self.right_panel)
        frame.pack(fill="both", expand=True, pady=(0, 10))
        
        self.comparison_section = ComparisonSection(
            frame,
            config=self.config,
            get_user_domain=lambda: self.cf_domain_var.get(),
            get_optimized_ip=self._get_best_ip,
            on_apply=self._on_apply_comparison_result,
            on_save_config=self._save_config
        )
        self.comparison_section.pack(fill="both", expand=True)
    
    def _get_best_ip(self) -> Optional[str]:
        """获取当前最佳 IP"""
        if not self.test_results:
            return self.config.selected_ip
        
        results = list(self.test_results.values())
        best = SpeedTester.get_best_ip(results)
        return best.ip_entry.ip if best else self.config.selected_ip
    
    def _on_apply_comparison_result(self, result):
        """应用对比结果
        
        根据选中的结果类型：
        1. 我的反代 (优选IP) → 应用优选IP到用户域名hosts，复制用户域名URL
        2. 我的反代 (直连) → 清除用户域名hosts，复制用户域名URL
        3. 公共服务 (优选IP) → 应用优选IP到该服务域名hosts，复制该服务URL
        4. 公共服务 (直连) → 清除该服务域名hosts（如果有），复制该服务URL
        """
        from urllib.parse import urlparse
        
        logger.info(f"应用对比结果: {result.service.name}, is_optimized={result.is_optimized}, is_baseline={result.is_baseline}")
        logger.debug(f"服务URL: {result.service.url}")
        
        # 解析选中服务的域名
        parsed = urlparse(result.service.url)
        service_domain = parsed.hostname
        service_url = result.service.url
        
        # 用户配置的反代域名
        user_cf_domain = URLParser.extract_domain(self.cf_domain_var.get())
        user_url = f"https://{user_cf_domain}" if user_cf_domain else ""
        
        logger.debug(f"service_domain={service_domain}, user_cf_domain={user_cf_domain}")
        
        best_ip = self._get_best_ip()
        
        if result.is_baseline:
            # 基准测试（我的反代直连）→ 清除用户域名hosts，复制用户URL
            if user_cf_domain:
                self.hosts_manager.backup()
                self.hosts_manager.remove_entry(user_cf_domain)
                self.hosts_manager.flush_dns()
                self._update_hosts_status()
                self.config.selected_ip = None
                self._save_config()
                
                self._copy_to_clipboard(user_url)
                self.status_var.set(f"已清除优选IP，URL已复制（直连模式）")
            else:
                messagebox.showinfo("提示", "请先配置 CF 反代域名")
        
        elif result.is_optimized:
            # 带优选IP的结果
            if not best_ip:
                messagebox.showinfo("提示", "没有可用的优选IP，请先测速")
                return
            
            if not service_domain:
                messagebox.showerror("错误", "无法解析服务域名")
                return
            
            # 判断是用户反代还是公共服务
            is_user_proxy = (service_domain == user_cf_domain) or result.service.name.startswith("我的反代")
            
            if is_user_proxy:
                # 我的反代 (优选IP) → 应用到用户域名
                target_domain = user_cf_domain
                copy_url = user_url
            else:
                # 公共服务 (优选IP) → 应用到该服务域名
                target_domain = service_domain
                copy_url = service_url
            
            logger.info(f"应用优选IP: {target_domain} -> {best_ip}")
            
            self.hosts_manager.backup()
            success = self.hosts_manager.update_entry(target_domain, best_ip)
            
            if success:
                self.hosts_manager.flush_dns()
                self._update_hosts_status()
                self.config.selected_ip = best_ip
                self._save_config()
                
                self._copy_to_clipboard(copy_url)
                self.status_var.set(f"已应用 {target_domain} -> {best_ip}，URL已复制")
            else:
                messagebox.showerror("错误", "修改 hosts 文件失败，请以管理员身份运行")
        
        else:
            # 公共服务直连结果 → 清除用户域名hosts（如果有），复制公共服务URL
            if user_cf_domain:
                self.hosts_manager.backup()
                self.hosts_manager.remove_entry(user_cf_domain)
                self.hosts_manager.flush_dns()
                self._update_hosts_status()
                self.config.selected_ip = None
                self._save_config()
            
            self._copy_to_clipboard(service_url)
            self.status_var.set(f"已清除优选IP，已复制: {service_url}")
    
    def _copy_to_clipboard(self, text: str):
        """复制文本到剪贴板"""
        try:
            self.clipboard_clear()
            self.clipboard_append(text)
            messagebox.showinfo("已复制", f"URL已复制到剪贴板:\n{text}")
        except Exception as e:
            messagebox.showerror("错误", f"复制失败: {e}")

    def _create_ip_management_section(self):
        """创建优选 IP 管理区域"""
        frame = ctk.CTkFrame(self.left_panel)
        frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # 标题
        title = ctk.CTkLabel(frame, text="📋 优选 IP 管理", font=AppTheme.FONT_BOLD)
        title.pack(anchor="w", padx=15, pady=(10, 5))
        
        # IP 卡片列表（可滚动）
        self.ip_scroll_frame = ctk.CTkScrollableFrame(
            frame,
            fg_color="transparent"
        )
        self.ip_scroll_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # 添加 IP 输入
        add_frame = ctk.CTkFrame(frame, fg_color="transparent")
        add_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(add_frame, text="添加 IP:", font=AppTheme.FONT_DEFAULT).pack(side="left")
        
        self.add_ip_var = ctk.StringVar()
        self.add_ip_entry = ctk.CTkEntry(
            add_frame,
            textvariable=self.add_ip_var,
            width=200,
            font=AppTheme.FONT_DEFAULT,
            placeholder_text="IP:端口，如 1.2.3.4:443"
        )
        self.add_ip_entry.pack(side="left", padx=10, fill="x", expand=True)
        self.add_ip_entry.bind('<Return>', lambda e: self._on_add_ip())
        
        ctk.CTkButton(
            add_frame, text="➕ 添加", width=70,
            command=self._on_add_ip
        ).pack(side="left")
        
        # 操作按钮
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(5, 10))
        
        self.test_btn = ctk.CTkButton(
            btn_frame,
            text="🚀 开始测速",
            width=100,
            fg_color=AppTheme.COLORS["primary"],
            command=self._on_test_speed
        )
        self.test_btn.pack(side="left", padx=2)
        
        ctk.CTkButton(
            btn_frame,
            text="✅ 应用选中",
            width=90,
            fg_color=AppTheme.COLORS["success"],
            hover_color="#218838",
            command=self._on_apply_selected_ip
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            btn_frame,
            text="🗑️ 删除",
            width=70,
            fg_color="gray50",
            hover_color="gray40",
            command=self._on_delete_ip
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            btn_frame,
            text="🧹 清hosts",
            width=80,
            fg_color=AppTheme.COLORS["danger"],
            hover_color="#c82333",
            command=self._on_clear_hosts
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            btn_frame,
            text="📥 导入订阅",
            width=90,
            fg_color=AppTheme.COLORS["info"] if hasattr(AppTheme.COLORS, "info") else "#17a2b8",
            hover_color="#138496",
            command=self._show_import_dialog
        ).pack(side="left", padx=2)
    
    def _create_status_section(self):
        """创建状态显示区域"""
        frame = ctk.CTkFrame(self.right_panel)
        frame.pack(fill="x")
        
        # 标题行
        title_row = ctk.CTkFrame(frame, fg_color="transparent")
        title_row.pack(fill="x", padx=15, pady=(10, 5))
        
        ctk.CTkLabel(title_row, text="📊 状态", font=AppTheme.FONT_BOLD).pack(side="left")
        
        # 主题切换
        theme_frame = ctk.CTkFrame(title_row, fg_color="transparent")
        theme_frame.pack(side="right")
        
        ctk.CTkLabel(theme_frame, text="主题:", font=AppTheme.FONT_SMALL).pack(side="left", padx=5)
        
        self.theme_var = ctk.StringVar(value=ctk.get_appearance_mode())
        self.theme_menu = ctk.CTkOptionMenu(
            theme_frame,
            variable=self.theme_var,
            values=["深色", "浅色", "跟随系统"],
            width=90,
            font=AppTheme.FONT_SMALL,
            command=self._on_theme_changed
        )
        # 设置当前主题显示
        current_mode = ctk.get_appearance_mode().lower()
        if current_mode == "dark":
            self.theme_var.set("深色")
        elif current_mode == "light":
            self.theme_var.set("浅色")
        else:
            self.theme_var.set("跟随系统")
        self.theme_menu.pack(side="left")
        
        # 状态信息容器
        info_frame = ctk.CTkFrame(frame, fg_color="transparent")
        info_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        # 左列：权限和hosts状态
        left_col = ctk.CTkFrame(info_frame, fg_color="transparent")
        left_col.pack(side="left", fill="x", expand=True)
        
        # 权限状态
        row0 = ctk.CTkFrame(left_col, fg_color="transparent")
        row0.pack(fill="x", pady=2)
        
        ctk.CTkLabel(row0, text="权限:", font=AppTheme.FONT_SMALL).pack(side="left")
        
        admin_color = AppTheme.COLORS["success"] if AdminHelper.is_admin() else AppTheme.COLORS["danger"]
        self.admin_status_label = ctk.CTkLabel(
            row0,
            text=AdminHelper.get_status_text(),
            text_color=admin_color,
            font=AppTheme.FONT_SMALL
        )
        self.admin_status_label.pack(side="left", padx=5)
        
        # 当前 hosts 配置
        row1 = ctk.CTkFrame(left_col, fg_color="transparent")
        row1.pack(fill="x", pady=2)
        
        ctk.CTkLabel(row1, text="Hosts:", font=AppTheme.FONT_SMALL).pack(side="left")
        
        self.hosts_status_var = ctk.StringVar(value="未配置")
        ctk.CTkLabel(
            row1,
            textvariable=self.hosts_status_var,
            font=AppTheme.FONT_SMALL
        ).pack(side="left", padx=5)
        
        # 操作状态
        row2 = ctk.CTkFrame(left_col, fg_color="transparent")
        row2.pack(fill="x", pady=2)
        
        ctk.CTkLabel(row2, text="状态:", font=AppTheme.FONT_SMALL).pack(side="left")
        
        self.status_var = ctk.StringVar(value="就绪")
        self.status_label = ctk.CTkLabel(
            row2,
            textvariable=self.status_var,
            font=AppTheme.FONT_SMALL
        )
        self.status_label.pack(side="left", padx=5)
        
        # 右列：hosts 操作按钮
        right_col = ctk.CTkFrame(info_frame, fg_color="transparent")
        right_col.pack(side="right")
        
        ctk.CTkButton(
            right_col,
            text="📋 查看 hosts",
            width=100,
            height=28,
            font=AppTheme.FONT_SMALL,
            command=self._on_view_hosts
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            right_col,
            text="📝 打开 hosts",
            width=100,
            height=28,
            font=AppTheme.FONT_SMALL,
            fg_color="gray50",
            hover_color="gray40",
            command=self._on_open_hosts_file
        ).pack(side="left", padx=2)

    def _load_config_to_ui(self):
        """将配置加载到界面"""
        # 目标节点
        if self.config.target_nodes:
            self.target_node_combo.configure(values=self.config.target_nodes)
            if self.config.current_target_node:
                self.target_node_var.set(self.config.current_target_node)
            else:
                self.target_node_var.set(self.config.target_nodes[0])
        
        # CF 反代域名
        self.cf_domain_var.set(self.config.cf_proxy_domain)
        
        # IP 列表
        self._refresh_ip_list()
        
        # 更新 hosts 状态
        self._update_hosts_status()
    
    def _refresh_ip_list(self):
        """刷新 IP 列表显示"""
        # 清空现有卡片
        for card in self.ip_cards:
            card.destroy()
        self.ip_cards.clear()
        
        # 找出最佳 IP
        best_ip = None
        if self.test_results:
            results = list(self.test_results.values())
            best_result = SpeedTester.get_best_ip(results)
            if best_result:
                best_ip = best_result.ip_entry.ip
        
        # 创建 IP 卡片
        for ip_entry in self.config.ip_list:
            result = self.test_results.get(ip_entry.ip)
            is_best = (ip_entry.ip == best_ip)
            
            card = IPCard(
                self.ip_scroll_frame,
                ip_entry=ip_entry,
                result=result,
                is_best=is_best,
                on_select=self._on_card_select
            )
            card.pack(fill="x", pady=3, padx=5)
            self.ip_cards.append(card)
        
        # 如果没有 IP，显示提示
        if not self.ip_cards:
            placeholder = ctk.CTkLabel(
                self.ip_scroll_frame,
                text="暂无 IP 地址，请添加",
                text_color="gray50",
                font=AppTheme.FONT_DEFAULT
            )
            placeholder.pack(pady=20)
    
    def _on_card_select(self, card: IPCard, shift_held: bool = False):
        """卡片选中回调
        
        Args:
            card: 被点击的卡片
            shift_held: 是否按住了 Shift 键
        """
        if shift_held and hasattr(self, '_last_selected_card') and self._last_selected_card:
            # Shift+点击：批量选中从上次选中到当前的所有卡片
            self._select_range(self._last_selected_card, card)
        else:
            # 普通点击：记录当前卡片为最后选中
            self._last_selected_card = card
    
    def _select_range(self, start_card: IPCard, end_card: IPCard):
        """选中从 start_card 到 end_card 之间的所有卡片
        
        Args:
            start_card: 起始卡片
            end_card: 结束卡片
        """
        try:
            start_idx = self.ip_cards.index(start_card)
            end_idx = self.ip_cards.index(end_card)
        except ValueError:
            return
        
        # 确保 start_idx <= end_idx
        if start_idx > end_idx:
            start_idx, end_idx = end_idx, start_idx
        
        # 选中范围内的所有卡片
        for i in range(start_idx, end_idx + 1):
            self.ip_cards[i].set_selected(True)
    
    def _get_selected_cards(self) -> List[IPCard]:
        """获取选中的卡片"""
        return [card for card in self.ip_cards if card.is_selected]
    
    def _update_hosts_status(self):
        """更新 hosts 状态显示"""
        cf_domain = URLParser.extract_domain(self.cf_domain_var.get())
        if cf_domain:
            entry = self.hosts_manager.get_entry(cf_domain)
            if entry:
                self.hosts_status_var.set(f"{cf_domain} -> {entry[0]}")
            else:
                self.hosts_status_var.set(f"{cf_domain}: 未配置")
        else:
            self.hosts_status_var.set("未配置")
    
    def _update_full_proxy_url(self):
        """更新完整代理地址显示"""
        cf_input = self.cf_domain_var.get().strip()
        target = self.target_node_var.get().strip()
        
        if not cf_input:
            self.full_proxy_url_var.set("")
            return
        
        # 解析输入
        config = URLParser.parse_proxy_url(cf_input)
        if config:
            cf_domain = config.cf_domain
            if config.target_node:
                target = config.target_node
        else:
            cf_domain = cf_input
        
        full_url = URLParser.build_proxy_url(cf_domain, target)
        self.full_proxy_url_var.set(full_url)
    
    def _save_config(self):
        """保存配置"""
        self.config.current_target_node = self.target_node_var.get()
        self.config.cf_proxy_domain = self.cf_domain_var.get()
        self.config_manager.save(self.config)
    
    # 事件处理
    def _on_target_node_changed(self, value=None):
        """目标节点改变"""
        self._update_full_proxy_url()
        self._save_config()
    
    def _on_add_target_node(self):
        """添加目标节点
        
        支持添加完整 URL（如 https://anyrouter.top）或纯域名（如 anyrouter.top）
        """
        node = self.target_node_var.get().strip()
        if not node:
            return
        
        if node not in self.config.target_nodes:
            self.config.target_nodes.append(node)
            self.target_node_combo.configure(values=self.config.target_nodes)
            # 切换到新添加的节点
            self.target_node_var.set(node)
            self._update_full_proxy_url()
            self._save_config()
            self.status_var.set(f"已添加节点: {node}")
        else:
            self.status_var.set(f"节点已存在: {node}")
    
    def _on_delete_target_node(self):
        """删除目标节点"""
        node = self.target_node_var.get().strip()
        if node in self.config.target_nodes:
            self.config.target_nodes.remove(node)
            self.target_node_combo.configure(values=self.config.target_nodes)
            if self.config.target_nodes:
                self.target_node_var.set(self.config.target_nodes[0])
            else:
                self.target_node_var.set("")
            self._save_config()
            self.status_var.set(f"已删除节点: {node}")
    
    def _on_cf_domain_changed(self, *args):
        """CF 反代域名改变"""
        self._update_full_proxy_url()
        self._update_hosts_status()
        self.after(500, self._save_config)
    
    def _on_add_ip(self):
        """添加 IP"""
        ip_text = self.add_ip_var.get().strip()
        if not ip_text:
            return
        
        entries = IPParser.parse_multiple(ip_text)
        if not entries:
            messagebox.showerror("错误", "无效的 IP 格式")
            return
        
        added = 0
        for entry in entries:
            exists = any(e.ip == entry.ip for e in self.config.ip_list)
            if not exists:
                self.config.ip_list.append(entry)
                added += 1
        
        if added > 0:
            self._refresh_ip_list()
            self._save_config()
            self.add_ip_var.set("")
            self.status_var.set(f"已添加 {added} 个 IP")
        else:
            self.status_var.set("IP 已存在")
    
    def _on_delete_ip(self):
        """删除选中的 IP"""
        selected = self._get_selected_cards()
        if not selected:
            messagebox.showinfo("提示", "请先选中要删除的 IP")
            return
        
        for card in selected:
            ip = card.ip_entry.ip
            self.config.ip_list = [e for e in self.config.ip_list if e.ip != ip]
            if ip in self.test_results:
                del self.test_results[ip]
        
        self._refresh_ip_list()
        self._save_config()
        self.status_var.set(f"已删除 {len(selected)} 个 IP")

    def _on_test_speed(self):
        """开始测速"""
        if not self.config.ip_list:
            messagebox.showinfo("提示", "没有可测试的 IP")
            return
        
        if self.is_testing:
            return
        
        self.is_testing = True
        self.test_btn.configure(state="disabled", text="测速中...")
        self.status_var.set("正在测速...")
        self.test_results.clear()
        
        def test_thread():
            def callback(current, total, result):
                self.test_results[result.ip_entry.ip] = result
                self.after(0, lambda: self._on_test_progress(current, total, result))
            
            self.speed_tester.test_all(self.config.ip_list, callback)
            self.after(0, self._on_test_complete)
        
        threading.Thread(target=test_thread, daemon=True).start()
    
    def _on_test_progress(self, current, total, result):
        """测速进度更新"""
        self.status_var.set(f"测速中... {current}/{total}")
        self._refresh_ip_list()
    
    def _on_test_complete(self):
        """测速完成，自动应用最佳 IP"""
        logger.info("测速完成回调开始")
        self.is_testing = False
        self.test_btn.configure(state="normal", text="🚀 开始测速")
        
        # 排序结果
        results = list(self.test_results.values())
        sorted_results = SpeedTester.sort_results(results)
        
        # 重新排序 IP 列表
        ip_order = {r.ip_entry.ip: i for i, r in enumerate(sorted_results)}
        self.config.ip_list.sort(key=lambda e: ip_order.get(e.ip, 999))
        
        self._refresh_ip_list()
        
        best = SpeedTester.get_best_ip(results)
        if best:
            # 自动应用最佳 IP
            cf_domain_input = self.cf_domain_var.get()
            logger.debug(f"CF 域名输入: '{cf_domain_input}'")
            cf_domain = URLParser.extract_domain(cf_domain_input)
            logger.debug(f"提取的域名: '{cf_domain}'")
            
            if cf_domain:
                logger.info(f"自动应用最佳 IP: {cf_domain} -> {best.ip_entry.ip}")
                self.hosts_manager.backup()
                success = self.hosts_manager.update_entry(cf_domain, best.ip_entry.ip)
                
                if success:
                    self.hosts_manager.flush_dns()
                    self._update_hosts_status()
                    self.config.selected_ip = best.ip_entry.ip
                    self._save_config()
                    status_msg = f"已应用最佳 IP: {best.ip_entry.ip} ({best.latency_ms:.2f}ms)"
                else:
                    status_msg = f"测速完成，最佳 IP: {best.ip_entry.ip} ({best.latency_ms:.2f}ms)，应用失败"
                    logger.warning(f"应用失败: {cf_domain} -> {best.ip_entry.ip}")
            else:
                status_msg = f"测速完成，最佳 IP: {best.ip_entry.ip} ({best.latency_ms:.2f}ms)"
                logger.warning("未配置 CF 域名，跳过自动应用")
            
            logger.info(status_msg)
            self.status_var.set(status_msg)
        else:
            status_msg = "测速完成，所有 IP 均不可用"
            logger.warning(status_msg)
            self.status_var.set(status_msg)
    
    def _on_apply_selected_ip(self):
        """应用选中的 IP"""
        cf_domain = URLParser.extract_domain(self.cf_domain_var.get())
        if not cf_domain:
            messagebox.showerror("错误", "请先配置 CF 反代域名")
            return
        
        selected = self._get_selected_cards()
        if not selected:
            messagebox.showinfo("提示", "请先选中要应用的 IP")
            return
        
        if len(selected) > 1:
            messagebox.showinfo("提示", "只能选中一个 IP 进行应用")
            return
        
        selected_card = selected[0]
        selected_ip = selected_card.ip_entry.ip
        
        # 备份
        backup_path = self.hosts_manager.backup()
        if backup_path:
            self.status_var.set("已备份 hosts 文件")
        
        # 更新 hosts
        success = self.hosts_manager.update_entry(cf_domain, selected_ip)
        
        if success:
            self.hosts_manager.flush_dns()
            self._update_hosts_status()
            self.config.selected_ip = selected_ip
            self._save_config()
            
            # 显示延迟信息（如果有测试结果）
            result = self.test_results.get(selected_card.ip_entry)
            if result and result.latency_ms is not None:
                self.status_var.set(f"已应用 IP: {selected_ip} ({result.latency_ms:.2f}ms)")
                messagebox.showinfo("成功", f"已将 {cf_domain} 指向 {selected_ip}\n延迟: {result.latency_ms:.2f}ms")
            else:
                self.status_var.set(f"已应用 IP: {selected_ip}")
                messagebox.showinfo("成功", f"已将 {cf_domain} 指向 {selected_ip}")
        else:
            messagebox.showerror("错误", "修改 hosts 文件失败，请以管理员身份运行")
    
    def _on_apply_best_ip(self):
        """应用最佳 IP"""
        cf_domain = URLParser.extract_domain(self.cf_domain_var.get())
        if not cf_domain:
            messagebox.showerror("错误", "请先配置 CF 反代域名")
            return
        
        results = list(self.test_results.values())
        best = SpeedTester.get_best_ip(results)
        
        if not best:
            messagebox.showerror("错误", "没有可用的 IP，请先测速")
            return
        
        # 备份
        backup_path = self.hosts_manager.backup()
        if backup_path:
            self.status_var.set("已备份 hosts 文件")
        
        # 更新 hosts
        success = self.hosts_manager.update_entry(cf_domain, best.ip_entry.ip)
        
        if success:
            self.hosts_manager.flush_dns()
            self._update_hosts_status()
            self.config.selected_ip = best.ip_entry.ip
            self._save_config()
            self.status_var.set(f"已应用最佳 IP: {best.ip_entry.ip}")
            messagebox.showinfo("成功", f"已将 {cf_domain} 指向 {best.ip_entry.ip}")
        else:
            messagebox.showerror("错误", "修改 hosts 文件失败，请以管理员身份运行")
    
    def _on_clear_hosts(self):
        """清除 hosts 配置"""
        cf_domain = URLParser.extract_domain(self.cf_domain_var.get())
        if not cf_domain:
            messagebox.showinfo("提示", "请先配置 CF 反代域名")
            return
        
        if not messagebox.askyesno("确认", f"确定要删除 {cf_domain} 的 hosts 配置吗？"):
            return
        
        self.hosts_manager.backup()
        success = self.hosts_manager.remove_entry(cf_domain)
        
        if success:
            self.hosts_manager.flush_dns()
            self._update_hosts_status()
            self.config.selected_ip = None
            self._save_config()
            self.status_var.set(f"已清除 {cf_domain} 的 hosts 配置")
        else:
            messagebox.showerror("错误", "修改 hosts 文件失败，请以管理员身份运行")
    
    def _on_view_hosts(self):
        """打开 Hosts 查看器"""
        from .hosts_viewer import HostsViewer
        
        def on_viewer_close():
            self._update_hosts_status()
        
        viewer = HostsViewer(
            self,
            self.hosts_manager,
            on_close=on_viewer_close
        )
        viewer.show()
    
    def _on_open_hosts_file(self):
        """用系统默认编辑器打开 hosts 文件"""
        import os
        import subprocess
        
        hosts_path = self.hosts_manager.hosts_path
        logger.info(f"打开 hosts 文件: {hosts_path}")
        
        try:
            # Windows: 使用 notepad 打开（需要管理员权限才能编辑）
            if os.name == 'nt':
                # 尝试用记事本打开
                subprocess.Popen(['notepad.exe', hosts_path])
                self.status_var.set(f"已打开 hosts 文件")
            else:
                # 其他系统使用默认编辑器
                os.startfile(hosts_path)
                self.status_var.set(f"已打开 hosts 文件")
        except Exception as e:
            logger.error(f"打开 hosts 文件失败: {e}")
            messagebox.showerror("错误", f"无法打开 hosts 文件:\n{e}")
    
    def _show_import_dialog(self):
        """显示 V2Ray 订阅导入对话框"""
        from cf_proxy_manager.components.import_dialog import ImportDialog
        
        dialog = ImportDialog(self, on_import=self._on_import_ips)
        dialog.focus()
    
    def _on_import_ips(self, ips: list[str]):
        """处理导入的 IP 列表
        
        Args:
            ips: 要导入的 IP 地址列表
        """
        added = 0
        skipped = 0
        
        for ip in ips:
            # 检查是否已存在
            exists = any(e.ip == ip for e in self.config.ip_list)
            if not exists:
                # 创建 IPEntry 并添加
                entry = IPEntry(ip=ip, port=443)  # 默认端口 443
                self.config.ip_list.append(entry)
                added += 1
            else:
                skipped += 1
        
        if added > 0:
            self._refresh_ip_list()
            self._save_config()
        
        status_msg = f"导入完成: 新增 {added} 个"
        if skipped > 0:
            status_msg += f", 跳过 {skipped} 个重复"
        
        self.status_var.set(status_msg)
        logger.info(f"IP 导入完成: 新增 {added}, 跳过 {skipped}")
    
    def _on_theme_changed(self, value):
        """主题切换"""
        theme_map = {
            "深色": "dark",
            "浅色": "light",
            "跟随系统": "system"
        }
        mode = theme_map.get(value, "system")
        ctk.set_appearance_mode(mode)
        
        # 保存主题设置
        self.config.theme_mode = mode
        self._save_config()
        self.status_var.set(f"已切换到{value}主题")
    
    def run(self):
        """运行主循环"""
        self.mainloop()
    
    def _get_version(self) -> str:
        """获取版本号"""
        from . import __version__
        return __version__
