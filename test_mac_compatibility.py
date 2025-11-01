#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
macOS兼容性测试脚本
"""

import sys
import os

def test_basic_imports():
    """测试基本导入"""
    print("=== 基本导入测试 ===")
    
    try:
        import tkinter as tk
        print("✓ tkinter 导入成功")
    except ImportError as e:
        print(f"✗ tkinter 导入失败: {e}")
        return False
    
    try:
        from tkinter import ttk, filedialog, messagebox
        print("✓ tkinter 子模块导入成功")
    except ImportError as e:
        print(f"✗ tkinter 子模块导入失败: {e}")
        return False
    
    try:
        from PIL import Image, ImageTk
        print("✓ PIL/Pillow 导入成功")
    except ImportError as e:
        print(f"✗ PIL/Pillow 导入失败: {e}")
        return False
    
    return True

def test_tkinter_basic():
    """测试Tkinter基本功能"""
    print("\n=== Tkinter基本功能测试 ===")
    
    try:
        import tkinter as tk
        root = tk.Tk()
        root.title("测试窗口")
        
        # 测试macOS检测
        try:
            windowing_system = root.tk.call('tk', 'windowingsystem')
            print(f"✓ 窗口系统: {windowing_system}")
        except Exception as e:
            print(f"✗ 窗口系统检测失败: {e}")
        
        # 测试基本组件
        label = tk.Label(root, text="测试标签")
        label.pack()
        
        print("✓ 基本Tkinter组件创建成功")
        
        # 不显示窗口，直接销毁
        root.destroy()
        return True
        
    except Exception as e:
        print(f"✗ Tkinter基本功能测试失败: {e}")
        return False

def test_pil_basic():
    """测试PIL基本功能"""
    print("\n=== PIL基本功能测试 ===")
    
    try:
        from PIL import Image
        
        # 创建一个测试图片
        img = Image.new('RGB', (100, 100), color='red')
        print("✓ PIL图片创建成功")
        
        # 测试图片操作
        resized = img.resize((50, 50))
        print("✓ PIL图片缩放成功")
        
        return True
        
    except Exception as e:
        print(f"✗ PIL基本功能测试失败: {e}")
        return False

def test_file_operations():
    """测试文件操作"""
    print("\n=== 文件操作测试 ===")
    
    try:
        # 测试当前目录访问
        current_dir = os.getcwd()
        print(f"✓ 当前目录: {current_dir}")
        
        # 测试目录列表
        files = os.listdir(current_dir)
        print(f"✓ 目录列表成功，共 {len(files)} 个项目")
        
        # 测试权限
        if os.access(current_dir, os.R_OK):
            print("✓ 目录读取权限正常")
        else:
            print("✗ 目录读取权限不足")
            
        if os.access(current_dir, os.W_OK):
            print("✓ 目录写入权限正常")
        else:
            print("✗ 目录写入权限不足")
        
        return True
        
    except Exception as e:
        print(f"✗ 文件操作测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print(f"Python版本: {sys.version}")
    print(f"运行平台: {sys.platform}")
    print(f"操作系统: {os.name}")
    
    tests = [
        test_basic_imports,
        test_tkinter_basic,
        test_pil_basic,
        test_file_operations
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"测试异常: {e}")
            results.append(False)
    
    print(f"\n=== 测试总结 ===")
    print(f"通过: {sum(results)}/{len(results)}")
    
    if all(results):
        print("✓ 所有测试通过，环境配置正常")
    else:
        print("✗ 部分测试失败，请检查环境配置")

if __name__ == "__main__":
    main()