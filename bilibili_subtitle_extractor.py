#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
B站视频字幕提取工具 - 增强版
作者: wjm
版本: v2.0.0
创建时间: 2025


功能特色:
- 支持AI小助手字幕自动获取
- 支持Whisper语音识别生成字幕
- 智能浏览器自动化操作
- 多格式字幕输出

技术栈:
- Python 3.7+
- Selenium WebDriver
- OpenAI Whisper
- Microsoft Edge 浏览器

免责声明:
本工具由 wjm 开发，仅供个人学习和研究使用，不得用于商业用途或盈利。
使用本工具获取的内容应遵守相关网站的使用条款和版权规定。
作者 wjm 不承担因使用本工具而产生的任何法律责任。

版权声明:
Copyright (c) 2025 wjm. All rights reserved.
本软件遵循个人使用许可协议。
"""

import os
import sys
import json
import re
import requests
from urllib.parse import urlparse, parse_qs
import subprocess
import tempfile
from pathlib import Path
import argparse
import time

# 版本信息
__version__ = "2.0.0"
__author__ = "wjm"
__email__ = "[您的邮箱地址]"
__license__ = "Personal Use Only - 仅供个人使用"
__copyright__ = "Copyright (c) 2025 wjm"
__description__ = "B站视频字幕提取工具 - 支持AI小助手和语音识别"
__url__ = "[您的项目URL]"
__status__ = "Production"

class BilibiliSubtitleExtractor:
    def __init__(self, output_dir="./subtitles"):
        """
        初始化B站字幕提取器
        
        Args:
            output_dir: 字幕保存目录
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
            'Referer': 'https://www.bilibili.com/',
            'Origin': 'https://www.bilibili.com',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        })
        # FFmpeg路径配置
        self.ffmpeg_path = r"D:\ffmpeg-7.1.1-essentials_build\ffmpeg-7.1.1-essentials_build\bin"
        
    def print_banner(self):
        """打印程序横幅"""
        banner = f"""
╔══════════════════════════════════════════════════════════════╗
║                    B站视频字幕提取工具                        ║
║                      by wjm - 2025                          ║
║                                                              ║
║  版本: {__version__:<10} 作者: {__author__:<10}                        ║
║  状态: {__status__:<10} 许可: 个人使用                      ║
║                                                              ║
║  {__license__:<58} ║
║  本工具由 wjm 开发，不得用于商业用途，仅供个人学习研究使用      ║
║                                                              ║
║  Copyright (c) 2025 wjm. All rights reserved.               ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def get_ai_subtitle_with_edge(self, bvid):
        """使用Edge浏览器获取AI小助手字幕 - 完整的用户交互流程"""
        try:
            import time
            import re
            
            # 尝试导入selenium
            try:
                from selenium import webdriver
                from selenium.webdriver.common.by import By
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC
                from selenium.webdriver.edge.options import Options
                from selenium.common.exceptions import TimeoutException, NoSuchElementException
                from selenium.webdriver.common.action_chains import ActionChains
                from selenium.webdriver.common.keys import Keys
            except ImportError:
                print("未检测到selenium，无法使用浏览器自动化")
                print("请安装: pip install selenium")
                return None
            
            print("🤖 启动AI字幕提取 - 完整交互流程")
            print("🔄 连接策略: 1. 调试模式连接 → 2. 用户配置启动 → 3. 错误提示")
            
            # 优先连接到用户当前的Edge浏览器实例
            driver = None
            wait = None
            
            # 方法1: 尝试连接已运行的Edge调试实例（推荐）
            try:
                debug_options = Options()
                debug_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
                driver = webdriver.Edge(options=debug_options)
                driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                wait = WebDriverWait(driver, 20)
                print("✅ 成功连接到Edge调试模式（保持登录状态）")
            except Exception as debug_error:
                print(f"调试模式连接失败: {debug_error}")
                
                # 方法2: 尝试使用默认用户数据目录启动
                try:
                    edge_options = Options()
                    # 明确指定用户数据目录来保持登录状态
                    import os
                    user_data_dir = os.path.expandvars(r'%USERPROFILE%\AppData\Local\Microsoft\Edge\User Data')
                    edge_options.add_argument(f'--user-data-dir={user_data_dir}')
                    edge_options.add_argument('--profile-directory=Default')
                    edge_options.add_argument('--no-sandbox')
                    edge_options.add_argument('--disable-dev-shm-usage')
                    edge_options.add_argument('--disable-web-security')
                    edge_options.add_argument('--window-size=1920,1080')
                    edge_options.add_argument('--start-maximized')  # 确保窗口最大化显示
                    edge_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0')
                    edge_options.add_experimental_option('excludeSwitches', ['enable-automation'])
                    edge_options.add_experimental_option('useAutomationExtension', False)
                    # 设置为使用默认用户配置（这样能保持登录状态）
                    edge_options.add_argument('--disable-blink-features=AutomationControlled')
                    
                    driver = webdriver.Edge(options=edge_options)
                    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                    wait = WebDriverWait(driver, 20)
                    print("✅ 使用用户配置启动Edge浏览器（保持登录状态）")
                    print("📝 注意: 如果未登录B站，请在新窗口中手动登录")
                except Exception as normal_error:
                    print(f"正常模式启动失败: {normal_error}")
                    raise Exception(f"Edge浏览器启动失败。请先运行GUI中的'启动Edge调试模式'按钮")
            
            if not driver or not wait:
                raise Exception("无法启动Edge浏览器")
            
            try:
                video_url = f"https://www.bilibili.com/video/{bvid}"
                print(f"📺 访问视频页面: {video_url}")
                
                driver.get(video_url)
                print("⏳ 等待页面加载完成...")
                print("👀 请观察浏览器窗口，您可以看到自动化操作过程")
                
                # 确保浏览器窗口最大化和可见
                try:
                    driver.maximize_window()
                    driver.execute_script("window.focus();")
                    print("📺 浏览器窗口已最大化")
                except:
                    pass
                
                time.sleep(15)  # 给页面充分时间加载
                
                # 第一步：查找AI小助手按钮
                print("\n🔍 步骤1: 查找AI小助手按钮")
                ai_button = self.find_ai_assistant_button_enhanced(driver, wait)
                if not ai_button:
                    print("❌ 未找到AI小助手按钮，正在进行详细诊断...")
                    self.debug_page_content(driver)
                    print("❌ 此视频可能不支持AI功能，或页面结构发生变化")
                    return None
                
                # 第二步：点击AI小助手按钮
                print("\n👆 步骤2: 点击AI小助手按钮")
                success = self.click_ai_assistant_enhanced(driver, ai_button)
                if not success:
                    print("❌ AI小助手按钮点击失败")
                    return None
                
                # 步骤3已经在步骤2中完成（面板检测成功），直接进入步骤4
                print("\n✅ 步骤3: AI面板已检测到，跳过等待")
                
                # 第四步：确保在字幕列表标签页
                print("\n📋 步骤4: 切换到字幕列表标签页")
                success = self.ensure_subtitle_tab_active(driver)
                if not success:
                    print("❌ 无法切换到字幕列表标签页")
                    return None
                
                # 第五步：滚动获取所有字幕内容
                print("\n📜 步骤5: 获取字幕内容（智能滚动）")
                subtitles = self.extract_subtitles_with_smart_scroll(driver)
                
                if subtitles and len(subtitles) > 0:
                    print(f"\n✅ 成功获取 {len(subtitles[0]['body']) if subtitles[0].get('body') else 0} 条字幕")
                    return subtitles
                else:
                    print("❌ 未获取到字幕内容")
                    return None
                    
            finally:
                try:
                    print("⏸️ 操作完成，5秒后关闭浏览器...")
                    print("👀 您可以观察最后的页面状态")
                    time.sleep(5)  # 给用户时间观察结果
                    driver.quit()
                    print("🔚 浏览器已关闭")
                except:
                    pass
                
        except Exception as e:
            print(f"❌ AI字幕获取失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def convert_ai_content_to_subtitle(self, ai_content):
        """将AI内容转换为字幕格式"""
        try:
            if not ai_content or len(ai_content.strip()) < 20:
                return None
            
            # 清理内容
            content = ai_content.strip()
            
            # 按句子分割
            sentences = re.split(r'[.!?。！？、，;]', content)
            sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 5]
            
            if not sentences:
                return None
            
            # 创建字幕数据结构
            fake_subtitles = []
            duration_per_sentence = 4.0  # 每句话4秒
            
            subtitle_item = {
                'lan': 'ai-zh',
                'lan_doc': 'AI中文总结',
                'subtitle_url': '',
                'body': []
            }
            
            for i, sentence in enumerate(sentences):
                start_time = i * duration_per_sentence
                end_time = start_time + duration_per_sentence
                
                subtitle_item['body'].append({
                    'from': start_time,
                    'to': end_time,
                    'content': sentence
                })
            
            fake_subtitles.append(subtitle_item)
            
            print(f"将AI内容转换为字幕格式: {len(sentences)} 句")
            return fake_subtitles
            
        except Exception as e:
            print(f"转换AI内容时错误: {str(e)}")
            return None

    def preprocess_audio(self, audio_file):
        """预处理音频文件以加快 Whisper 处理速度"""
        try:
            import tempfile
            
            # 检查音频文件大小
            file_size = audio_file.stat().st_size / (1024 * 1024)  # MB
            print(f"原始音频文件大小: {file_size:.1f} MB")
            
            # 如果文件小于50MB，直接返回
            if file_size < 50:
                print("音频文件较小，跳过预处理")
                return audio_file
            
            # 为大文件进行压缩和优化
            compressed_file = self.output_dir / f"{audio_file.stem}_compressed.wav"
            
            # 使用FFmpeg压缩音频
            cmd = [
                os.path.join(self.ffmpeg_path, 'ffmpeg.exe'),
                '-i', str(audio_file),
                '-ar', '16000',  # 降采样率到16kHz
                '-ac', '1',      # 转为单声道
                '-ab', '64k',    # 降低比特率
                '-y',            # 覆盖输出文件
                str(compressed_file)
            ]
            
            print("正在压缩音频以加快处理...")
            result = subprocess.run(cmd, capture_output=True, text=True,
                                  encoding='utf-8', errors='ignore', timeout=300)
            
            if result.returncode == 0 and compressed_file.exists():
                new_size = compressed_file.stat().st_size / (1024 * 1024)
                print(f"音频压缩完成: {new_size:.1f} MB ({((file_size-new_size)/file_size*100):.1f}% 减少)")
                return compressed_file
            else:
                print("音频压缩失败，使用原文件")
                return audio_file
                
        except Exception as e:
            print(f"音频预处理出错: {str(e)}，使用原文件")
            return audio_file

    
    def extract_ai_content_from_page(self, driver):
        """从页面中提取AI生成的内容"""
        try:
            import re
            from selenium.webdriver.common.by import By
            
            # 获取页面全部文本
            page_text = driver.find_element(By.TAG_NAME, "body").get_attribute('textContent')
            
            # 查找AI内容容器
            ai_content_containers = []
            
            # 策略1: 查找特定的AI内容容器
            ai_container_selectors = [
                "[class*='ai-summary']",
                "[class*='conclusion']", 
                "[class*='summary-content']",
                "[class*='ai-content']",
                "[data-v-*][class*='content']",  # Vue组件样式
                ".summary-text",
                ".ai-text",
                ".conclusion-text"
            ]
            
            for selector in ai_container_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed():
                            text = element.get_attribute('textContent') or element.text or ''
                            if len(text.strip()) > 50:  # 过滤太短的内容
                                ai_content_containers.append(text.strip())
                except:
                    continue
            
            # 策略2: 通过正则表达式提取中文段落
            if not ai_content_containers:
                # 查找较长的中文段落（可能是AI总结）
                chinese_paragraphs = re.findall(r'[\u4e00-\u9fff][^\n\r]{30,300}', page_text)
                
                # 过滤和去重
                filtered_paragraphs = []
                exclude_keywords = [
                    '点击', '关注', '投币', '点赞', '分享', 'UP主', '播放量', 
                    '评论', '弹幕', '登录', '注册', '下载', '广告', '推荐',
                    '热门', '排行', '直播', '游戏', '购买', '价格'
                ]
                
                for para in chinese_paragraphs:
                    para = para.strip()
                    # 过滤常见的非内容关键词
                    if not any(keyword in para for keyword in exclude_keywords):
                        # 去重
                        if para not in filtered_paragraphs and len(para) > 30:
                            # 检查是否像是有意义的内容（包含足够的中文字符）
                            chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', para))
                            if chinese_chars / len(para) > 0.7:  # 中文字符比例超过70%
                                filtered_paragraphs.append(para)
                
                if len(filtered_paragraphs) >= 3:
                    ai_content_containers = filtered_paragraphs[:10]  # 取前10段
            
            # 合并和清理结果
            if ai_content_containers:
                combined_content = '\n'.join(ai_content_containers)
                # 简单清理
                combined_content = re.sub(r'\s+', ' ', combined_content)  # 合并多个空格
                combined_content = combined_content.replace('\t', ' ').strip()
                
                if len(combined_content) > 100:  # 确保有足够的内容
                    print(f"提取到AI内容: {len(combined_content)} 字符")
                    return combined_content
            
            return None
            
        except Exception as e:
            print(f"提取AI内容时出错: {str(e)}")
            return None
    
    def extract_bvid_from_url(self, url):
        """从 B站URL中提取BV号"""
        import re
        patterns = [
            r'BV[a-zA-Z0-9]+',
            r'av(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                if pattern.startswith('av'):
                    return match.group(0)
                else:
                    return match.group(0)
        
        raise ValueError("无法从URL中提取有效的视频ID")
    
    def get_video_info(self, bvid):
        """获取视频基本信息"""
        api_url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
        
        try:
            response = self.session.get(api_url)
            response.raise_for_status()
            data = response.json()
            
            if data['code'] != 0:
                raise Exception(f"获取视频信息失败: {data['message']}")
            
            video_info = data['data']
            return {
                'title': video_info['title'],
                'bvid': video_info['bvid'],
                'aid': video_info['aid'],
                'cid': video_info['cid'],
                'pages': video_info['pages']
            }
        except Exception as e:
            raise Exception(f"获取视频信息失败: {str(e)}")
    
    def extract_subtitle_from_url(self, video_url, page_num=1, use_ai=False):
        """从 B站视频URL提取字幕
        
        Args:
            video_url: B站视频URL
            page_num: 页面号(多P视频)
            use_ai: 是否优先使用AI小助手字幕
        """
        try:
            # 提取视频ID
            bvid = self.extract_bvid_from_url(video_url)
            print(f"提取到视频ID: {bvid}")
            
            # 获取视频信息
            video_info = self.get_video_info(bvid)
            print(f"视频标题: {video_info['title']}")
            
            # 如果开启AI模式，先尝试获取AI字幕
            if use_ai:
                print("尝试获取B站AI小助手字幕...")
                subtitles = self.get_ai_subtitle_with_edge(bvid)
                
                if subtitles:
                    print("AI字幕获取成功!")
                    # 保存AI字幕
                    safe_title = re.sub(r'[^\w\-_\. ]', '_', video_info['title'])
                    filename = f"{safe_title}_AI字幕.srt"
                    output_file = self.output_dir / filename
                    
                    # 转换为SRT格式并保存
                    srt_content = self.convert_to_srt(subtitles[0]['body'])
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(srt_content)
                    
                    print(f"AI字幕已保存到: {output_file}")
                    return True
                else:
                    print("AI字幕获取失败")
            
            # 如果没有AI字幕，返回失败（v2版本主要专注于AI功能）
            print("本版本主要支持AI字幕功能，请尝试使用语音识别模式")
            return False
            
        except Exception as e:
            print(f"提取字幕时出错: {str(e)}")
            return False
    
    def save_subtitle_with_format(self, subtitle_data, output_file, format_type='srt'):
        """根据指定格式保存字幕"""
        output_file = Path(output_file)
        base_name = output_file.stem
        
        if format_type.lower() == 'srt':
            srt_file = output_file.with_suffix('.srt')
            srt_content = self.convert_to_srt(subtitle_data)
            with open(srt_file, 'w', encoding='utf-8') as f:
                f.write(srt_content)
            return srt_file
            
        elif format_type.lower() == 'txt':
            txt_file = output_file.with_suffix('.txt')
            txt_content = ""
            for i, item in enumerate(subtitle_data, 1):
                start_time = self.format_time_simple(item['from'])
                end_time = self.format_time_simple(item['to'])
                content = item['content']
                txt_content += f"[{start_time} - {end_time}] {content}\n"
            
            with open(txt_file, 'w', encoding='utf-8') as f:
                f.write(txt_content)
            return txt_file
            
        elif format_type.lower() == 'json':
            json_file = output_file.with_suffix('.json')
            json_data = {
                'video_info': {'format': 'bilibili_subtitle'},
                'subtitles': subtitle_data
            }
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            return json_file
    
    def format_time_simple(self, seconds):
        """将秒数转换为简单时间格式"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"

    def convert_to_srt(self, subtitle_data):
        """将字幕数据转换为SRT格式"""
        srt_content = ""
        
        for i, item in enumerate(subtitle_data, 1):
            start_time = self.format_srt_time(item['from'])
            end_time = self.format_srt_time(item['to'])
            content = item['content'].strip()
            
            srt_content += f"{i}\n"
            srt_content += f"{start_time} --> {end_time}\n"
            srt_content += f"{content}\n\n"
        
        return srt_content
    
    def format_srt_time(self, seconds):
        """将秒数转换为SRT时间格式"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"
    
    def extract_subtitle_with_speech_recognition(self, video_url, model_size="base"):
        """使用语音识别从 B站视频提取字幕 - 加速版"""
        try:
            print("开始语音识别流程...")
            
            # 优化的音频下载
            audio_file = self.download_audio_optimized(video_url)
            print(f"音频下载完成: {audio_file}")
            
            # 加速的音频转文字
            subtitle_file = self.audio_to_text_optimized(audio_file, model_size)
            
            return subtitle_file
            
        except Exception as e:
            print(f"语音识别提取字幕时出错: {str(e)}")
            return None
    
    def download_audio_optimized(self, video_url):
        """优化的音频下载 - 更快的速度"""
        try:
            import tempfile
            
            # 使用临时目录优化IO性能
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_output_dir = Path(temp_dir)
                
                # 优化的yt-dlp命令，使用更快的设置
                cmd = [
                    'yt-dlp',
                    '--extract-audio',
                    '--audio-format', 'wav',
                    '--audio-quality', '5',  # 降低音频质量以加快下载
                    '--no-playlist',  # 禁用播放列表
                    '--no-write-info-json',  # 不写入元数据
                    '--no-write-thumbnail',  # 不下载缩略图
                    '--ffmpeg-location', self.ffmpeg_path,
                    '-o', str(temp_output_dir / '%(title)s.%(ext)s'),
                    video_url
                ]
                
                print("正在下载音频（优化模式）...")
                result = subprocess.run(cmd, capture_output=True, text=True, 
                                      encoding='utf-8', errors='ignore', timeout=300)  # 5分钟超时
                
                if result.returncode != 0:
                    raise Exception(f"下载失败: {result.stderr}")
                
                # 查找下载的音频文件
                audio_files = list(temp_output_dir.glob("*.wav"))
                if audio_files:
                    # 移动到最终目录
                    final_audio_file = self.output_dir / audio_files[0].name
                    audio_files[0].rename(final_audio_file)
                    return final_audio_file
                else:
                    raise Exception("未找到下载的音频文件")
                    
        except FileNotFoundError:
            raise Exception("yt-dlp 未安装，请先安装: pip install yt-dlp")
        except subprocess.TimeoutExpired:
            raise Exception("音频下载超时，请检查网络连接")
    
    def audio_to_text_optimized(self, audio_file, model_size="base"):
        """优化的音频转文字 - 更快的Whisper设置"""
        try:
            audio_file = Path(audio_file)
            if not audio_file.exists():
                raise Exception(f"音频文件不存在: {audio_file}")
            
            # 首先预处理音频以加快处理速度
            processed_audio = self.preprocess_audio(audio_file)
            
            # 构造输出文件名
            output_file = self.output_dir / f"{audio_file.stem}_whisper.srt"
            
            # 设置FFmpeg环境变量
            env = os.environ.copy()
            if self.ffmpeg_path not in env.get('PATH', ''):
                env['PATH'] = self.ffmpeg_path + os.pathsep + env.get('PATH', '')
            
            # 优化的Whisper命令
            cmd = [
                'whisper',
                str(processed_audio),
                '--model', model_size,
                '--language', 'Chinese',
                '--output_dir', str(self.output_dir),
                '--output_format', 'srt',
                '--fp16', 'False',  # 禁用16位浮点数以提高兼容性
                '--threads', '4',  # 使用4个线程
                '--no_speech_threshold', '0.6',  # 降低语音检测阈值
                '--condition_on_previous_text', 'False',  # 禁用上下文依赖以加快速度
            ]
            
            print(f"正在使用 Whisper 转换音频为文字 (模型: {model_size}, 优化模式)...")
            print("优化设置: 禁用FP16, 4线程, 无上下文依赖")
            print("这可能需要几分钟时间，请耐心等待...")
            
            result = subprocess.run(cmd, capture_output=True, text=True, 
                                  encoding='utf-8', errors='ignore', env=env, timeout=1800)  # 30分钟超时
            
            if result.returncode != 0:
                error_msg = result.stderr.strip()
                
                # 检查常见错误
                if "NumPy" in error_msg and "cannot be run in" in error_msg:
                    numpy_error = (
                        "NumPy版本兼容性问题！\n"
                        "请运行: python fix_numpy_compatibility.py"
                    )
                    raise Exception(numpy_error)
                else:
                    raise Exception(f"转换失败: {error_msg}")
            
            # 查找生成的字幕文件
            srt_files = list(self.output_dir.glob(f"{processed_audio.stem}*.srt"))
            if srt_files:
                print(f"字幕文件已生成: {srt_files[-1]}")
                
                # 清理预处理的音频文件
                if processed_audio != audio_file and processed_audio.exists():
                    processed_audio.unlink()
                
                return srt_files[-1]
            else:
                raise Exception("未找到生成的字幕文件")
                
        except FileNotFoundError:
            raise Exception("Whisper 未安装，请先安装: pip install openai-whisper")
        except subprocess.TimeoutExpired:
            raise Exception("语音识别超时，请尝试使用更小的模型")
    
    def find_ai_assistant_button_enhanced(self, driver, wait):
        """增强版AI小助手按钮查找 - 专门针对图标按钮"""
        from selenium.webdriver.common.by import By
        import time
        
        print("🔍 使用图标识别策略查找AI小助手按钮...")
        
        # 策略1: B站视频页面的精确选择器（基于实际结构）
        bilibili_specific_selectors = [
            # B站视频页面右侧工具栏
            ".video-toolbar-right button", ".video-toolbar button", ".toolbar button",
            "[class*='video-toolbar'] button", "[class*='toolbar'] button",
            # B站视频信息区域
            ".video-info-v1 button", ".video-desc button", ".video-info button",
            "[class*='video-info'] button", "[class*='video-desc'] button",
            # B站侧边栏和操作区域
            ".right-container button", ".side-toolbar button", ".operation-btn",
            "[class*='right-container'] button", "[class*='side-toolbar'] button",
            # 通用按钮容器
            ".video-page button", "[class*='video'] button", "[id*='video'] button",
            # 更广泛的查找
            "button[class*='btn']", "div[role='button']", "span[role='button']", "a[role='button']"
        ]
        
        # 策略2: 基于属性的选择器（AI相关但不依赖文本）
        attribute_selectors = [
            "[data-name*='ai']", "[data-module*='ai']", "[data-action*='ai']",
            "[class*='ai-']", "[class*='_ai_']", "[class*='AI']",
            "[title*='AI']", "[aria-label*='AI']", "[data-title*='AI']",
            "[class*='summary']", "[class*='assistant']", "[class*='smart']",
            "[data-v-*][class*='tool']", "[data-v-*][class*='action']"
        ]
        
        # 策略3: 位置和视觉特征查找
        visual_selectors = [
            # 小尺寸按钮（通常图标按钮较小）
            "button", "[role='button']", ".btn", "[class*='btn']",
            # 在特定容器中的元素
            ".video-page button", ".bilibili-player button", ".player-auxiliary-area button"
        ]
        
        all_selectors = bilibili_specific_selectors + attribute_selectors + visual_selectors
        
        print(f"将尝试 {len(all_selectors)} 种不同的选择器策略")
        
        for i, selector in enumerate(all_selectors):
            try:
                print(f"🔎 策略 {i+1}/{len(all_selectors)}: {selector}")
                
                # 查找元素
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                
                if not elements:
                    continue
                    
                print(f"   找到 {len(elements)} 个候选元素")
                
                # 对每个元素进行详细评估
                for j, element in enumerate(elements):
                    try:
                        if not (element.is_displayed() and element.is_enabled()):
                            continue
                            
                        # 使用图标识别评分系统
                        score = self.calculate_ai_icon_score(element)
                        
                        if score > 0.6:  # 降低阈值，因为图标识别更严格
                            element_info = self.get_detailed_element_info(element)
                            print(f"   ✅ 候选 {j+1}: {element_info} (评分: {score:.2f})")
                            return element
                        elif score > 0.3:
                            element_info = self.get_detailed_element_info(element)
                            print(f"   📋 候选 {j+1}: {element_info} (评分: {score:.2f}) - 分数偏低")
                            
                    except Exception as e:
                        continue
                        
            except Exception as e:
                print(f"   ❌ 策略失败: {str(e)[:50]}")
                continue
        
        print("❌ 所有策略均未找到合适的AI按钮")
        return None
    
    def is_valid_ai_button(self, driver, element):
        """验证元素是否为有效的AI按钮"""
        try:
            if not (element.is_displayed() and element.is_enabled()):
                return False
            
            # 获取元素文本和属性
            text = (element.get_attribute('textContent') or 
                   element.get_attribute('innerText') or 
                   element.get_attribute('title') or 
                   element.get_attribute('aria-label') or 
                   element.text or '').strip().lower()
            
            class_name = (element.get_attribute('class') or '').lower()
            tag_name = element.tag_name.lower()
            
            # AI相关关键词
            ai_keywords = ['ai', '总结', '小助手', '智能', 'summary', 'assistant', 'conclusion']
            
            # 检查文本内容
            has_ai_text = any(keyword in text for keyword in ai_keywords)
            has_ai_class = any(keyword in class_name for keyword in ['ai', 'summary', 'assistant'])
            is_interactive = tag_name in ['button', 'a'] or 'button' in class_name or element.get_attribute('role') == 'button'
            
            # 简单的位置检查（排除明显不可能的位置）
            location = element.location
            size = element.size
            is_reasonable_size = size['width'] > 20 and size['height'] > 20
            is_reasonable_position = location['x'] >= 0 and location['y'] >= 0
            
            return (has_ai_text or has_ai_class) and is_interactive and is_reasonable_size and is_reasonable_position
            
        except Exception:
            return False
    
    def smart_text_search_ai_button(self, driver):
        """智能文本搜索AI按钮"""
        from selenium.webdriver.common.by import By
        
        try:
            # 获取所有可能的交互元素
            interactive_selectors = [
                "button", "a", "div[role='button']", "span[role='button']", 
                "[onclick]", "[data-action]", "[class*='btn']", "[class*='button']"
            ]
            
            candidates = []
            for selector in interactive_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    candidates.extend(elements)
                except:
                    continue
            
            # 智能评分系统
            best_candidate = None
            best_score = 0
            
            for element in candidates:
                score = self.calculate_ai_button_score(element)
                if score > best_score and score > 0.5:  # 阈值0.5
                    best_score = score
                    best_candidate = element
            
            if best_candidate:
                print(f"🏆 智能匹配找到AI按钮（评分: {best_score:.2f}）")
                return best_candidate
            
        except Exception as e:
            print(f"智能搜索失败: {e}")
        
        return None
    
    def debug_page_content(self, driver):
        """调试页面内容，查找可能的AI元素"""
        try:
            from selenium.webdriver.common.by import By
            print("🔍 开始页面调试分析...")
            
            # 检查页面标题
            try:
                title = driver.title
                print(f"📝 页面标题: {title}")
            except:
                print("❌ 无法获取页面标题")
            
            # 检查当前 URL
            try:
                current_url = driver.current_url
                print(f"🔗 当前 URL: {current_url}")
            except:
                print("❌ 无法获取当前 URL")
            
            # 查找所有按钮和链接
            buttons_and_links = []
            try:
                buttons = driver.find_elements(By.TAG_NAME, "button")
                links = driver.find_elements(By.TAG_NAME, "a")
                divs_with_role = driver.find_elements(By.CSS_SELECTOR, "div[role='button']")
                spans_with_role = driver.find_elements(By.CSS_SELECTOR, "span[role='button']")
                
                all_interactive = buttons + links + divs_with_role + spans_with_role
                
                print(f"🔍 找到 {len(all_interactive)} 个交互元素")
                
                ai_related = []
                for element in all_interactive:
                    try:
                        if not element.is_displayed():
                            continue
                        
                        text = (element.get_attribute('textContent') or '').strip()
                        class_name = element.get_attribute('class') or ''
                        title_attr = element.get_attribute('title') or ''
                        aria_label = element.get_attribute('aria-label') or ''
                        
                        all_text = f"{text} {class_name} {title_attr} {aria_label}".lower()
                        
                        # 查找AI相关关键词
                        ai_keywords = ['ai', '总结', '小助手', '智能', 'summary', 'assistant']
                        if any(keyword in all_text for keyword in ai_keywords):
                            ai_related.append({
                                'tag': element.tag_name,
                                'text': text[:50],
                                'class': class_name[:50],
                                'title': title_attr[:50],
                                'aria_label': aria_label[:50]
                            })
                    except:
                        continue
                
                if ai_related:
                    print(f"🤖 找到 {len(ai_related)} 个AI相关元素:")
                    for i, element_info in enumerate(ai_related[:10]):  # 只显示前10个
                        print(f"  {i+1}. {element_info['tag']}: '{element_info['text']}'")
                        if element_info['class']:
                            print(f"     class: {element_info['class']}")
                else:
                    print("❌ 未找到任何AI相关元素")
                    
            except Exception as e:
                print(f"❌ 元素分析失败: {e}")
            
            # 检查页面是否包含登录提示
            try:
                body_text = driver.find_element(By.TAG_NAME, "body").get_attribute('textContent')
                if '登录' in body_text or 'login' in body_text.lower():
                    print("⚠️ 页面可能需要登录")
                if '不支持' in body_text or '暂无' in body_text:
                    print("⚠️ 页面可能显示不支持AI功能")
            except:
                pass
                
        except Exception as e:
            print(f"❌ 页面调试失败: {str(e)}")
    
    def debug_ai_panel_status(self, driver):
        """调试AI面板状态，分析为什么未出现面板"""
        try:
            from selenium.webdriver.common.by import By
            print("🔍 AI面板状态调试分析:")
            
            # 1. 检查窗口尺寸
            window_size = driver.get_window_size()
            print(f"   📺 窗口尺寸: {window_size['width']}x{window_size['height']}")
            
            # 2. 检查右侧区域的所有可见元素
            right_elements = driver.execute_script(f"""
                var rightElements = [];
                var allElements = document.querySelectorAll('*');
                for (var i = 0; i < allElements.length; i++) {{
                    var element = allElements[i];
                    var rect = element.getBoundingClientRect();
                    var style = window.getComputedStyle(element);
                    
                    if (rect.left > {window_size['width'] * 0.6} && 
                        rect.width > 100 && rect.height > 100 &&
                        style.display !== 'none' && style.visibility !== 'hidden') {{
                        rightElements.push({{
                            tagName: element.tagName,
                            className: element.className,
                            id: element.id,
                            width: Math.round(rect.width),
                            height: Math.round(rect.height),
                            left: Math.round(rect.left),
                            top: Math.round(rect.top),
                            text: element.textContent ? element.textContent.substring(0, 50) : ''
                        }});
                    }}
                }}
                return rightElements;
            """)
            
            if right_elements:
                print(f"   📋 右侧区域找到 {len(right_elements)} 个可见元素:")
                for i, elem in enumerate(right_elements[:5]):  # 只显示前5个
                    print(f"     {i+1}. {elem['tagName']}.{elem['className'][:30]} [{elem['width']}x{elem['height']}] @({elem['left']},{elem['top']}) '{elem['text'][:30]}'")
                if len(right_elements) > 5:
                    print(f"     ... 还有 {len(right_elements) - 5} 个元素")
            else:
                print("   ❌ 右侧区域没有找到大尺寸可见元素")
            
            # 3. 检查是否有AI相关的元素
            ai_related_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'AI') or contains(text(), '字幕') or contains(text(), '总结')]")
            print(f"   🤖 页面中包含AI相关文本的元素数量: {len(ai_related_elements)}")
            
            # 4. 检查是否有错误或加载信息
            try:
                error_elements = driver.find_elements(By.XPATH, "//*[contains(text(), '错误') or contains(text(), '失败') or contains(text(), '加载') or contains(text(), '网络')]")
                if error_elements:
                    print(f"   ⚠️ 可能的错误信息:")
                    for elem in error_elements[:3]:
                        text = elem.text.strip()
                        if text:
                            print(f"     - {text[:50]}")
            except:
                pass
            
            # 5. 检查当前页面URL和标题
            current_url = driver.current_url
            page_title = driver.title
            print(f"   🔗 当前URL: {current_url}")
            print(f"   📝 页面标题: {page_title}")
            
            # 6. 检查是否有登录问题
            try:
                login_elements = driver.find_elements(By.XPATH, "//*[contains(text(), '登录') or contains(text(), '登陆')]")
                if login_elements:
                    print(f"   🔑 可能需要登录: 找到 {len(login_elements)} 个登录相关元素")
            except:
                pass
                
        except Exception as e:
            print(f"   ❌ 调试分析失败: {str(e)}")
    
    def calculate_ai_icon_score(self, element):
        """专门针对AI图标按钮的评分系统"""
        try:
            from selenium.webdriver.common.by import By
            score = 0.0
            
            # 获取元素信息
            text = (element.get_attribute('textContent') or element.text or '').strip()
            class_name = (element.get_attribute('class') or '').lower()
            tag_name = element.tag_name.lower()
            title = (element.get_attribute('title') or '').lower()
            aria_label = (element.get_attribute('aria-label') or '').lower()
            href = (element.get_attribute('href') or '').lower()
            data_name = (element.get_attribute('data-name') or '').lower()
            onclick = (element.get_attribute('onclick') or '').lower()
            
            # 过滤明显的非目标元素
            if self.is_obviously_not_ai_button(element, text, href):
                return 0
            
            # 1. 精确匹配AI相关关键词（最高分）
            all_text = f"{text} {class_name} {title} {aria_label} {data_name} {onclick}".lower()
            
            # 精确匹配
            if 'ai小助手' in all_text:
                score += 1.0
            elif 'ai总结' in all_text or 'ai智能总结' in all_text:
                score += 0.9
            elif '视频总结' in all_text or '智能总结' in all_text:
                score += 0.8
            elif 'ai' in all_text and ('助手' in all_text or '智能' in all_text or '总结' in all_text):
                score += 0.7
            
            # 2. 基于CSS类名的匹配
            if any(ai_class in class_name for ai_class in ['ai-', '_ai_', 'summary', 'assistant', 'smart']):
                score += 0.6
            
            # 3. 基于数据属性的匹配
            if any(keyword in data_name for keyword in ['ai', 'summary', 'assistant']):
                score += 0.5
            
            # 4. 位置和尺寸特征加分
            location = element.location
            size = element.size
            
            # 合理的图标按钮尺寸（20-80px宽高）
            if 20 <= size['width'] <= 80 and 20 <= size['height'] <= 80:
                score += 0.3
            elif 15 <= size['width'] <= 120 and 15 <= size['height'] <= 120:
                score += 0.2
            
            # 在视频页面右侧的位置加分
            try:
                window_size = element.parent.execute_script("return {width: window.innerWidth, height: window.innerHeight};") if hasattr(element, 'parent') else {'width': 1920, 'height': 1080}
                if location['x'] > window_size.get('width', 1920) * 0.6:  # 在右侦
                    score += 0.2
            except:
                pass
            
            # 5. 交互性特征
            if tag_name == 'button' or element.get_attribute('role') == 'button':
                score += 0.3
            elif 'btn' in class_name or 'button' in class_name:
                score += 0.2
            
            # 6. 特殊情况处理：无文本的图标按钮
            if len(text.strip()) == 0:  # 纯图标按钮
                # 通过其他特征判断
                if any(keyword in class_name for keyword in ['tool', 'action', 'icon', 'feature']):
                    score += 0.4
                if size['width'] <= 50 and size['height'] <= 50:  # 小尺寸图标
                    score += 0.3
                # 在合适的位置
                if location['x'] > 200 and location['y'] > 100:  # 不在左上角
                    score += 0.2
            
            # 7. 在B站特定容器中的加分
            parent_classes = []
            try:
                parent = element.find_element(By.XPATH, "./..")
                parent_classes.append(parent.get_attribute('class') or '')
                grandparent = parent.find_element(By.XPATH, "./..")
                parent_classes.append(grandparent.get_attribute('class') or '')
            except:
                pass
            
            parent_text = ' '.join(parent_classes).lower()
            if any(container in parent_text for container in ['video', 'toolbar', 'action', 'tool', 'operation']):
                score += 0.3
                
            return min(max(score, 0), 1.0)
            
        except Exception as e:
            return 0
    
    def is_obviously_not_ai_button(self, element, text, href):
        """过滤明显不是AI按钮的元素"""
        # 文本过长，可能是视频标题等
        if len(text) > 50:
            return True
            
        # 视频链接
        if 'video' in href and 'BV' in href:
            return True
            
        # 视频集数
        if '第' in text and '集' in text:
            return True
            
        # 明显的非目标内容
        unwanted_keywords = ['stm32', '教程', '部署', '播放', '下载', '分享', '收藏', '点赞', '评论', '投币']
        text_lower = text.lower()
        if any(keyword in text_lower for keyword in unwanted_keywords):
            return True
            
        return False
    
    def get_detailed_element_info(self, element):
        """获取详细的元素信息用于调试"""
        try:
            text = (element.get_attribute('textContent') or element.text or '').strip()
            class_name = element.get_attribute('class') or ''
            tag_name = element.tag_name
            title = element.get_attribute('title') or ''
            data_name = element.get_attribute('data-name') or ''
            location = element.location
            size = element.size
            
            info_parts = []
            info_parts.append(f"Tag:{tag_name}")
            if text:
                info_parts.append(f"Text:'{text[:20]}'")
            if class_name:
                info_parts.append(f"Class:'{class_name[:30]}'")
            if title:
                info_parts.append(f"Title:'{title[:20]}'")
            if data_name:
                info_parts.append(f"Data:'{data_name[:20]}'")
            info_parts.append(f"Size:{size['width']}x{size['height']}")
            info_parts.append(f"Pos:({location['x']},{location['y']})")
            
            return ' | '.join(info_parts)
        except:
            return "unknown element"
    
    def calculate_ai_button_score(self, element):
        """计算元素作AI按钮的得分"""
        try:
            if not element.is_displayed():
                return 0
            
            score = 0
            
            # 获取元素信息
            text = (element.get_attribute('textContent') or '').strip()
            class_name = (element.get_attribute('class') or '').lower()
            tag_name = element.tag_name.lower()
            title = (element.get_attribute('title') or '').lower()
            aria_label = (element.get_attribute('aria-label') or '').lower()
            href = (element.get_attribute('href') or '').lower()
            
            # 过滤掉明显的非目标元素
            if len(text) > 100:  # 文本太长，可能是视频标题等
                return 0
            if 'video' in href and 'BV' in href:  # 视频链接
                return 0
            if '第' in text and '集' in text:  # 视频集数
                return 0
            if 'stm32' in text.lower() and ('教程' in text or '部署' in text):  # STM32相关视频
                return 0
            
            all_text_lower = f"{text} {class_name} {title} {aria_label}".lower()
            
            # 精确匹配"AI小助手"
            if 'ai小助手' in text:
                score += 1.0  # 最高分
            elif 'ai小助手' in all_text_lower:
                score += 0.9
            
            # 其他AI相关匹配
            elif 'ai总结' in text or 'ai智能总结' in text:
                score += 0.8
            elif '视频总结' in text:
                score += 0.7
            elif text == 'AI' or text == 'ai':  # 简单的AI文本
                score += 0.6
            elif 'ai' in all_text_lower and len(text) < 20:  # 短文本中包含AI
                score += 0.4
            
            # 标签类型加分
            if tag_name == 'button':
                score += 0.3
            elif tag_name == 'a' and not href:  # 没有href的链接，可能是按钮
                score += 0.2
            elif element.get_attribute('role') == 'button':
                score += 0.2
            
            # 位置和尺寸检查
            location = element.location
            size = element.size
            
            # AI按钮通常不会太大或太小
            if 30 <= size['width'] <= 200 and 20 <= size['height'] <= 60:
                score += 0.1
            elif size['width'] > 500 or size['height'] > 100:  # 太大的元素，可能不是按钮
                score -= 0.5
            
            # 检查是否在合理的位置（不在页面最左侧或最底部）
            window_size = element.parent.get_window_size() if hasattr(element, 'parent') else {'width': 1920, 'height': 1080}
            if location['x'] < 50:  # 太靠左
                score -= 0.2
            if location['y'] > window_size.get('height', 1080) * 0.8:  # 太靠下
                score -= 0.2
            
            return min(max(score, 0), 1.0)  # 分数0-1之间
            
        except Exception:
            return 0
    
    def get_element_info(self, element):
        """获取元素信息用于日志"""
        try:
            text = (element.get_attribute('textContent') or element.text or '').strip()
            class_name = element.get_attribute('class') or ''
            tag_name = element.tag_name
            return f"{tag_name}.{class_name[:30]} '{text[:30]}'"
        except:
            return "unknown element"
    
    def click_ai_assistant_enhanced(self, driver, ai_button):
        """增强版AI小助手按钮点击"""
        import time
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.action_chains import ActionChains
        from selenium.webdriver.common.keys import Keys
        
        try:
            print(f"👆 准备点击AI按钮: {self.get_element_info(ai_button)}")
            
            # 确保元素可见并居中
            driver.execute_script("""
                arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});
                arguments[0].style.border = '2px solid red';
            """, ai_button)
            time.sleep(2)
            
            # 获取点击前的页面状态
            before_panels = len(driver.find_elements(By.CSS_SELECTOR, "[class*='InteractWrapper'], [class*='VideoAssistant'], [data-video-assistant-subject-wrapper]"))
            print(f"📊 点击前面板数量: {before_panels}")
            
            # 多种点击策略
            click_strategies = [
                {
                    'name': '直接点击',
                    'action': lambda: ai_button.click()
                },
                {
                    'name': 'JavaScript点击',
                    'action': lambda: driver.execute_script("arguments[0].click();", ai_button)
                },
                {
                    'name': '动作链点击',
                    'action': lambda: ActionChains(driver).move_to_element(ai_button).click().perform()
                },
                {
                    'name': '双击策略',
                    'action': lambda: ActionChains(driver).move_to_element(ai_button).double_click().perform()
                },
                {
                    'name': '焦点+回车',
                    'action': lambda: (ai_button.click(), ai_button.send_keys(Keys.RETURN))
                }
            ]
            
            for i, strategy in enumerate(click_strategies):
                try:
                    print(f"🔄 尝试{strategy['name']}...")
                    
                    # 执行点击
                    strategy['action']()
                    
                    # 等待响应（优化等待时间）
                    print("⏳ 等待AI面板加载...")
                    
                    # 每0.5秒检查一次，最多等待12次（6秒）
                    for wait_attempt in range(12):
                        time.sleep(0.5)  # 等待0.5秒
                        
                        # 检查是否成功
                        success = self.verify_ai_panel_appeared(driver, before_panels)
                        if success:
                            print(f"✅ {strategy['name']}成功! (等待{(wait_attempt + 1) * 0.5:.1f}秒后检测到面板)")
                            return True
                        
                        if wait_attempt < 11:  # 不是最后一次
                            print(f"   ⏳ 继续等待... ({(wait_attempt + 1) * 0.5:.1f}/6.0秒)")
                    
                    print(f"❌ {strategy['name']}失败 - 等待6秒后仍未检测到面板")
                        
                except Exception as e:
                    print(f"❌ {strategy['name']}出错: {str(e)}")
                    continue
            
            print("❌ 所有点击策略均失败")
            
            # 添加详细的页面调试信息
            print("🔍 进行详细的页面调试分析...")
            self.debug_ai_panel_status(driver)
            
            return False
            
        except Exception as e:
            print(f"❌ 点击AI按钮失败: {str(e)}")
            return False
    
    def verify_ai_panel_appeared(self, driver, before_count):
        """验证AI面板是否出现 - 超简化版"""
        from selenium.webdriver.common.by import By
        import time
        
        try:
            print("🔍 检测AI面板是否出现...")
            
            # 最简单的检测：直接查找页面中是否出现了这些关键元素
            success_indicators = [
                "视频总结",  # 左侧标签
                "字幕列表",  # 右侧标签  
                "AI小助手",  # 面板标题
                "00:01",    # 字幕时间戳
                "Hello"     # 字幕内容示例
            ]
            
            found_indicators = []
            
            for indicator in success_indicators:
                try:
                    elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{indicator}')]")
                    if elements:
                        # 检查是否有可见元素
                        visible_count = sum(1 for elem in elements if elem.is_displayed())
                        if visible_count > 0:
                            found_indicators.append(indicator)
                            print(f"   ✅ 找到: '{indicator}' (共{visible_count}个可见元素)")
                except Exception as e:
                    continue
            
            # 如果找到2个或以上指示器，认为面板已出现
            if len(found_indicators) >= 2:
                print(f"✅ AI面板检测成功! 找到 {len(found_indicators)} 个指示器: {found_indicators}")
                return True
            
            # 备用检测：检查是否有新的可见元素出现在页面上
            try:
                visible_elements = driver.execute_script("""
                    var count = 0;
                    var allElements = document.querySelectorAll('*');
                    for (var i = 0; i < allElements.length; i++) {
                        var elem = allElements[i];
                        var style = window.getComputedStyle(elem);
                        if (style.display !== 'none' && style.visibility !== 'hidden' && 
                            elem.offsetWidth > 0 && elem.offsetHeight > 0) {
                            count++;
                        }
                    }
                    return count;
                """)
                
                print(f"   📊 当前页面可见元素总数: {visible_elements}")
                
                # 如果元素数量显著增加，可能是面板出现了
                if visible_elements > 500:  # 假设面板会增加较多元素
                    print("✅ 检测到页面元素显著增加，可能是AI面板出现")
                    return True
                    
            except Exception as e:
                print(f"   ❌ 元素计数失败: {str(e)}")
            
            print(f"❌ AI面板检测失败 - 只找到 {len(found_indicators)} 个指示器: {found_indicators}")
            return False
            
        except Exception as e:
            print(f"检查面板时出错: {str(e)}")
            return False
    
    def wait_for_ai_panel_enhanced(self, driver, wait):
        """增强版等待AI面板出现"""
        import time
        from selenium.webdriver.common.by import By
        
        print("🔍 等待AI面板出现...")
        
        # 基于您提供的HTML结构的精确选择器
        precise_panel_selectors = [
            # 您提供的精确结构
            "[data-video-assistant-subject-wrapper]",
            "[data-video-assistant-subject]",
            "div[class*='_InteractWrapper_']",
            "div[class*='_VideoAssistant_']",
            # 常见的AI面板选择器
            "[class*='VideoAssistant']",
            "[class*='InteractWrapper']",
            "[class*='ai-panel']",
            "[class*='assistant-panel']",
            "[class*='video-assistant']",
            # 通用弹窗/侧边栏选择器
            "[class*='sidebar']",
            "[class*='drawer']", 
            "[class*='panel']",
            "[class*='popup']",
            "[class*='modal']"
        ]
        
        # 等待最多20秒
        for attempt in range(40):  # 20秒，每0.5秒检查一次
            try:
                for selector in precise_panel_selectors:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if self.is_valid_ai_panel(driver, element):
                            print(f"✅ 找到AI面板: {selector}")
                            return element
                
                # 显示进度
                if attempt % 4 == 0:  # 每2秒显示一次
                    print(f"⏳ 等待中... ({attempt//2 + 1}/20秒)")
                
                time.sleep(0.5)
                
            except Exception:
                time.sleep(0.5)
                continue
        
        print("❌ 超时，未找到AI面板")
        return None
    
    def is_valid_ai_panel(self, driver, element):
        """验证元素是否为有效的AI面板"""
        try:
            if not element.is_displayed():
                return False
            
            # 检查尺寸（AI面板通常比较大）
            size = element.size
            if size['width'] < 300 or size['height'] < 400:
                return False
            
            # 检查位置（通常在右侧）
            location = element.location
            window_width = driver.get_window_size()['width']
            is_right_side = location['x'] > window_width * 0.5
            
            # 检查内容（包含AI相关文本）
            text_content = element.get_attribute('textContent') or ''
            has_ai_content = any(keyword in text_content for keyword in [
                'AI小助手', '视频总结', '字幕列表', 'AI', '总结', 
                '小助手', '智能', 'assistant', 'summary'
            ])
            
            # 检查是否包含标签页结构
            has_tabs = len(element.find_elements(By.CSS_SELECTOR, "[class*='tab'], [class*='Tab']")) > 0
            
            return (is_right_side or has_ai_content) and (has_ai_content or has_tabs) and len(text_content.strip()) > 100
            
        except Exception:
            return False
    
    def ensure_subtitle_tab_active(self, driver, timeout=10):
        """确保字幕列表标签页处于激活状态"""
        try:
            import time
            from selenium.webdriver.common.by import By
            from selenium.webdriver.common.action_chains import ActionChains
            
            print("📋 查找并点击字幕列表标签页...")
            
            # 策略1: 直接搜索包含"字幕列表"的元素
            subtitle_tab = None
            
            # 使用多种XPath策略查找
            xpath_strategies = [
                "//div[text()='字幕列表']",
                "//span[text()='字幕列表']", 
                "//div[contains(text(), '字幕列表')]",
                "//span[contains(text(), '字幕列表')]",
                "//div[contains(text(), '字幕')]",
                "//span[contains(text(), '字幕')]",
                "//button[contains(text(), '字幕')]",
                "//*[contains(@class, 'tab') and contains(text(), '字幕')]"
            ]
            
            for xpath in xpath_strategies:
                try:
                    elements = driver.find_elements(By.XPATH, xpath)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            # 检查是否在AI面板内（右侧区域）
                            location = element.location
                            window_width = driver.get_window_size()['width']
                            if location['x'] > window_width * 0.4:  # 在右侧
                                print(f"✅ 找到字幕列表标签: '{element.text}' 位置:({location['x']},{location['y']})")
                                subtitle_tab = element
                                break
                    if subtitle_tab:
                        break
                except Exception as e:
                    continue
            
            # 策略2: 在右侧AI面板中查找所有可点击元素
            if not subtitle_tab:
                print("🔎 在右侧AI面板中查找字幕相关元素...")
                try:
                    window_width = driver.get_window_size()['width']
                    # 使用JavaScript查找右侧所有包含字幕的元素
                    right_subtitle_elements = driver.execute_script(f"""
                        var elements = [];
                        var allElements = document.querySelectorAll('*');
                        for (var i = 0; i < allElements.length; i++) {{
                            var elem = allElements[i];
                            var rect = elem.getBoundingClientRect();
                            var text = elem.textContent || '';
                            
                            if (rect.left > {window_width * 0.4} && 
                                (text.includes('字幕列表') || text.includes('字幕')) &&
                                rect.width > 0 && rect.height > 0 &&
                                elem.style.display !== 'none') {{
                                elements.push(elem);
                            }}
                        }}
                        return elements;
                    """)
                    
                    if right_subtitle_elements:
                        subtitle_tab = right_subtitle_elements[0]
                        print(f"✅ 在右侧区域找到字幕元素: '{subtitle_tab.text if hasattr(subtitle_tab, 'text') else 'JavaScript元素'}'")
                        
                except Exception as e:
                    print(f"右侧区域查找失败: {str(e)}")
            
            # 执行点击操作
            if subtitle_tab:
                try:
                    # 检查是否已经激活
                    class_name = subtitle_tab.get_attribute('class') or ''
                    is_active = (
                        '_Active_' in class_name or
                        'active' in class_name.lower() or
                        'selected' in class_name.lower()
                    )
                    
                    if not is_active:
                        print(f"👆 点击字幕列表标签页: '{subtitle_tab.text}'")
                        
                        # 尝试多种点击方式
                        click_success = False
                        click_methods = [
                            ('JavaScript点击', lambda: driver.execute_script("arguments[0].click();", subtitle_tab)),
                            ('直接点击', lambda: subtitle_tab.click()),
                            ('动作链点击', lambda: ActionChains(driver).move_to_element(subtitle_tab).click().perform())
                        ]
                        
                        for method_name, click_action in click_methods:
                            try:
                                click_action()
                                time.sleep(2)  # 等待标签页切换
                                print(f"✅ {method_name}成功")
                                click_success = True
                                break
                            except Exception as e:
                                print(f"❌ {method_name}失败: {str(e)}")
                                continue
                        
                        if not click_success:
                            print("❌ 所有点击方法均失败")
                            return False
                    else:
                        print("✅ 字幕列表标签页已经处于激活状态")
                    
                    return True
                    
                except Exception as e:
                    print(f"点击字幕标签页时出错: {str(e)}")
                    return False
            else:
                print("❌ 未找到字幕列表标签页")
                return False
                
        except Exception as e:
            print(f"切换到字幕列表标签页时出错: {str(e)}")
            return False
    
    def extract_subtitles_with_smart_scroll(self, driver, timeout=30):
        """智能滚动提取所有字幕内容"""
        try:
            import time
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            print("开始智能滚动提取字幕...")
            
            # 首先查找AI面板容器，确保只在AI面板内查找字幕
            ai_panel = None
            ai_panel_selectors = [
                "[data-video-assistant-subject-wrapper]",
                "[class*='VideoAssistant']",
                "[class*='InteractWrapper']",
                "//*[contains(text(), 'AI小助手')]/ancestor::div[contains(@class, 'panel') or contains(@class, 'wrapper') or contains(@class, 'container')][1]"
            ]
            
            for selector in ai_panel_selectors:
                try:
                    if selector.startswith('//'):
                        elements = driver.find_elements(By.XPATH, selector)
                    else:
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for element in elements:
                        if element.is_displayed():
                            # 验证是否包含字幕列表
                            text_content = element.get_attribute('textContent') or ''
                            if '字幕列表' in text_content:
                                ai_panel = element
                                print(f"✅ 找到AI面板容器: {selector}")
                                break
                    if ai_panel:
                        break
                except Exception as e:
                    continue
            
            if not ai_panel:
                print("❌ 未找到AI面板容器")
                return []
            
            # 在AI面板内查找字幕容器
            subtitle_container = None
            container_selectors = [
                '[data-video-assistant-subject-subtitles]',
                '._SubtitlesList_2jiok_1',
                '[class*="_SubtitlesList_"]',
                '[class*="_Subtitles_"]'
            ]
            
            for selector in container_selectors:
                try:
                    subtitle_container = ai_panel.find_element(By.CSS_SELECTOR, selector)
                    if subtitle_container.is_displayed():
                        print(f"✅ 在AI面板内找到字幕容器: {selector}")
                        break
                except:
                    continue
            
            if not subtitle_container:
                # 如果找不到专用容器，就使AI面板本身
                subtitle_container = ai_panel
                print("⚠️ 未找到专用字幕容器，使用AI面板本身")
            
            # 查找可滚动的区域（在AI面板内）
            scrollable_container = None
            scroll_selectors = [
                '[data-video-assistant-subject-content]',
                '._Content_196qs_128',
                '[class*="_Content_"]',
                '[data-video-assistant-subject-subtitles]'
            ]
            
            for selector in scroll_selectors:
                try:
                    scrollable_container = ai_panel.find_element(By.CSS_SELECTOR, selector)
                    if scrollable_container.is_displayed():
                        print(f"✅ 在AI面板内找到可滚动容器: {selector}")
                        break
                except:
                    continue
            
            if not scrollable_container:
                scrollable_container = subtitle_container
                print("⚠️ 使用字幕容器作为滚动容器")
            
            # 收集所有字幕
            all_subtitles = []
            last_subtitle_count = 0
            no_new_content_count = 0
            max_scroll_attempts = 20
            
            print("开始收集字幕内容...")
            
            for scroll_attempt in range(max_scroll_attempts):
                # 在字幕容器内查找字幕项（不是全页面查找）
                subtitle_items = []
                item_selectors = [
                    '._Part_1iu0q_16',
                    '[class*="_Part_"]',
                    '.item',
                    '[class*="subtitle"][class*="item"]',
                    'div[class*="time"]'  # 包含时间的div
                ]
                
                for selector in item_selectors:
                    try:
                        # 关键修改：只在subtitle_container内查找，不是全页面柩找
                        items = subtitle_container.find_elements(By.CSS_SELECTOR, selector)
                        if items:
                            # 过滤掉不相关的元素（比如选集列表）
                            filtered_items = []
                            for item in items:
                                if item.is_displayed():
                                    item_text = item.text.strip()
                                    # 过滤掉明显不是字幕的内容
                                    if (
                                        item_text and 
                                        len(item_text) > 0 and
                                        '选集' not in item_text and
                                        'P' not in item_text or ':' in item_text  # 包含时间或不包含P
                                    ):
                                        filtered_items.append(item)
                            
                            if filtered_items:
                                subtitle_items = filtered_items
                                print(f"   使用选择器 {selector}，找到 {len(subtitle_items)} 个字幕项")
                                break
                    except Exception as e:
                        continue
                
                if not subtitle_items:
                    print(f"   未找到字幕项，尝试直接获取容器内容")
                    # 如果找不到具体的字幕项，直接分析容器内容
                    container_text = subtitle_container.get_attribute('textContent') or ''
                    if container_text:
                        # 简单解析文本内容
                        lines = container_text.split('\n')
                        for line in lines:
                            line = line.strip()
                            if line and ':' in line and len(line) > 5:  # 可能是时间戳+内容
                                if line not in [item['content'] for item in all_subtitles]:
                                    all_subtitles.append({
                                        'time': line.split(' ')[0] if ' ' in line else '00:00',
                                        'content': line
                                    })
                
                # 提取字幕数据
                for item in subtitle_items:
                    try:
                        # 提取时间
                        time_text = ''
                        time_selectors = [
                            '._TimeText_1iu0q_35',
                            '[class*="_TimeText_"]',
                            '[class*="time"]',
                            '.time'
                        ]
                        
                        for time_sel in time_selectors:
                            try:
                                time_element = item.find_element(By.CSS_SELECTOR, time_sel)
                                time_text = time_element.text.strip()
                                break
                            except:
                                continue
                        
                        # 提取内容
                        content_text = ''
                        content_selectors = [
                            '._Text_1iu0q_64',
                            '[class*="_Text_"]',
                            '[class*="content"] span',
                            '.content',
                            'span'
                        ]
                        
                        for content_sel in content_selectors:
                            try:
                                content_element = item.find_element(By.CSS_SELECTOR, content_sel)
                                content_text = content_element.text.strip()
                                break
                            except:
                                continue
                        
                        # 如果没有通过选择器找到内容，尝试直接获取文本
                        if not content_text:
                            item_text = item.text.strip()
                            # 移除时间部分，保留内容
                            if time_text and time_text in item_text:
                                content_text = item_text.replace(time_text, '').strip()
                            else:
                                content_text = item_text
                        
                        # 验证和添加字幕项
                        if time_text and content_text and len(content_text) > 1:
                            subtitle_entry = {
                                'time': time_text,
                                'content': content_text
                            }
                            
                            # 避免重复
                            if subtitle_entry not in all_subtitles:
                                all_subtitles.append(subtitle_entry)
                                
                    except Exception as e:
                        continue
                
                current_count = len(all_subtitles)
                print(f"滚动 {scroll_attempt + 1}/{max_scroll_attempts}: 已收集 {current_count} 条字幕")
                
                # 检查是否有新内容
                if current_count == last_subtitle_count:
                    no_new_content_count += 1
                    if no_new_content_count >= 3:
                        print("连续3次滚动无新内容，结束收集")
                        break
                else:
                    no_new_content_count = 0
                    last_subtitle_count = current_count
                
                # 滚动到下一部分
                try:
                    driver.execute_script(
                        "arguments[0].scrollTop += arguments[0].clientHeight * 0.8;",
                        scrollable_container
                    )
                    time.sleep(0.5)  # 等待内容加载
                except:
                    # 如果滚动失败，尝试其他方式
                    try:
                        driver.execute_script("window.scrollBy(0, 300);")
                        time.sleep(0.5)
                    except:
                        break
            
            print(f"✅ 字幕收集完成，共获取 {len(all_subtitles)} 条字幕")
            
            # 转换为标准格式
            if all_subtitles:
                return self.convert_ai_subtitles_to_standard_format(all_subtitles)
            else:
                return []
                
        except Exception as e:
            print(f"智能滚动提取字幕时出错: {str(e)}")
            return []
    
    def convert_ai_subtitles_to_standard_format(self, subtitle_entries):
        """将AI字幕转换为标准格式"""
        try:
            if not subtitle_entries:
                return []
            
            # 创建标准字幕格式
            subtitle_item = {
                'lan': 'ai-zh',
                'lan_doc': 'AI智能字幕',
                'subtitle_url': '',
                'body': []
            }
            
            for entry in subtitle_entries:
                try:
                    time_str = entry['time']
                    content = entry['content']
                    
                    # 解析时间（格式如 "00:01", "01:25" 等）
                    time_parts = time_str.split(':')
                    if len(time_parts) >= 2:
                        minutes = int(time_parts[0])
                        seconds = int(time_parts[1])
                        start_time = minutes * 60 + seconds
                        end_time = start_time + 3  # 假设每条字幕持续3秒
                        
                        subtitle_item['body'].append({
                            'from': start_time,
                            'to': end_time,
                            'content': content
                        })
                except Exception as e:
                    print(f"处理字幕项时出错: {e}")
                    continue
            
            if subtitle_item['body']:
                print(f"转换完成: {len(subtitle_item['body'])} 条有效字幕")
                return [subtitle_item]
            else:
                return []
                
        except Exception as e:
            print(f"转换字幕格式时出错: {str(e)}")
            return []
    
    def find_subtitle_list_button(self, driver, ai_panel):
        """在AI弹窗中查找字幕列表按钮"""
        from selenium.webdriver.common.by import By
        
        try:
            print("在AI弹窗中查找字幕列表按钮...")
            
            # 在AI弹窗内查找字幕相关按钮
            subtitle_selectors = [
                # 直接按文本查找
                ".//button[contains(text(), '字幕')]",
                ".//button[contains(text(), '文本')]", 
                ".//button[contains(text(), '列表')]",
                ".//span[contains(text(), '字幕列表')]",
                ".//div[contains(text(), '视频文本')]",
                # 按类名查找
                ".//button[contains(@class, 'subtitle')]",
                ".//button[contains(@class, 'transcript')]",
                ".//button[contains(@class, 'text')]",
                ".//div[contains(@class, 'tab')]",
                ".//li[contains(@class, 'tab')]",
                # 更广泛的查找
                ".//button", ".//a", ".//div[@role='button']", ".//span[@role='button']"
            ]
            
            for selector in subtitle_selectors:
                try:
                    elements = ai_panel.find_elements(By.XPATH, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            text = (element.get_attribute('textContent') or 
                                   element.get_attribute('aria-label') or 
                                   element.text or '').strip()
                            
                            # 检查是否包含字幕相关关键词
                            subtitle_keywords = ['字幕', '文本', '列表', 'transcript', 'subtitle', 'text', '内容']
                            if any(keyword in text.lower() for keyword in subtitle_keywords):
                                print(f"找到字幕按钮: {text[:30]}")
                                return element
                                
                except Exception:
                    continue
            
            # 如果找不到专用按钮，尝试找第一个可点击的元素
            try:
                clickable_elements = ai_panel.find_elements(By.XPATH, ".//button | .//a | .//*[@role='button']")
                for element in clickable_elements:
                    if element.is_displayed() and element.is_enabled():
                        text = element.get_attribute('textContent') or ''
                        if len(text.strip()) > 0:
                            print(f"尝试使用可点击元素: {text[:20]}")
                            return element
            except Exception:
                pass
            
            print("未在AI弹窗中找到字幕列表按钮")
            return None
            
        except Exception as e:
            print(f"查找字幕按钮时出错: {str(e)}")
            return None
    
    def click_subtitle_list(self, driver, subtitle_button):
        """点击字幕列表按钮"""
        import time
        from selenium.webdriver.common.action_chains import ActionChains
        
        try:
            # 确保按钮可见
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", subtitle_button)
            time.sleep(1)
            
            # 尝试多种点击方式
            click_methods = [
                lambda: subtitle_button.click(),
                lambda: driver.execute_script("arguments[0].click();", subtitle_button),
                lambda: ActionChains(driver).move_to_element(subtitle_button).click().perform()
            ]
            
            for i, click_method in enumerate(click_methods):
                try:
                    print(f"尝试点击字幕按钮方式 {i+1}...")
                    click_method()
                    time.sleep(2)
                    print("字幕按钮点击成功")
                    return True
                except Exception as e:
                    print(f"点击方式 {i+1} 失败: {str(e)}")
                    continue
            
            return False
            
        except Exception as e:
            print(f"点击字幕按钮时出错: {str(e)}")
            return False
    

    
    def extract_all_subtitles_with_scroll(self, driver, ai_panel):
        """在AI弹窗中滚动获取所有字幕内容"""
        import time
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.keys import Keys
        
        try:
            print("开始提取字幕内容...")
            
            # 查找AI弹窗中的字幕容器
            subtitle_container = self.find_subtitle_container_in_panel(driver, ai_panel)
            if not subtitle_container:
                print("未找到字幕容器")
                return None
            
            all_subtitles = []
            seen_texts = set()
            previous_content_length = 0
            no_new_content_count = 0
            
            print("开始滚动获取字幕...")
            
            # 最多滚动20次
            for scroll_attempt in range(20):
                try:
                    # 获取当前可见的字幕内容
                    current_subtitles = self.extract_subtitle_items_from_container(subtitle_container)
                    
                    new_items_count = 0
                    for subtitle in current_subtitles:
                        if subtitle['text'] not in seen_texts and len(subtitle['text'].strip()) > 5:
                            all_subtitles.append(subtitle)
                            seen_texts.add(subtitle['text'])
                            new_items_count += 1
                    
                    print(f"第{scroll_attempt + 1}次滚动: 新增{new_items_count}条，总计{len(all_subtitles)}条")
                    
                    # 检查是否连续多次没有新内容
                    if new_items_count == 0:
                        no_new_content_count += 1
                        if no_new_content_count >= 3:
                            print("连续3次没有新内容，停止滚动")
                            break
                    else:
                        no_new_content_count = 0
                    
                    # 尝试多种滚动方式
                    scroll_success = self.scroll_subtitle_container(driver, subtitle_container)
                    if not scroll_success:
                        print(f"滚动失败，停止在第{scroll_attempt + 1}次")
                        break
                    
                    time.sleep(2)  # 等待内容加载
                    
                except Exception as e:
                    print(f"滚动过程中出错: {str(e)}")
                    break
            
            print(f"滚动完成，共获取{len(all_subtitles)}条字幕")
            return all_subtitles if all_subtitles else None
            
        except Exception as e:
            print(f"提取字幕时出错: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def find_subtitle_container_in_panel(self, driver, ai_panel):
        """在AI弹窗中查找字幕容器"""
        from selenium.webdriver.common.by import By
        
        try:
            # 定义可能的字幕容器选择器
            container_selectors = [
                ".//div[contains(@class, 'subtitle')]",
                ".//div[contains(@class, 'transcript')]", 
                ".//div[contains(@class, 'text-list')]",
                ".//div[contains(@class, 'content-list')]",
                ".//ul", ".//ol", ".//div[contains(@class, 'list')]",
                ".//div[@role='list']", ".//div[contains(@class, 'scroll')]",
                ".//div[contains(@class, 'overflow')]"
            ]
            
            for selector in container_selectors:
                try:
                    elements = ai_panel.find_elements(By.XPATH, selector)
                    for element in elements:
                        if element.is_displayed():
                            # 检查元素是否包含字幕内容
                            text_content = element.get_attribute('textContent') or ''
                            child_count = len(element.find_elements(By.XPATH, ".//*"))
                            
                            # 判断标准：包含多个子元素且有足够的文本内容
                            if child_count > 3 and len(text_content) > 100:
                                print(f"找到字幕容器: {child_count}个子元素，{len(text_content)}个字符")
                                return element
                except Exception:
                    continue
            
            # 如果找不到专用容器，使用整个AI弹窗
            print("未找到专用字幕容器，使用整个弹窗")
            return ai_panel
            
        except Exception as e:
            print(f"查找字幕容器时出错: {str(e)}")
            return ai_panel
    
    def extract_subtitle_items_from_container(self, container):
        """从容器中提取字幕项"""
        from selenium.webdriver.common.by import By
        
        subtitles = []
        
        try:
            # 定义字幕项的可能选择器
            item_selectors = [
                ".//li", ".//p", ".//div[contains(@class, 'item')]",
                ".//div[contains(@class, 'line')]", ".//div[contains(@class, 'sentence')]",
                ".//span[contains(@class, 'text')]", ".//div[contains(@class, 'segment')]"
            ]
            
            for selector in item_selectors:
                try:
                    elements = container.find_elements(By.XPATH, selector)
                    for element in elements:
                        if element.is_displayed():
                            text = (element.get_attribute('textContent') or 
                                   element.text or '').strip()
                            
                            # 过滤有效的字幕文本
                            if (len(text) > 5 and 
                                not text.isdigit() and  # 排除纯数字
                                '中文' in text or '英文' in text or  # 包含中文或英文
                                any(char.isalpha() or '\u4e00' <= char <= '\u9fff' for char in text)):  # 包含字母或中文字符
                                
                                timestamp = self.extract_timestamp_from_element(element)
                                subtitles.append({
                                    'text': text,
                                    'timestamp': timestamp,
                                    'element': element
                                })
                    
                    if subtitles:  # 如果找到了，停止尝试其他选择器
                        break
                        
                except Exception:
                    continue
            
            return subtitles
            
        except Exception as e:
            print(f"提取字幕项时出错: {str(e)}")
            return []
    
    def scroll_subtitle_container(self, driver, container):
        """滚动字幕容器"""
        try:
            from selenium.webdriver.common.keys import Keys
            
            # 尝试多种滚动方式
            scroll_methods = [
                lambda: driver.execute_script("arguments[0].scrollTop += 500;", container),
                lambda: driver.execute_script("arguments[0].scrollBy(0, 500);", container),
                lambda: driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", container),
                lambda: container.send_keys(Keys.PAGE_DOWN) if hasattr(container, 'send_keys') else None
            ]
            
            for i, scroll_method in enumerate(scroll_methods):
                try:
                    if scroll_method:
                        scroll_method()
                        return True
                except Exception:
                    continue
            
            return False
            
        except Exception:
            return False
    
    def extract_timestamp_from_element(self, element):
        """从元素中提取时间戳"""
        try:
            # 尝试从各种属性中获取时间信息
            time_attrs = ['data-time', 'data-timestamp', 'data-start', 'time']
            for attr in time_attrs:
                time_value = element.get_attribute(attr)
                if time_value:
                    try:
                        return float(time_value)
                    except ValueError:
                        continue
            
            # 尝试从文本中提取时间格式 (00:00:00)
            text = element.get_attribute('textContent') or ''
            import re
            time_pattern = r'(\d{1,2}):(\d{2}):(\d{2})'
            match = re.search(time_pattern, text)
            if match:
                hours, minutes, seconds = map(int, match.groups())
                return hours * 3600 + minutes * 60 + seconds
            
            # 如果找不到时间，返回0
            return 0.0
            
        except Exception:
            return 0.0
    

    

    
    def extract_timestamp_from_text(self, text):
        """从文本中提取时间戳"""
        try:
            import re
            # 匹配 mm:ss 或 hh:mm:ss 格式
            pattern = r'(\d{1,2}):(\d{2})(?::(\d{2}))?'
            match = re.search(pattern, text)
            if match:
                if match.group(3):  # hh:mm:ss
                    h, m, s = int(match.group(1)), int(match.group(2)), int(match.group(3))
                    return h * 3600 + m * 60 + s
                else:  # mm:ss
                    m, s = int(match.group(1)), int(match.group(2))
                    return m * 60 + s
        except Exception:
            pass
        return 0
    
    def format_ai_subtitles(self, subtitles):
        """格式化AI字幕为标准格式"""
        try:
            if not subtitles:
                return None
            
            formatted_subtitles = []
            duration = 3.0  # 每条字幕3秒
            
            subtitle_item = {
                'lan': 'ai-zh',
                'lan_doc': 'AI中文字幕',
                'subtitle_url': '',
                'body': []
            }
            
            for i, subtitle in enumerate(subtitles):
                start_time = subtitle.get('timestamp', i * duration)
                end_time = start_time + duration
                
                subtitle_item['body'].append({
                    'from': start_time,
                    'to': end_time,
                    'content': subtitle['text']
                })
            
            formatted_subtitles.append(subtitle_item)
            return formatted_subtitles
            
        except Exception as e:
            print(f"格式化字幕旷出错: {str(e)}")
            return None




def main():
    """主函数 - 命令行接口"""
    parser = argparse.ArgumentParser(description='B站视频字幕提取工具 v2.0 - 增强版')
    parser.add_argument('url', nargs='?', help='B站视频URL')
    parser.add_argument('-o', '--output', default='./subtitles', help='输出目录 (默认: ./subtitles)')
    parser.add_argument('-p', '--page', type=int, default=1, help='多P视频的页面号 (默认: 1)')
    parser.add_argument('--ai', action='store_true', help='使用AI小助手字幕')
    parser.add_argument('--speech', action='store_true', help='使用语音识别提取字幕')
    parser.add_argument('--model', default='base', choices=['tiny', 'base', 'small', 'medium', 'large'], 
                       help='Whisper模型大小 (默认: base)')
    parser.add_argument('--check-deps', action='store_true', help='检查依赖工具')
    parser.add_argument('--fix-numpy', action='store_true', help='修复NumPy兼容性问题')
    parser.add_argument('--start-edge', action='store_true', help='启动Edge调试模式')
    
    args = parser.parse_args()
    
    # 创建提取器实例
    extractor = BilibiliSubtitleExtractor(args.output)
    extractor.print_banner()
    
    # 修复NumPy兼容性
    if args.fix_numpy:
        print("启动NumPy兼容性修复...")
        import subprocess
        subprocess.run([sys.executable, 'fix_numpy_compatibility.py'])
        return
    
    # 启动Edge调试模式
    if args.start_edge:
        print("启动Edge调试模式...")
        import subprocess
        import os
        batch_file = os.path.join(os.path.dirname(__file__), '启动Edge调试模式.bat')
        if os.path.exists(batch_file):
            subprocess.run([batch_file], shell=True)
        else:
            print("警告: 找不到启动脚本，手动运行 Edge 并加上参数:")
            print("msedge.exe --remote-debugging-port=9222 --user-data-dir=\"%USERPROFILE%\\AppData\\Local\\Microsoft\\Edge\\User Data\"")
        return
    
    # 检查依赖
    if args.check_deps:
        print("检查依赖工具...")
        missing = check_dependencies_v2()
        if missing:
            print(f"\n缺少以下依赖工具: {', '.join(missing)}")
            print("请先安装缺少的工具后再运行程序")
            print("可以运行: install_dependencies.bat")
            return
        else:
            print("\n所有依赖工具都已安装!")
            return
    
    # 检查URL参数
    if not args.url:
        print("错误: 请提供视频URL")
        print("示例: python bilibili_subtitle_extractor_v2.py --ai 'https://www.bilibili.com/video/BV1xx411c7mD'")
        return
    
    try:
        if args.speech:
            print("使用语音识别模式...")
            result = extractor.extract_subtitle_with_speech_recognition(args.url, args.model)
            if result:
                print(f"\n✓ 字幕提取成功!")
                print(f"保存位置: {result}")
            else:
                print("\n✗ 字幕提取失败")
                sys.exit(1)
        else:
            # 默认使用AI模式（v2版本主要特性）
            print("使用AI小助手模式...")
            success = extractor.extract_subtitle_from_url(args.url, args.page, use_ai=True)
            if success:
                print(f"\n✓ 字幕提取成功!")
                print(f"保存目录: {extractor.output_dir}")
            else:
                print("\n✗ AI字幕提取失败，尝试使用语音识别模式:")
                print(f"python bilibili_subtitle_extractor_v2.py --speech '{args.url}'")
                sys.exit(1)
                
    except KeyboardInterrupt:
        print("\n\n用户取消操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n程序运行出错: {str(e)}")
        if "NumPy" in str(e):
            print("建议运行: python fix_numpy_compatibility.py")
        sys.exit(1)


def check_dependencies_v2():
    """检查v2版本依赖"""
    missing = []
    
    # 检查NumPy版本
    try:
        import numpy as np
        if np.__version__.startswith('2.'):
            print("⚠️  检测到NumPy 2.x，可能与Whisper不兼容")
            print("请运行: python fix_numpy_compatibility.py")
    except ImportError:
        missing.append('numpy')
    
    # 检查其他依赖
    for module, package in [('whisper', 'openai-whisper'), ('yt_dlp', 'yt-dlp'), ('selenium', 'selenium')]:
        try:
            __import__(module)
            print(f"✓ {module}: 已安装")
        except ImportError:
            print(f"✗ {module}: 未安装")
            missing.append(package)
    
    # 检查FFmpeg
    ffmpeg_path = r"D:\ffmpeg-7.1.1-essentials_build\ffmpeg-7.1.1-essentials_build\bin\ffmpeg.exe"
    if os.path.exists(ffmpeg_path):
        print(f"✓ FFmpeg: 找到指定路径")
    else:
        print(f"⚠️  FFmpeg: 指定路径不存在")
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            print(f"✓ FFmpeg: 在环境变量中找到")
        except:
            missing.append('ffmpeg')
    
    return missing


if __name__ == "__main__":
    main()
