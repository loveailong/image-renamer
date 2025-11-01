#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片批量重命名工具
适用于macOS系统
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
        
        # 定义重命名规则 - 按照指定顺序
        self.rename_rules = [
            "_1_左前45度.jpg",
            "_2_正前方.jpg", 
            "_3_右前45度.jpg",
            "_4_左侧面.jpg",
            "_5_左后45度.jpg",
            "_6_正后方.jpg",
            "_7_右后45度.jpg",
            "_9_右后大灯.jpg",
            "_11_钥匙.jpg",
            "_12_中控台.jpg",
            "_13_方向盘.jpg",
            "_14_组合仪表.jpg",
            "_15_里程数特写.jpg",
            "_16_音响及空调面板.jpg",
            "_18_变速杆.jpg",
            "_19_驾驶员座椅.jpg",
            "_20_驾驶位.jpg",
            "_21_后排.jpg",
            "_22_车内顶棚.jpg",
            "_23_后备箱.jpg",
            "_24_发动机舱.jpg",
            "_30_左侧底大边.jpg",
            "_29_右侧底大边.jpg",
            "_35_左前轮胎轮毂.jpg",
            "_36_左前大灯.jpg",
            "_41_右侧前座椅.jpg",
            "_44_右侧后座椅.jpg",
            "_57_车顶.jpg",
            "_58_右侧面.jpg"
        ]
    
    def setup_ui(self):
        """设置用户界面"""
        self.root.title("图片批量重命名工具")
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
        
        # 压缩选项区域
        compress_frame = ttk.LabelFrame(main_frame, text="图片处理选项", padding="15")
        compress_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        
        self.compress_var = tk.BooleanVar()
        self.compress_var.set(True)  # 默认启用压缩
        self.compress_check = ttk.Checkbutton(compress_frame, text="压缩图片到 1800×1800 像素", 
                                            variable=self.compress_var)
        self.compress_check.grid(row=0, column=0, sticky=tk.W, padx=(0, 20))
        
        # 质量选项
        ttk.Label(compress_frame, text="压缩质量:").grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        self.quality_var = tk.IntVar()
        self.quality_var.set(85)  # 默认质量85%
        self.quality_scale = ttk.Scale(compress_frame, from_=60, to=95, 
                                     variable=self.quality_var, orient=tk.HORIZONTAL, length=150)
        self.quality_scale.grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        
        self.quality_label = ttk.Label(compress_frame, text="85%")
        self.quality_label.grid(row=0, column=3, sticky=tk.W)
        
        # 绑定质量滑块事件
        self.quality_scale.configure(command=self.update_quality_label)
        
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
        self.status_var.set("请选择包含子文件夹的目标文件夹")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var)
        self.status_label.grid(row=6, column=0, columnspan=3, pady=(10, 0))
    
    def browse_folder(self):
        """浏览文件夹"""
        try:
            folder = filedialog.askdirectory(title="选择包含子文件夹的目标文件夹")
            if folder:
                # 检查文件夹权限
                if not os.access(folder, os.R_OK):
                    messagebox.showerror("错误", f"没有读取权限: {folder}")
                    return
                
                self.selected_folder = folder
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
    
    def compress_image(self, input_path, output_path, target_size=(1800, 1800), quality=85):
        """压缩图片到指定尺寸"""
        try:
            with Image.open(input_path) as img:
                # 处理图片方向（EXIF数据）
                try:
                    from PIL.ExifTags import ORIENTATION
                    exif = img._getexif()
                    if exif is not None:
                        orientation = exif.get(0x0112)  # ORIENTATION tag
                        if orientation == 3:
                            img = img.rotate(180, expand=True)
                        elif orientation == 6:
                            img = img.rotate(270, expand=True)
                        elif orientation == 8:
                            img = img.rotate(90, expand=True)
                except Exception:
                    # 如果EXIF处理失败，继续处理
                    pass
                
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
        """从文件夹名称中提取数字"""
        # 匹配模式: 2025_11_1_北京_1234567_英菲尼迪G37
        pattern = r'^\d{4}_\d{1,2}_\d{1,2}_[^_]+_(\d+)_'
        match = re.match(pattern, folder_name)
        if match:
            return match.group(1)
        return None
    
    def get_jpg_files_in_folder(self, folder_path):
        """获取文件夹中的所有jpg文件"""
        jpg_files = []
        try:
            for file in os.listdir(folder_path):
                # 支持更多图片格式，忽略隐藏文件
                if (not file.startswith('.') and 
                    file.lower().endswith(('.jpg', '.jpeg'))):
                    jpg_files.append(file)
        except PermissionError:
            print(f"权限错误：无法访问文件夹 {folder_path}")
        except Exception as e:
            print(f"读取文件夹错误 {folder_path}: {e}")
        return sorted(jpg_files)  # 按文件名排序  
  
    def preview_rename(self):
        """预览重命名结果"""
        if not self.selected_folder:
            messagebox.showerror("错误", "请先选择文件夹")
            return
        
        # 清空之前的预览
        self.clear_preview()
        
        try:
            subfolders = [f for f in os.listdir(self.selected_folder) 
                         if os.path.isdir(os.path.join(self.selected_folder, f))]
            
            if not subfolders:
                messagebox.showwarning("警告", "选择的文件夹中没有子文件夹")
                return
            
            total_files = 0
            preview_data = []
            
            for subfolder in subfolders:
                subfolder_path = os.path.join(self.selected_folder, subfolder)
                
                # 提取数字
                number = self.extract_number_from_folder_name(subfolder)
                if not number:
                    self.status_var.set(f"警告: 无法从文件夹名 '{subfolder}' 中提取数字")
                    continue
                
                # 获取jpg文件
                jpg_files = self.get_jpg_files_in_folder(subfolder_path)
                
                if len(jpg_files) != 29:
                    self.status_var.set(f"警告: 文件夹 '{subfolder}' 中有 {len(jpg_files)} 张图片，不是29张")
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
            
            # 显示预览数据
            for data in preview_data:
                self.tree.insert('', 'end', values=(
                    f"{data['folder']}/{data['original']}", 
                    f"{data['folder']}/{data['new']}"
                ))
            
            self.preview_data = preview_data
            self.rename_btn.config(state='normal' if preview_data else 'disabled')
            self.status_var.set(f"预览完成，共 {total_files} 个文件待重命名")
            
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
        """开始重命名"""
        if not hasattr(self, 'preview_data') or not self.preview_data:
            messagebox.showerror("错误", "请先预览重命名结果")
            return
        
        # 确认对话框
        compress_text = ""
        if self.compress_var.get():
            quality = int(self.quality_var.get())
            compress_text = f"\n同时将图片压缩到1800×1800像素（质量{quality}%）"
        
        result = messagebox.askyesno("确认", 
                                   f"确定要重命名 {len(self.preview_data)} 个文件吗？{compress_text}\n此操作不可撤销！")
        if not result:
            return
        
        # 在新线程中执行重命名
        self.rename_btn.config(state='disabled')
        self.preview_btn.config(state='disabled')
        
        thread = threading.Thread(target=self.perform_rename)
        thread.daemon = True
        thread.start()
    
    def perform_rename(self):
        """执行重命名操作"""
        try:
            total = len(self.preview_data)
            success_count = 0
            error_count = 0
            errors = []
            
            for i, data in enumerate(self.preview_data):
                try:
                    # 检查原文件是否存在
                    if not os.path.exists(data['original_path']):
                        errors.append(f"文件不存在: {data['original_path']}")
                        error_count += 1
                        continue
                    
                    # 检查新文件名是否已存在
                    if os.path.exists(data['new_path']):
                        errors.append(f"目标文件已存在: {data['new_path']}")
                        error_count += 1
                        continue
                    
                    # 根据用户选择决定是否压缩
                    if self.compress_var.get():
                        # 压缩并重命名
                        quality = int(self.quality_var.get())
                        if self.compress_image(data['original_path'], data['new_path'], 
                                             target_size=(1800, 1800), quality=quality):
                            # 压缩成功后删除原文件
                            os.remove(data['original_path'])
                            success_count += 1
                        else:
                            errors.append(f"压缩失败: {data['original']} -> {data['new']}")
                            error_count += 1
                    else:
                        # 只重命名，不压缩
                        os.rename(data['original_path'], data['new_path'])
                        success_count += 1
                    
                except Exception as e:
                    errors.append(f"重命名失败 {data['original']} -> {data['new']}: {str(e)}")
                    error_count += 1
                
                # 更新进度条
                progress = (i + 1) / total * 100
                self.root.after(0, lambda p=progress: self.progress_var.set(p))
                
                # 更新状态显示
                if self.compress_var.get():
                    status_text = f"正在压缩和重命名... {i+1}/{total}"
                else:
                    status_text = f"正在重命名... {i+1}/{total}"
                self.root.after(0, lambda text=status_text: self.status_var.set(text))
            
            # 完成后的处理
            self.root.after(0, self.rename_completed, success_count, error_count, errors)
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("错误", f"重命名过程中发生错误: {str(e)}"))
            self.root.after(0, self.reset_buttons)
    
    def rename_completed(self, success_count, error_count, errors):
        """重命名完成后的处理"""
        self.progress_var.set(100)
        
        if error_count == 0:
            messagebox.showinfo("完成", f"重命名完成！成功处理 {success_count} 个文件。")
            self.status_var.set(f"重命名完成，成功处理 {success_count} 个文件")
        else:
            error_msg = f"重命名完成！成功: {success_count}, 失败: {error_count}\n\n"
            if len(errors) <= 10:
                error_msg += "错误详情:\n" + "\n".join(errors)
            else:
                error_msg += "错误详情:\n" + "\n".join(errors[:10]) + f"\n... 还有 {len(errors)-10} 个错误"
            
            messagebox.showwarning("完成", error_msg)
            self.status_var.set(f"重命名完成，成功: {success_count}, 失败: {error_count}")
        
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