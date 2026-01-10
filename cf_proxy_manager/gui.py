"""
CF Proxy Manager - GUI
图形用户界面
"""
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from typing import Optional

from .models import Config, IPEntry, DEFAULT_IPS, DEFAULT_TARGET_NODE
from .config_manager import ConfigManager
from .parsers import URLParser, IPParser
from .speed_tester import SpeedTester
from .hosts_manager import HostsManager
from .admin_helper import AdminHelper


class CFProxyManagerGUI:
    """CF Proxy Manager 主界面"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🐯 虎哥API反代")
        self.root.geometry("600x650")
        self.root.resizable(True, True)
        
        # 初始化组件
        self.config_manager = ConfigManager()
        self.speed_tester = SpeedTester(timeout=3.0)
        self.hosts_manager = HostsManager()
        
        # 加载配置
        self.config = self.config_manager.load()
        
        # 测试结果缓存
        self.test_results = {}
        
        # 创建界面
        self._create_widgets()
        self._load_config_to_ui()
    
    def _create_widgets(self):
        """创建所有界面组件"""
        # 主容器
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 1. 目标反代节点区域
        self._create_target_node_section(main_frame)
        
        # 2. CF 反代配置区域
        self._create_cf_proxy_section(main_frame)
        
        # 3. 优选 IP 管理区域
        self._create_ip_management_section(main_frame)
        
        # 4. 状态显示区域
        self._create_status_section(main_frame)
    
    def _create_target_node_section(self, parent):
        """创建目标反代节点区域"""
        frame = ttk.LabelFrame(parent, text="目标反代节点", padding="5")
        frame.pack(fill=tk.X, pady=(0, 10))
        
        # 当前节点选择
        row1 = ttk.Frame(frame)
        row1.pack(fill=tk.X, pady=2)
        
        ttk.Label(row1, text="当前节点:").pack(side=tk.LEFT)
        
        self.target_node_var = tk.StringVar()
        self.target_node_combo = ttk.Combobox(
            row1, 
            textvariable=self.target_node_var,
            width=40
        )
        self.target_node_combo.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.target_node_combo.bind('<<ComboboxSelected>>', self._on_target_node_changed)
        self.target_node_combo.bind('<Return>', self._on_add_target_node)
        
        ttk.Button(row1, text="添加", command=self._on_add_target_node).pack(side=tk.LEFT)
        ttk.Button(row1, text="删除", command=self._on_delete_target_node).pack(side=tk.LEFT, padx=2)
    
    def _create_cf_proxy_section(self, parent):
        """创建 CF 反代配置区域"""
        frame = ttk.LabelFrame(parent, text="CF 反代配置", padding="5")
        frame.pack(fill=tk.X, pady=(0, 10))
        
        # 反代域名输入
        row1 = ttk.Frame(frame)
        row1.pack(fill=tk.X, pady=2)
        
        ttk.Label(row1, text="反代域名/URL:").pack(side=tk.LEFT)
        
        self.cf_domain_var = tk.StringVar()
        self.cf_domain_entry = ttk.Entry(row1, textvariable=self.cf_domain_var, width=45)
        self.cf_domain_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.cf_domain_var.trace_add('write', self._on_cf_domain_changed)
        
        # 完整代理地址显示
        row2 = ttk.Frame(frame)
        row2.pack(fill=tk.X, pady=2)
        
        ttk.Label(row2, text="完整代理地址:").pack(side=tk.LEFT)
        
        self.full_proxy_url_var = tk.StringVar()
        self.full_proxy_url_label = ttk.Label(
            row2, 
            textvariable=self.full_proxy_url_var,
            foreground="blue"
        )
        self.full_proxy_url_label.pack(side=tk.LEFT, padx=5)
    
    def _create_ip_management_section(self, parent):
        """创建优选 IP 管理区域"""
        frame = ttk.LabelFrame(parent, text="优选 IP 管理", padding="5")
        frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # IP 列表
        list_frame = ttk.Frame(frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Treeview
        columns = ("ip", "latency", "status")
        self.ip_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=8)
        
        self.ip_tree.heading("ip", text="IP")
        self.ip_tree.heading("latency", text="延迟")
        self.ip_tree.heading("status", text="状态")
        
        self.ip_tree.column("ip", width=200)
        self.ip_tree.column("latency", width=100)
        self.ip_tree.column("status", width=100)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.ip_tree.yview)
        self.ip_tree.configure(yscrollcommand=scrollbar.set)
        
        self.ip_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 添加 IP 输入
        add_frame = ttk.Frame(frame)
        add_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(add_frame, text="添加 IP:").pack(side=tk.LEFT)
        
        self.add_ip_var = tk.StringVar()
        self.add_ip_entry = ttk.Entry(add_frame, textvariable=self.add_ip_var, width=35)
        self.add_ip_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.add_ip_entry.bind('<Return>', lambda e: self._on_add_ip())
        
        ttk.Button(add_frame, text="添加", command=self._on_add_ip).pack(side=tk.LEFT)
        
        # 操作按钮
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="开始测速", command=self._on_test_speed).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="应用最佳 IP", command=self._on_apply_best_ip).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="删除选中", command=self._on_delete_ip).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="清除hosts", command=self._on_clear_hosts).pack(side=tk.LEFT, padx=2)
    
    def _create_status_section(self, parent):
        """创建状态显示区域"""
        frame = ttk.LabelFrame(parent, text="状态", padding="5")
        frame.pack(fill=tk.X)
        
        # 权限状态
        row0 = ttk.Frame(frame)
        row0.pack(fill=tk.X, pady=2)
        
        ttk.Label(row0, text="权限状态:").pack(side=tk.LEFT)
        
        self.admin_status_var = tk.StringVar(value=AdminHelper.get_status_text())
        self.admin_status_label = tk.Label(
            row0, 
            textvariable=self.admin_status_var,
            fg=AdminHelper.get_status_color(),
            font=("Segoe UI", 9)
        )
        self.admin_status_label.pack(side=tk.LEFT, padx=5)
        
        # 查看 hosts 按钮
        ttk.Button(
            row0, 
            text="📋 查看 hosts", 
            command=self._on_view_hosts
        ).pack(side=tk.RIGHT)
        
        # 当前 hosts 配置
        row1 = ttk.Frame(frame)
        row1.pack(fill=tk.X, pady=2)
        
        ttk.Label(row1, text="当前 hosts 配置:").pack(side=tk.LEFT)
        
        self.hosts_status_var = tk.StringVar(value="未配置")
        ttk.Label(row1, textvariable=self.hosts_status_var).pack(side=tk.LEFT, padx=5)
        
        # 操作状态
        row2 = ttk.Frame(frame)
        row2.pack(fill=tk.X, pady=2)
        
        ttk.Label(row2, text="状态:").pack(side=tk.LEFT)
        
        self.status_var = tk.StringVar(value="就绪")
        self.status_label = ttk.Label(row2, textvariable=self.status_var)
        self.status_label.pack(side=tk.LEFT, padx=5)
    
    def _load_config_to_ui(self):
        """将配置加载到界面"""
        # 目标节点
        self.target_node_combo['values'] = self.config.target_nodes
        if self.config.current_target_node:
            self.target_node_var.set(self.config.current_target_node)
        elif self.config.target_nodes:
            self.target_node_var.set(self.config.target_nodes[0])
        
        # CF 反代域名
        self.cf_domain_var.set(self.config.cf_proxy_domain)
        
        # IP 列表
        self._refresh_ip_list()
        
        # 更新 hosts 状态
        self._update_hosts_status()
    
    def _refresh_ip_list(self):
        """刷新 IP 列表显示"""
        # 清空列表
        for item in self.ip_tree.get_children():
            self.ip_tree.delete(item)
        
        # 添加 IP
        for ip_entry in self.config.ip_list:
            ip_str = f"{ip_entry.ip}:{ip_entry.port}"
            
            # 获取测试结果
            result = self.test_results.get(ip_entry.ip)
            if result:
                latency = f"{result.latency_ms}ms" if result.success else "--"
                status = "✓" if result.success else "✗"
            else:
                latency = "--"
                status = "待测试"
            
            self.ip_tree.insert("", tk.END, values=(ip_str, latency, status))
    
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
            # 如果输入已包含目标节点，使用它
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
    def _on_target_node_changed(self, event=None):
        """目标节点改变"""
        self._update_full_proxy_url()
        self._save_config()
    
    def _on_add_target_node(self, event=None):
        """添加目标节点"""
        node = self.target_node_var.get().strip()
        if not node:
            return
        
        if node not in self.config.target_nodes:
            self.config.target_nodes.append(node)
            self.target_node_combo['values'] = self.config.target_nodes
            self._save_config()
            self.status_var.set(f"已添加节点: {node}")
    
    def _on_delete_target_node(self):
        """删除目标节点"""
        node = self.target_node_var.get().strip()
        if node in self.config.target_nodes:
            self.config.target_nodes.remove(node)
            self.target_node_combo['values'] = self.config.target_nodes
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
        # 延迟保存
        self.root.after(500, self._save_config)
    
    def _on_add_ip(self):
        """添加 IP"""
        ip_text = self.add_ip_var.get().strip()
        if not ip_text:
            return
        
        # 解析 IP
        entries = IPParser.parse_multiple(ip_text)
        if not entries:
            messagebox.showerror("错误", "无效的 IP 格式")
            return
        
        added = 0
        for entry in entries:
            # 检查是否已存在
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
        selection = self.ip_tree.selection()
        if not selection:
            return
        
        for item in selection:
            values = self.ip_tree.item(item, 'values')
            ip_str = values[0]
            ip = ip_str.split(':')[0]
            
            # 从配置中删除
            self.config.ip_list = [e for e in self.config.ip_list if e.ip != ip]
            
            # 从测试结果中删除
            if ip in self.test_results:
                del self.test_results[ip]
        
        self._refresh_ip_list()
        self._save_config()
        self.status_var.set("已删除选中的 IP")
    
    def _on_test_speed(self):
        """开始测速"""
        if not self.config.ip_list:
            messagebox.showinfo("提示", "没有可测试的 IP")
            return
        
        self.status_var.set("正在测速...")
        self.test_results.clear()
        
        def test_thread():
            def callback(current, total, result):
                self.test_results[result.ip_entry.ip] = result
                self.root.after(0, lambda: self._on_test_progress(current, total, result))
            
            self.speed_tester.test_all(self.config.ip_list, callback)
            self.root.after(0, self._on_test_complete)
        
        threading.Thread(target=test_thread, daemon=True).start()
    
    def _on_test_progress(self, current, total, result):
        """测速进度更新"""
        self.status_var.set(f"测速中... {current}/{total}")
        self._refresh_ip_list()
    
    def _on_test_complete(self):
        """测速完成"""
        # 排序结果
        results = list(self.test_results.values())
        sorted_results = SpeedTester.sort_results(results)
        
        # 重新排序 IP 列表
        ip_order = {r.ip_entry.ip: i for i, r in enumerate(sorted_results)}
        self.config.ip_list.sort(key=lambda e: ip_order.get(e.ip, 999))
        
        self._refresh_ip_list()
        
        best = SpeedTester.get_best_ip(results)
        if best:
            self.status_var.set(f"测速完成，最佳 IP: {best.ip_entry.ip} ({best.latency_ms}ms)")
        else:
            self.status_var.set("测速完成，所有 IP 均不可用")
    
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
            self.status_var.set(f"已备份 hosts 文件")
        
        # 更新 hosts
        success = self.hosts_manager.update_entry(cf_domain, best.ip_entry.ip)
        
        if success:
            # 刷新 DNS
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
        
        # 确认
        if not messagebox.askyesno("确认", f"确定要删除 {cf_domain} 的 hosts 配置吗？"):
            return
        
        # 备份
        self.hosts_manager.backup()
        
        # 删除条目
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
            """查看器关闭回调"""
            self._update_hosts_status()
        
        viewer = HostsViewer(
            self.root, 
            self.hosts_manager,
            on_close=on_viewer_close
        )
        viewer.show()
    
    def run(self):
        """运行主循环"""
        self.root.mainloop()
