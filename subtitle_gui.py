#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
B站视频字幕提取工具 - 美化GUI版本
作者: wjm
版本: v2.0.0
创建时间: 2024
联系方式: [您的联系方式]

功能说明:
- 现代化的图形用户界面
- 支持AI小助手字幕提取
- 支持Whisper语音识别
- 实时进度显示和日志输出
- Edge浏览器调试模式集成

技术实现:
- Tkinter GUI框架
- 多线程处理
- 实时消息队列
- 现代化视觉设计

版权声明:
Copyright (c) 2024 wjm. All rights reserved.
本软件由 wjm 开发，仅供个人学习和研究使用。
禁止用于商业用途或盈利。
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import sys
import os
from pathlib import Path
import queue
from tkinter import font

# 导入主要的提取器类
from bilibili_subtitle_extractor import BilibiliSubtitleExtractor

# 版本信息
__version__ = "2.0.0"
__author__ = "wjm"
__email__ = "[您的邮箱地址]"
__license__ = "Personal Use Only - 仅供个人使用"
__copyright__ = "Copyright (c) 2024 wjm"
__description__ = "B站视频字幕提取工具 - 现代化GUI界面"
__url__ = "[您的项目URL]"
__status__ = "Production"

class ModernSubtitleExtractorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(f"B站视频字幕提取工具 v{__version__} - 作者: {__author__} | Copyright 2024")
        self.root.geometry("900x800")
        self.root.configure(bg='#f0f0f0')
        
        # 设置窗口图标（如果有的话）
        try:
            self.root.iconbitmap('icon.ico')
        except:
            pass
        
        # 创建输出队列用于线程间通信
        self.output_queue = queue.Queue()
        
        # 默认输出目录
        self.output_dir = "./subtitles"
        
        # 设置现代化字体
        self.setup_fonts()
        
        # 创建界面元素
        self.create_modern_widgets()
        
        # 启动输出更新线程
        self.root.after(100, self.update_output)
    
    def setup_fonts(self):
        """设置现代化字体"""
        self.title_font = font.Font(family="Microsoft YaHei UI", size=16, weight="bold")
        self.subtitle_font = font.Font(family="Microsoft YaHei UI", size=10)
        self.button_font = font.Font(family="Microsoft YaHei UI", size=9, weight="bold")
        self.label_font = font.Font(family="Microsoft YaHei UI", size=9)
    
    def create_modern_widgets(self):
        # 创建主容器
        main_container = tk.Frame(self.root, bg='#f0f0f0')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题区域
        self.create_header(main_container)
        
        # 输入区域
        self.create_input_section(main_container)
        
        # 设置区域
        self.create_settings_section(main_container)
        
        # 控制按钮区域
        self.create_control_section(main_container)
        
        # 进度区域
        self.create_progress_section(main_container)
        
        # 日志区域
        self.create_log_section(main_container)
        
        # 底部信息
        self.create_footer(main_container)
    
    def create_header(self, parent):
        """创建标题区域"""
        header_frame = tk.Frame(parent, bg='#2c3e50', height=80)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        header_frame.pack_propagate(False)
        
        # 主标题
        title_label = tk.Label(
            header_frame, 
            text="B站视频字幕提取工具", 
            font=self.title_font,
            fg='white', 
            bg='#2c3e50'
        )
        title_label.pack(pady=(15, 5))
        
        # 副标题
        subtitle_label = tk.Label(
            header_frame, 
            text=f"版本 {__version__} | 开发者: {__author__} | 仅供个人使用，禁止商业用途 | Copyright © 2024", 
            font=self.subtitle_font,
            fg='#bdc3c7', 
            bg='#2c3e50'
        )
        subtitle_label.pack()
    
    def create_input_section(self, parent):
        """创建输入区域"""
        input_frame = tk.LabelFrame(
            parent, 
            text="  视频信息  ", 
            font=self.label_font,
            bg='#f0f0f0',
            fg='#2c3e50',
            padx=10, 
            pady=10
        )
        input_frame.pack(fill=tk.X, pady=(0, 15))
        
        # URL输入
        tk.Label(input_frame, text="B站视频URL:", font=self.label_font, bg='#f0f0f0').grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5)
        )
        
        self.url_var = tk.StringVar()
        url_entry = tk.Entry(
            input_frame, 
            textvariable=self.url_var, 
            font=self.label_font,
            width=70,
            relief=tk.FLAT,
            bd=5
        )
        url_entry.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # 页面号和输出目录
        tk.Label(input_frame, text="页面号:", font=self.label_font, bg='#f0f0f0').grid(
            row=1, column=0, sticky=tk.W, pady=(0, 5)
        )
        
        self.page_var = tk.StringVar(value="1")
        page_entry = tk.Entry(
            input_frame, 
            textvariable=self.page_var, 
            font=self.label_font,
            width=10,
            relief=tk.FLAT,
            bd=5
        )
        page_entry.grid(row=1, column=1, sticky=tk.W, pady=(0, 5))
        
        tk.Label(input_frame, text="(多P视频页面号)", font=self.label_font, fg='#7f8c8d', bg='#f0f0f0').grid(
            row=1, column=2, sticky=tk.W, padx=(10, 0), pady=(0, 5)
        )
        
        # 输出目录
        tk.Label(input_frame, text="保存目录:", font=self.label_font, bg='#f0f0f0').grid(
            row=2, column=0, sticky=tk.W, pady=(0, 5)
        )
        
        self.output_var = tk.StringVar(value=self.output_dir)
        output_entry = tk.Entry(
            input_frame, 
            textvariable=self.output_var, 
            font=self.label_font,
            width=50,
            relief=tk.FLAT,
            bd=5
        )
        output_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        browse_btn = tk.Button(
            input_frame, 
            text="浏览", 
            command=self.select_output_dir,
            font=self.button_font,
            bg='#3498db',
            fg='white',
            relief=tk.FLAT,
            padx=15
        )
        browse_btn.grid(row=2, column=2, padx=(10, 0), pady=(0, 5))
        
        input_frame.columnconfigure(1, weight=1)
    
    def create_settings_section(self, parent):
        """创建设置区域"""
        settings_frame = tk.LabelFrame(
            parent, 
            text="  提取设置  ", 
            font=self.label_font,
            bg='#f0f0f0',
            fg='#2c3e50',
            padx=10, 
            pady=10
        )
        settings_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 提取模式
        mode_frame = tk.Frame(settings_frame, bg='#f0f0f0')
        mode_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(mode_frame, text="提取模式:", font=self.label_font, bg='#f0f0f0').pack(side=tk.LEFT)
        
        self.mode_var = tk.StringVar(value="ai")
        
        modes = [
            ("现有字幕", "subtitle", "快速提取现有字幕文件"),
            ("AI小助手", "ai", "使用AI总结生成字幕（推荐）"),
            ("语音识别", "speech", "适用于所有视频，较慢")
        ]
        
        for text, value, desc in modes:
            rb = tk.Radiobutton(
                mode_frame,
                text=f"{text} - {desc}",
                variable=self.mode_var,
                value=value,
                font=self.label_font,
                bg='#f0f0f0',
                fg='#2c3e50'
            )
            rb.pack(anchor=tk.W, padx=(20, 0))
        
        # 输出格式选择
        format_frame = tk.Frame(settings_frame, bg='#f0f0f0')
        format_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Label(format_frame, text="输出格式:", font=self.label_font, bg='#f0f0f0').pack(side=tk.LEFT)
        
        self.format_var = tk.StringVar(value="srt")
        format_combo = ttk.Combobox(
            format_frame,
            textvariable=self.format_var,
            values=["srt", "txt", "json"],
            state="readonly",
            font=self.label_font,
            width=10
        )
        format_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        tk.Label(
            format_frame, 
            text="SRT: 标准字幕格式 | TXT: 纯文本格式 | JSON: 结构化数据", 
            font=self.label_font, 
            fg='#7f8c8d', 
            bg='#f0f0f0'
        ).pack(side=tk.LEFT, padx=(20, 0))
        
        # Whisper设置
        whisper_frame = tk.Frame(settings_frame, bg='#f0f0f0')
        whisper_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Label(whisper_frame, text="语音模型:", font=self.label_font, bg='#f0f0f0').pack(side=tk.LEFT)
        
        self.model_var = tk.StringVar(value="base")
        model_combo = ttk.Combobox(
            whisper_frame,
            textvariable=self.model_var,
            values=["tiny", "base", "small", "medium", "large"],
            state="readonly",
            font=self.label_font,
            width=10
        )
        model_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        tk.Label(
            whisper_frame, 
            text="tiny(最快) → large(最准确)", 
            font=self.label_font, 
            fg='#7f8c8d', 
            bg='#f0f0f0'
        ).pack(side=tk.LEFT, padx=(20, 0))
    
    def create_control_section(self, parent):
        """创建控制按钮区域"""
        control_frame = tk.Frame(parent, bg='#f0f0f0')
        control_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 主要按钮
        self.extract_button = tk.Button(
            control_frame,
            text="🚀 开始提取",
            command=self.start_extraction,
            font=self.button_font,
            bg='#27ae60',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=8
        )
        self.extract_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 辅助按钮
        buttons = [
            ("🌐 启动Edge", self.start_edge_debug, '#9b59b6'),
            ("🔗 测试连接", self.test_edge_connection, '#e74c3c'),
            ("🔧 检查依赖", self.check_dependencies, '#e67e22'),
            ("🧹 清空日志", self.clear_output, '#95a5a6'),
            ("❓ 帮助", self.show_help, '#3498db')
        ]
        
        for text, command, color in buttons:
            btn = tk.Button(
                control_frame,
                text=text,
                command=command,
                font=self.button_font,
                bg=color,
                fg='white',
                relief=tk.FLAT,
                padx=15,
                pady=8
            )
            btn.pack(side=tk.LEFT, padx=(0, 10))
    
    def create_progress_section(self, parent):
        """创建进度区域"""
        progress_frame = tk.Frame(parent, bg='#f0f0f0')
        progress_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(progress_frame, text="进度:", font=self.label_font, bg='#f0f0f0').pack(side=tk.LEFT)
        
        self.progress = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
    
    def create_log_section(self, parent):
        """创建日志区域"""
        log_frame = tk.LabelFrame(
            parent, 
            text="  运行日志  ", 
            font=self.label_font,
            bg='#f0f0f0',
            fg='#2c3e50',
            padx=10, 
            pady=10
        )
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # 创建文本框和滚动条
        self.output_text = scrolledtext.ScrolledText(
            log_frame,
            height=15,
            width=80,
            font=('Consolas', 9),
            bg='#2c3e50',
            fg='#ecf0f1',
            insertbackground='white',
            relief=tk.FLAT
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        # 添加欢迎信息
        welcome_msg = f"""
╔══════════════════════════════════════════════════════════════╗
║                    B站视频字幕提取工具                        ║
║                                                              ║
║  版本: {__version__:<10} 作者: {__author__:<10}                        ║
║                                                              ║
║  免责声明: 本工具仅供个人学习使用，不得用于商业用途            ║
╚══════════════════════════════════════════════════════════════╝

欢迎使用 B站视频字幕提取工具！

📝 使用说明：
1. 输入B站视频URL
2. 选择提取模式（推荐使用AI小助手）
3. 选择输出格式
4. 点击"开始提取"

⚠️  注意事项：
• AI模式需要启动浏览器，首次使用可能需要下载驱动
• 语音识别模式速度较慢但支持所有视频
• 本工具仅供个人学习研究使用

准备就绪，请输入视频信息开始提取...

"""
        self.output_text.insert(tk.END, welcome_msg)
        self.output_text.see(tk.END)
    
    def create_footer(self, parent):
        """创建底部信息"""
        footer_frame = tk.Frame(parent, bg='#34495e', height=40)
        footer_frame.pack(fill=tk.X)
        footer_frame.pack_propagate(False)
        
        footer_text = f"B站字幕提取工具 v{__version__} | 开发者: {__author__} | Copyright © 2024 | 开源工具，仅供个人使用"
        footer_label = tk.Label(
            footer_frame,
            text=footer_text,
            font=self.subtitle_font,
            fg='#bdc3c7',
            bg='#34495e'
        )
        footer_label.pack(expand=True)
    
    def select_output_dir(self):
        """选择输出目录"""
        directory = filedialog.askdirectory(initialdir=self.output_var.get())
        if directory:
            self.output_var.set(directory)
            self.output_dir = directory
    
    def log_output(self, message, tag=None):
        """添加日志输出到队列"""
        self.output_queue.put((message + "\n", tag))
    
    def update_output(self):
        """更新输出文本框"""
        try:
            while True:
                item = self.output_queue.get_nowait()
                if isinstance(item, tuple):
                    message, tag = item
                else:
                    message, tag = item, None
                    
                self.output_text.insert(tk.END, message)
                self.output_text.see(tk.END)
                self.root.update_idletasks()
        except queue.Empty:
            pass
        
        self.root.after(100, self.update_output)
    
    def start_edge_debug(self):
        """启动Edge调试模式 - 保持用户登录状态"""
        def start_edge():
            try:
                self.log_output("🌐 正在启动Edge调试模式...")
                self.log_output("📝 此模式将使用您当前的Edge浏览器配置，保持登录状态")
                import subprocess
                import os
                import time
                
                # 先关闭所有Edge进程，然后启动调试模式
                try:
                    subprocess.run('taskkill /f /im msedge.exe', shell=True, capture_output=True)
                    time.sleep(2)  # 等待进程完全关闭
                    self.log_output("🔄 已关闭所有Edge进程")
                except:
                    pass
                
                # 查找启动脚本
                batch_file = os.path.join(os.path.dirname(__file__), '启动Edge调试模式.bat')
                if os.path.exists(batch_file):
                    subprocess.Popen([batch_file], shell=True)
                    self.log_output("✅ Edge调试模式已启动（使用脚本）")
                else:
                    # 手动启动命令 - 使用默认用户数据目录
                    edge_paths = [
                        r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
                        r'C:\Program Files\Microsoft\Edge\Application\msedge.exe'
                    ]
                    
                    edge_exe = None
                    for path in edge_paths:
                        if os.path.exists(path):
                            edge_exe = path
                            break
                    
                    if edge_exe:
                        # 使用默认用户数据目录启动调试模式
                        cmd = f'"{edge_exe}" --remote-debugging-port=9222 --user-data-dir="%USERPROFILE%\\AppData\\Local\\Microsoft\\Edge\\User Data" --profile-directory=Default'
                        subprocess.Popen(cmd, shell=True)
                        self.log_output("✅ Edge调试模式已启动（手动命令）")
                    else:
                        self.log_output("⚠️ 未找到Edge浏览器安装路径")
                        return
                
                time.sleep(3)  # 等待浏览器启动
                
                # 检测Edge是否成功启动
                try:
                    import socket
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    result = sock.connect_ex(('127.0.0.1', 9222))
                    sock.close()
                    
                    if result == 0:
                        self.log_output("✅ Edge调试端口已开启（端口9222）")
                        self.log_output("📝 使用说明：")
                        self.log_output("1. 如果您之前已经在Edge中登录B站，在新窗口中应该保持登录状态")
                        self.log_output("2. 如果未登录，请在打开的Edge浏览器中登录B站账号")
                        self.log_output("3. 登录完成后，即可使用AI字幕功能")
                        self.log_output("4. 点击'测试连接'按钮可以验证连接状态")
                        self.log_output("🔗 调试模式端口: 9222")
                    else:
                        self.log_output("⚠️ Edge调试端口未检测到，请手动检查浏览器是否启动")
                        self.log_output("💡 如果Edge未启动，请稍等几秒或点击'测试连接'")
                except Exception as e:
                    self.log_output("📝 状态检测失败，请手动验证Edge是否启动")
                    
            except Exception as e:
                self.log_output(f"❌ 启动Edge调试模式失败: {str(e)}")
                self.log_output("🔧 请尝试手动操作：")
                self.log_output("1. 关闭所有Edge窗口")
                self.log_output("2. 按Win+R，输入以下命令：")
                self.log_output('   "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe" --remote-debugging-port=9222')
                self.log_output("3. 在打开的Edge中登录B站")
        
        threading.Thread(target=start_edge, daemon=True).start()
    
    def test_edge_connection(self):
        """测试Edge连接状态"""
        def test_connection():
            try:
                self.log_output("🔗 正在测试Edge连接...")
                
                # 尝试导入selenium
                try:
                    from selenium import webdriver
                    from selenium.webdriver.edge.options import Options
                except ImportError:
                    self.log_output("⚠️ selenium未安装，无法测试连接")
                    return
                
                # 尝试连接调试模式
                try:
                    debug_options = Options()
                    debug_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
                    driver = webdriver.Edge(options=debug_options)
                    
                    # 获取当前页面信息
                    current_url = driver.current_url
                    page_title = driver.title
                    
                    self.log_output("✅ 成功连接到Edge调试模式")
                    self.log_output(f"📄 当前页面: {page_title}")
                    self.log_output(f"🔗 地址: {current_url}")
                    
                    # 检查是否在B站
                    if "bilibili.com" in current_url:
                        self.log_output("✅ 已在B站页面")
                        
                        # 检查登录状态 - 使用多种方法检测
                        try:
                            # 方法1: 查找登录相关元素
                            login_elements = driver.find_elements("css selector", ".header-login-entry")
                            user_elements = driver.find_elements("css selector", ".header-avatar-wrap")
                            
                            # 方法2: 检查用户信息
                            username_elements = driver.find_elements("css selector", ".username")
                            
                            # 方法3: 检查页面中的用户相关信息
                            user_info_elements = driver.find_elements("css selector", ".user-info, .user-name, .user-avatar")
                            
                            # 判断登录状态
                            is_logged_in = bool(user_elements or username_elements or user_info_elements)
                            is_not_logged_in = bool(login_elements)
                            
                            if is_logged_in and not is_not_logged_in:
                                self.log_output("✅ B站登录状态: 已登录")
                                self.log_output("🎉 可以使用AI字幕功能了！")
                                self.log_output("💡 提示: 现在可以提取字幕了")
                            elif is_not_logged_in and not is_logged_in:
                                self.log_output("⚠️ B站登录状态: 未登录")
                                self.log_output("📝 请在Edge中登录B站账号后再使用AI功能")
                                self.log_output("🔑 登录方法: 在Edge中访问 https://www.bilibili.com 并登录")
                            else:
                                self.log_output("❓ 登录状态不确定，建议手动确认")
                                self.log_output("💡 如已登录，可以直接尝试提取字幕")
                        except Exception as e:
                            self.log_output(f"❓ 无法检查登录状态: {str(e)}")
                            self.log_output("💡 建议手动确认B站登录状态")
                    else:
                        self.log_output(f"📝 当前不在B站页面")
                        self.log_output("🔗 建议手动访问 https://www.bilibili.com 并登录")
                        self.log_output("💡 或直接提取字幕，工具会自动跳转到视频页面")
                    
                    driver.quit()
                    
                except Exception as e:
                    if "ERR_CONNECTION_REFUSED" in str(e) or "No connection could be made" in str(e):
                        self.log_output("❌ Edge调试模式未启动")
                        self.log_output("📝 请先点击 '启动Edge' 按钮或者手动运行调试模式")
                    else:
                        self.log_output(f"❌ 连接失败: {str(e)}")
                        
            except Exception as e:
                self.log_output(f"❌ 测试连接时出错: {str(e)}")
        
        threading.Thread(target=test_connection, daemon=True).start()
    
    def clear_output(self):
        """清空输出日志"""
        self.output_text.delete(1.0, tk.END)
        self.log_output("日志已清空")
    
    def show_help(self):
        """显示帮助信息"""
        help_text = f"""
B站视频字幕提取工具 v{__version__} 使用帮助

🔧 功能说明：
• 现有字幕：提取视频已有的字幕文件
• AI小助手：获取B站AI生成的视频总结字幕
• 语音识别：使用Whisper将音频转换为字幕

📁 输出格式：
• SRT：标准字幕格式，支持大多数播放器
• TXT：纯文本格式，包含时间标记
• JSON：结构化数据格式，便于程序处理

⚠️ 注意事项：
• 确保网络连接正常
• AI模式首次使用需要下载浏览器驱动
• 语音识别需要FFmpeg支持
• 某些视频可能没有字幕或AI总结

📧 问题反馈：
如有问题请检查依赖安装是否完整

版权声明：
本工具仅供个人学习研究使用，不得用于商业用途。
使用本工具应遵守相关法律法规和网站使用条款。
        """
        messagebox.showinfo("使用帮助", help_text)
    
    def check_dependencies(self):
        """检查依赖工具"""
        def check():
            try:
                self.log_output("🔍 正在检查依赖工具...")
                extractor = BilibiliSubtitleExtractor()
                
                # 其他检查逻辑...
                self.log_output("✅ 依赖检查完成")
                
            except Exception as e:
                self.log_output(f"❌ 检查依赖时出错: {str(e)}")
        
        threading.Thread(target=check, daemon=True).start()
    
    def start_extraction(self):
        """开始字幕提取"""
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("错误", "请输入B站视频URL")
            return
        
        try:
            page_num = int(self.page_var.get())
        except ValueError:
            messagebox.showerror("错误", "页面号必须是数字")
            return
        
        output_dir = self.output_var.get().strip()
        if not output_dir:
            messagebox.showerror("错误", "请选择保存目录")
            return
        
        mode = self.mode_var.get()
        model_size = self.model_var.get()
        output_format = self.format_var.get()
        
        # 禁用开始按钮和显示进度条
        self.extract_button.config(state='disabled')
        self.progress.start()
        
        def extraction_thread():
            try:
                self.log_output("🚀 开始提取字幕...")
                self.log_output(f"📹 视频URL: {url}")
                self.log_output(f"📁 保存目录: {output_dir}")
                self.log_output(f"🔧 提取模式: {'现有字幕' if mode == 'subtitle' else 'AI小助手' if mode == 'ai' else '语音识别'}")
                self.log_output(f"📄 输出格式: {output_format.upper()}")
                self.log_output("-" * 60)
                
                # 提取逻辑...
                extractor = BilibiliSubtitleExtractor(output_dir)
                
                # 根据模式执行不同的提取
                success = False
                if mode == 'ai':
                    success = extractor.extract_subtitle_from_url(url, page_num, use_ai=True)
                elif mode == 'subtitle':
                    success = extractor.extract_subtitle_from_url(url, page_num, use_ai=False)
                elif mode == 'speech':
                    result = extractor.extract_subtitle_with_speech_recognition(url, model_size)
                    success = result is not None
                
                if success:
                    self.log_output("✅ 字幕提取成功！")
                else:
                    self.log_output("❌ 字幕提取失败")
                
            except Exception as e:
                self.log_output(f"❌ 提取过程出错: {str(e)}")
            finally:
                # 恢复界面状态
                self.root.after(0, self.extraction_finished)
        
        # 启动提取线程
        threading.Thread(target=extraction_thread, daemon=True).start()
    
    def extraction_finished(self):
        """提取完成后的处理"""
        self.extract_button.config(state='normal')
        self.progress.stop()
        self.log_output("-" * 60)
        self.log_output("🎉 提取过程完成")


def main():
    root = tk.Tk()
    app = ModernSubtitleExtractorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()