#!/usr/bin/env python3
"""
Vercel构建脚本
"""
import os
import subprocess

def build():
    """构建函数"""
    print("Building Tech News Aggregator...")
    
    # 安装依赖
    subprocess.run([
        "pip", "install", "-r", "requirements.txt", 
        "--break-system-packages"
    ], check=True)
    
    print("Build completed!")

if __name__ == "__main__":
    build()
