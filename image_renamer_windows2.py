#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片批量重命名工具
适用于Windows系统
"""

import os
import re
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from pathlib import Path

# 添加调试信息
print(f"Python版本: {sys.version}")
print(f"运行平台: {sys.platform}")

try:
    from PIL import Image, ImageTk
    print("PIL/Pillow 导入成功")
except ImportError as e:
    print(f"PIL/Pillow 导入失败: {e}")
    messagebox.showerror("错误", "缺少必要的图片处理库 Pillow\n请运行: pip install pillow")
    sys.exit(1)

class ImageRenamerApp:
    def __init__(self, root):
        self.root = root
        self.setup_ui()
        self.selected_folder = None
        
        # 定义重命名规则 - 按照最新的顺序（1-29）
        self.rename_rules = [
            "_58_右侧面.jpg",
            "_3_右前45度.jpg",
            "_2_正前方.jpg",
            "_36_左前大灯.jpg",
            "_1_左前45度.jpg",
            "_35_左前轮胎轮毂.jpg",
            "_4_左侧面.jpg",
            "_5_左后45度.jpg",
            "_6_正后方.jpg",
            "_7_右后45度.jpg",
            "_9_右后大灯.jpg",
            "_29_右侧底大边.jpg",
            "_30_左侧底大边.jpg",
            "_57_车顶.jpg",
            "_20_驾驶位.jpg",
            "_19_驾驶员座椅.jpg",
            "_21_后排.jpg",
            "_23_后备箱.jpg",
            "_24_发动机舱.jpg",
            "_41_右侧前座椅.jpg",
            "_44_右侧后座椅.jpg",
            "_12_中控台.jpg",
            "_22_车内顶棚.jpg",
            "_16_音响及空调面板.jpg",
            "_13_方向盘.jpg",
            "_14_组合仪表.jpg",
            "_15_里程数特写.jpg",
            "_18_变速杆.jpg",
            "_11_钥匙.jpg"
        ]
    
    def setup_ui(self):
        """设置用户界面"""
        self.root.title("图片批量重命名工具 - Windows版")
        self.root.geometry("800x800")
        
        # 设置macOS风格 - 添加异常处理
        try:
            if self.root.tk.call('tk', 'windowingsystem') == 'aqua':
                self.root.configure(bg='#f0f0f0')
        except Exception:
            # 如果macOS样式设置失败，使用默认样式
            pass
        
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 标题 - 使用跨平台字体
        try:
            # 尝试使用macOS系统字体
            title_font = ('SF Pro Display', 24, 'bold')
            title_label = ttk.Label(main_frame, text="图片批量重命名工具", font=title_font)
        except Exception:
            # 如果系统字体不可用，使用默认字体
            title_label = ttk.Label(main_frame, text="图片批量重命名工具", 
                                   font=('Helvetica', 24, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 30))
        
        # 文件夹选择区域
        folder_frame = ttk.LabelFrame(main_frame, text="选择文件夹", padding="15")
        folder_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        folder_frame.columnconfigure(1, weight=1)
        
        ttk.Label(folder_frame, text="目标文件夹:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        self.folder_var = tk.StringVar()
        self.folder_entry = ttk.Entry(folder_frame, textvariable=self.folder_var, 
                                     state='readonly', width=50)
        self.folder_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        self.browse_btn = ttk.Button(folder_frame, text="浏览", command=self.browse_folder)
        self.browse_btn.grid(row=0, column=2)
        
        # 处理选项区域
        options_frame = ttk.LabelFrame(main_frame, text="处理选项", padding="15")
        options_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # 第一行：重命名选项
        self.rename_enable_var = tk.BooleanVar()
        self.rename_enable_var.set(True)  # 默认启用重命名
        self.rename_enable_check = ttk.Checkbutton(options_frame, text="启用重命名", 
                                                   variable=self.rename_enable_var)
        self.rename_enable_check.grid(row=0, column=0, sticky=tk.W, padx=(0, 20), pady=(0, 10))
        
        # 第二行：压缩选项
        self.compress_var = tk.BooleanVar()
        self.compress_var.set(False)  # 默认不启用压缩
        self.compress_check = ttk.Checkbutton(options_frame, text="启用压缩（压缩到 1800×1800 像素）", 
                                            variable=self.compress_var,
                                            command=self.toggle_quality_controls)
        self.compress_check.grid(row=1, column=0, sticky=tk.W, padx=(0, 20))
        
        # 质量选项
        ttk.Label(options_frame, text="压缩质量:").grid(row=1, column=1, sticky=tk.W, padx=(0, 10))
        self.quality_var = tk.IntVar()
        self.quality_var.set(85)  # 默认质量85%
        self.quality_scale = ttk.Scale(options_frame, from_=60, to=95, 
                                     variable=self.quality_var, orient=tk.HORIZONTAL, length=150)
        self.quality_scale.grid(row=1, column=2, sticky=tk.W, padx=(0, 10))
        
        self.quality_label = ttk.Label(options_frame, text="85%")
        self.quality_label.grid(row=1, column=3, sticky=tk.W)
        
        # 绑定质量滑块事件
        self.quality_scale.configure(command=self.update_quality_label)
        
        # 初始化质量控件状态
        self.toggle_quality_controls()
        
        # 预览区域
        preview_frame = ttk.LabelFrame(main_frame, text="预览", padding="15")
        preview_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)
        
        # 创建Treeview用于显示预览
        self.tree = ttk.Treeview(preview_frame, columns=('original', 'new'), show='headings', height=15)
        self.tree.heading('original', text='原文件名')
        self.tree.heading('new', text='新文件名')
        self.tree.column('original', width=300)
        self.tree.column('new', width=300)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=20)
        
        self.preview_btn = ttk.Button(button_frame, text="预览重命名", 
                                     command=self.preview_rename, state='disabled')
        self.preview_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.rename_btn = ttk.Button(button_frame, text="开始重命名", 
                                    command=self.start_rename, state='disabled')
        self.rename_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.clear_btn = ttk.Button(button_frame, text="清空", command=self.clear_preview)
        self.clear_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.exit_btn = ttk.Button(button_frame, text="退出", command=self.exit_app)
        self.exit_btn.pack(side=tk.LEFT)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, 
                                          maximum=100, length=400)
        self.progress_bar.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # 状态标签
        self.status_var = tk.StringVar()
        self.status_var.set("请选择第二层文件夹，程序会批量处理其中所有子文件夹的图片")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var)
        self.status_label.grid(row=6, column=0, columnspan=3, pady=(10, 0))
    
    def browse_folder(self):
        """浏览文件夹"""
        try:
            # 使用中文提示
            folder = filedialog.askdirectory(
                title="选择第二层文件夹（会批量处理其中所有子文件夹）",
                mustexist=True
            )
            if folder:
                # 检查文件夹权限
                if not os.access(folder, os.R_OK):
                    messagebox.showerror("错误", f"没有读取权限: {folder}")
                    return
                
                self.selected_folder = folder
                # 显示完整路径（支持中文）
                self.folder_var.set(folder)
                self.preview_btn.config(state='normal')
                self.status_var.set(f"已选择文件夹: {os.path.basename(folder)}")
                print(f"选择的文件夹: {folder}")
        except Exception as e:
            messagebox.showerror("错误", f"选择文件夹时发生错误: {str(e)}")
            print(f"浏览文件夹错误: {e}")
    
    def update_quality_label(self, value):
        """更新质量标签"""
        quality = int(float(value))
        self.quality_label.config(text=f"{quality}%")
    
    def toggle_quality_controls(self):
        """切换质量控件的启用状态"""
        if self.compress_var.get():
            self.quality_scale.config(state='normal')
        else:
            self.quality_scale.config(state='disabled')
    
    def compress_image(self, input_path, output_path, target_size=(1800, 1800), quality=85):
        """压缩图片到指定尺寸（不旋转）"""
        try:
            with Image.open(input_path) as img:
                # 不处理EXIF方向，保持原始方向
                
                # 转换为RGB模式（如果是RGBA或其他模式）
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 计算缩放比例，保持宽高比
                img_width, img_height = img.size
                target_width, target_height = target_size
                
                # 计算缩放比例
                scale = min(target_width / img_width, target_height / img_height)
                
                # 如果图片已经小于目标尺寸，不放大
                if scale > 1:
                    scale = 1
                
                # 计算新尺寸
                new_width = int(img_width * scale)
                new_height = int(img_height * scale)
                
                # 缩放图片 - 兼容旧版本PIL
                try:
                    img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                except AttributeError:
                    # 旧版本PIL使用ANTIALIAS
                    img_resized = img.resize((new_width, new_height), Image.ANTIALIAS)
                
                # 创建目标尺寸的白色背景
                background = Image.new('RGB', target_size, (255, 255, 255))
                
                # 计算居中位置
                x = (target_width - new_width) // 2
                y = (target_height - new_height) // 2
                
                # 将缩放后的图片粘贴到背景上
                background.paste(img_resized, (x, y))
                
                # 保存压缩后的图片
                background.save(output_path, 'JPEG', quality=quality, optimize=True)
                
                return True
        except Exception as e:
            print(f"压缩图片失败 {input_path}: {e}")
            return False
    
    def extract_number_from_folder_name(self, folder_name):
        """
        从第三层文件夹名称中提取车源号
        格式: 车源号_车辆名
        例如: 1234567_英菲尼迪G37
        """
        # 匹配模式: 数字_车辆名
        pattern = r'^(\d+)_'
        match = re.match(pattern, folder_name)
        if match:
            return match.group(1)
        return None
    
    def natural_sort_key(self, text):
        """
        自然排序键函数 - Windows版本
        将 '1.jpg', '2.jpg', '10.jpg' 正确排序为 1, 2, 10
        而不是字符串排序的 1, 10, 2
        """
        def atoi(text):
            return int(text) if text.isdigit() else text.lower()
        
        return [atoi(c) for c in re.split(r'(\d+)', text)]
    
    def get_jpg_files_in_folder(self, folder_path):
        """
        获取文件夹中的所有jpg文件
        Windows版本：按照文件名的自然顺序排序
        """
        jpg_files = []
        try:
            for file in os.listdir(folder_path):
                # 支持更多图片格式，忽略隐藏文件
                if (not file.startswith('.') and 
                    file.lower().endswith(('.jpg', '.jpeg'))):
                    jpg_files.append(file)
        except PermissionError:
            print(f"权限错误：无法访问文件夹 {folder_path}")
            return []
        except Exception as e:
            print(f"读取文件夹错误 {folder_path}: {e}")
            return []
        
        # Windows版本：使用自然排序（按文件名）
        jpg_files.sort(key=self.natural_sort_key)
        
        # 调试输出 - 显示排序后的文件顺序
        if jpg_files:
            print(f"\n文件夹 '{os.path.basename(folder_path)}' 中的图片顺序（按文件名自然排序）:")
            for i, f in enumerate(jpg_files, 1):
                print(f"  {i}. {f}")
        
        return jpg_files  
  
    def extract_folder_info(self, folder_name):
        """
        从第二层文件夹名称中提取信息
        格式: 2025_11_06_芜湖_张三01
        返回: 张三01 (作为车源号)
        """
        # 匹配模式: 年_月_日_城市_名称
        pattern = r'^\d{4}_\d{1,2}_\d{1,2}_[^_]+_(.+)$'
        match = re.match(pattern, folder_name)
        if match:
            return match.group(1)
        return None
    
    def preview_rename(self):
        """预览重命名结果"""
        if not self.selected_folder:
            messagebox.showerror("错误", "请先选择文件夹")
            return
        
        # 清空之前的预览
        self.clear_preview()
        
        try:
            # 检查是否有子文件夹
            print(f"\n正在扫描文件夹: {self.selected_folder}")
            all_items = os.listdir(self.selected_folder)
            print(f"文件夹中的所有项目: {all_items}")
            
            subfolders = []
            for item in all_items:
                item_path = os.path.join(self.selected_folder, item)
                is_dir = os.path.isdir(item_path)
                is_hidden = item.startswith('.')
                print(f"  - {item}: 是文件夹={is_dir}, 是隐藏={is_hidden}")
                if is_dir and not is_hidden:
                    subfolders.append(item)
            
            print(f"检测到的子文件夹: {subfolders}")
            
            total_files = 0
            preview_data = []
            warnings = []
            
            # 模式1: 如果有子文件夹，处理子文件夹（第三层：车源号_车辆名）
            if subfolders:
                print("检测到子文件夹，使用模式1：处理子文件夹")
                for subfolder in subfolders:
                    subfolder_path = os.path.join(self.selected_folder, subfolder)
                    
                    # 提取车源号
                    number = self.extract_number_from_folder_name(subfolder)
                    if not number:
                        warnings.append(f"无法从文件夹名 '{subfolder}' 中提取车源号（格式应为：车源号_车辆名）")
                        continue
                    
                    # 获取jpg文件
                    jpg_files = self.get_jpg_files_in_folder(subfolder_path)
                    
                    if len(jpg_files) != 29:
                        warnings.append(f"文件夹 '{subfolder}' 中有 {len(jpg_files)} 张图片，不是29张")
                        continue
                    
                    # 生成重命名预览
                    for i, original_file in enumerate(jpg_files):
                        if i < len(self.rename_rules):
                            new_name = f"{number}{self.rename_rules[i]}"
                            preview_data.append({
                                'folder': subfolder,
                                'original': original_file,
                                'new': new_name,
                                'original_path': os.path.join(subfolder_path, original_file),
                                'new_path': os.path.join(subfolder_path, new_name)
                            })
                            total_files += 1
            
            # 模式2: 如果没有子文件夹，提示用户
            else:
                print("未检测到子文件夹")
                folder_name = os.path.basename(self.selected_folder)
                
                messagebox.showerror("错误", 
                    f"选择的文件夹中没有子文件夹！\n\n"
                    f"当前选择: {folder_name}\n\n"
                    f"正确的文件夹结构应该是：\n"
                    f"第二层文件夹（你选择的）/\n"
                    f"  └── 第三层文件夹（车源号_车辆名）/\n"
                    f"      ├── 1.jpg\n"
                    f"      ├── 2.jpg\n"
                    f"      └── ...\n\n"
                    f"例如：\n"
                    f"2025_11_06_芜湖_张三01/\n"
                    f"  ├── 1234567_英菲尼迪G37/\n"
                    f"  ├── 7654321_宝马X5/\n"
                    f"  └── 9999999_奔驰C200/\n\n"
                    f"请检查文件夹结构是否正确！")
                return
                
                # 获取jpg文件
                jpg_files = self.get_jpg_files_in_folder(self.selected_folder)
                
                if len(jpg_files) == 0:
                    messagebox.showwarning("警告", "当前文件夹中没有找到图片文件")
                    return
                
                if len(jpg_files) != 29:
                    result = messagebox.askyesno("警告", 
                        f"当前文件夹中有 {len(jpg_files)} 张图片，不是29张\n是否继续？")
                    if not result:
                        return
                
                # 生成重命名预览
                for i, original_file in enumerate(jpg_files):
                    if i < len(self.rename_rules):
                        new_name = f"{number}{self.rename_rules[i]}"
                        preview_data.append({
                            'folder': '',  # 当前文件夹，不显示子文件夹名
                            'original': original_file,
                            'new': new_name,
                            'original_path': os.path.join(self.selected_folder, original_file),
                            'new_path': os.path.join(self.selected_folder, new_name)
                        })
                        total_files += 1
            
            # 显示预览数据
            for data in preview_data:
                if data['folder']:
                    original_display = f"{data['folder']}/{data['original']}"
                    new_display = f"{data['folder']}/{data['new']}"
                else:
                    original_display = data['original']
                    new_display = data['new']
                
                self.tree.insert('', 'end', values=(original_display, new_display))
            
            self.preview_data = preview_data
            self.rename_btn.config(state='normal' if preview_data else 'disabled')
            
            # 显示状态和警告
            if warnings:
                warning_msg = "\n".join(warnings[:5])  # 只显示前5个警告
                if len(warnings) > 5:
                    warning_msg += f"\n... 还有 {len(warnings)-5} 个警告"
                messagebox.showwarning("警告", warning_msg)
            
            self.status_var.set(f"预览完成，共 {total_files} 个文件待处理")
            
        except Exception as e:
            messagebox.showerror("错误", f"预览时发生错误: {str(e)}")
            self.status_var.set("预览失败")
    
    def clear_preview(self):
        """清空预览"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.rename_btn.config(state='disabled')
        self.preview_data = []
        self.progress_var.set(0)
    
    def start_rename(self):
        """开始处理"""
        if not hasattr(self, 'preview_data') or not self.preview_data:
            messagebox.showerror("错误", "请先预览重命名结果")
            return
        
        # 检查是否至少选择了一个操作
        if not self.rename_enable_var.get() and not self.compress_var.get():
            messagebox.showerror("错误", "请至少勾选一个操作（重命名或压缩）")
            return
        
        # 确认对话框
        operations = []
        if self.rename_enable_var.get():
            operations.append("重命名")
        if self.compress_var.get():
            quality = int(self.quality_var.get())
            operations.append(f"压缩到1800×1800像素（质量{quality}%）")
        
        operation_text = "、".join(operations)
        
        result = messagebox.askyesno("确认", 
                                   f"确定要对 {len(self.preview_data)} 个文件执行以下操作吗？\n\n{operation_text}\n\n此操作不可撤销！")
        if not result:
            return
        
        # 在新线程中执行处理
        self.rename_btn.config(state='disabled')
        self.preview_btn.config(state='disabled')
        
        thread = threading.Thread(target=self.perform_rename)
        thread.daemon = True
        thread.start()
    
    def perform_rename(self):
        """执行处理操作（重命名和/或压缩）"""
        try:
            total = len(self.preview_data)
            success_count = 0
            error_count = 0
            errors = []
            
            rename_enabled = self.rename_enable_var.get()
            compress_enabled = self.compress_var.get()
            
            for i, data in enumerate(self.preview_data):
                try:
                    # 检查原文件是否存在
                    if not os.path.exists(data['original_path']):
                        errors.append(f"文件不存在: {data['original_path']}")
                        error_count += 1
                        continue
                    
                    # 根据用户选择执行不同的操作
                    if compress_enabled and rename_enabled:
                        # 压缩并重命名
                        if os.path.exists(data['new_path']):
                            errors.append(f"目标文件已存在: {data['new_path']}")
                            error_count += 1
                            continue
                        
                        quality = int(self.quality_var.get())
                        if self.compress_image(data['original_path'], data['new_path'], 
                                             target_size=(1800, 1800), quality=quality):
                            os.remove(data['original_path'])
                            success_count += 1
                        else:
                            errors.append(f"压缩失败: {data['original']}")
                            error_count += 1
                    
                    elif compress_enabled and not rename_enabled:
                        # 只压缩，不重命名（覆盖原文件）
                        import tempfile
                        temp_path = data['original_path'] + '.tmp'
                        quality = int(self.quality_var.get())
                        if self.compress_image(data['original_path'], temp_path, 
                                             target_size=(1800, 1800), quality=quality):
                            os.remove(data['original_path'])
                            os.rename(temp_path, data['original_path'])
                            success_count += 1
                        else:
                            if os.path.exists(temp_path):
                                os.remove(temp_path)
                            errors.append(f"压缩失败: {data['original']}")
                            error_count += 1
                    
                    elif rename_enabled and not compress_enabled:
                        # 只重命名，不压缩
                        if os.path.exists(data['new_path']):
                            errors.append(f"目标文件已存在: {data['new_path']}")
                            error_count += 1
                            continue
                        
                        os.rename(data['original_path'], data['new_path'])
                        success_count += 1
                    
                except Exception as e:
                    errors.append(f"处理失败 {data['original']}: {str(e)}")
                    error_count += 1
                
                # 更新进度条
                progress = (i + 1) / total * 100
                self.root.after(0, lambda p=progress: self.progress_var.set(p))
                
                # 更新状态显示
                operations = []
                if compress_enabled:
                    operations.append("压缩")
                if rename_enabled:
                    operations.append("重命名")
                operation_text = "和".join(operations)
                status_text = f"正在{operation_text}... {i+1}/{total}"
                self.root.after(0, lambda text=status_text: self.status_var.set(text))
            
            # 完成后的处理
            self.root.after(0, self.rename_completed, success_count, error_count, errors)
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("错误", f"处理过程中发生错误: {str(e)}"))
            self.root.after(0, self.reset_buttons)
    
    def rename_completed(self, success_count, error_count, errors):
        """处理完成后的处理"""
        self.progress_var.set(100)
        
        if error_count == 0:
            messagebox.showinfo("完成", f"处理完成！成功处理 {success_count} 个文件。")
            self.status_var.set(f"处理完成，成功处理 {success_count} 个文件")
        else:
            error_msg = f"处理完成！成功: {success_count}, 失败: {error_count}\n\n"
            if len(errors) <= 10:
                error_msg += "错误详情:\n" + "\n".join(errors)
            else:
                error_msg += "错误详情:\n" + "\n".join(errors[:10]) + f"\n... 还有 {len(errors)-10} 个错误"
            
            messagebox.showwarning("完成", error_msg)
            self.status_var.set(f"处理完成，成功: {success_count}, 失败: {error_count}")
        
        self.reset_buttons()
        # 清空预览，让用户重新预览
        self.clear_preview()
    
    def reset_buttons(self):
        """重置按钮状态"""
        self.rename_btn.config(state='disabled')
        self.preview_btn.config(state='normal' if self.selected_folder else 'disabled')
    
    def exit_app(self):
        """退出应用程序"""
        # 检查是否有正在进行的重命名操作
        if hasattr(self, 'preview_data') and self.preview_data and self.rename_btn['state'] == 'disabled':
            result = messagebox.askyesno("确认退出", 
                                       "检测到可能有重命名操作正在进行中。\n确定要退出程序吗？")
            if not result:
                return
        
        # 确认退出
        result = messagebox.askyesno("确认退出", "确定要退出图片重命名工具吗？")
        if result:
            self.root.quit()
            self.root.destroy()


def main():
    """主函数"""
    root = tk.Tk()
    
    # macOS特定设置 - 添加异常处理
    try:
        if root.tk.call('tk', 'windowingsystem') == 'aqua':
            # 设置macOS原生外观
            root.tk.call('tk::unsupported::MacWindowStyle', 'style', root._w, 'document')
    except Exception:
        # 如果macOS特定设置失败，继续使用默认设置
        pass
    
    app = ImageRenamerApp(root)
    
    # 设置窗口居中
    try:
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f'{width}x{height}+{x}+{y}')
    except Exception:
        # 如果窗口居中失败，使用默认位置
        pass
    
    root.mainloop()


if __name__ == "__main__":
    main()