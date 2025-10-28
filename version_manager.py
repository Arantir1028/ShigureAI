#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import webbrowser
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton, QMessageBox, QApplication
from PyQt5.QtCore import Qt

from version import __version__

class VersionManager:
    def __init__(self, parent):
        self.parent = parent
        self.update_status_label = None

    def show_about(self):
        QMessageBox.about(self.parent, "关于",
                         f"<h2>ShigureAI</h2>"
                         f"<p><strong>版本:</strong> {__version__}</p>"
                         f"<p>这是一个用于计算《蔚蓝档案》游戏中学生好感度的工具。</p>"
                         f"<p>支持特殊喜好礼物配置、批量导入和计算预计等级。</p>"
                         f"<p><strong>作者:</strong> 学识 @ <a href='https://space.bilibili.com/127207268?spm_id_from=333.1007.0.0'>Arantir_</a></p>"
                         f"<p><strong>项目地址:</strong> <a href='https://github.com/Arantir1028/ShigureAI'>https://github.com/Arantir1028/ShigureAI</a></p>"
                         f"<p><strong>许可证:</strong> GPL-3.0</p>")

    def show_version(self):
        """显示版本信息"""
        dialog = QDialog(self.parent)
        dialog.setWindowTitle("版本信息")
        dialog.setModal(True)
        dialog.resize(500, 400)

        layout = QVBoxLayout(dialog)

        title_label = QLabel(f"<h2>ShigureAI {__version__}</h2>")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        version_info = QTextEdit()
        version_info.setMaximumHeight(200)
        version_info.setHtml(
            f"<h3>当前版本: {__version__}</h3>"
            f"<p><strong>功能特性:</strong></p>"
            f"<ul>"
            f"<li>支持学生特殊喜好礼物配置</li>"
            f"<li>支持批量导入和计算好感度升级</li>"
            f"<li>支持保存/加载配置</li>"
            f"</ul>"
        )
        version_info.setReadOnly(True)
        layout.addWidget(version_info)

        update_layout = QHBoxLayout()

        self.update_status_label = QLabel("准备检查更新...")
        self.update_status_label.setStyleSheet("color: gray;")
        update_layout.addWidget(self.update_status_label)

        update_layout.addStretch()

        check_button = QPushButton("检查更新")
        check_button.clicked.connect(lambda: self.check_for_updates(dialog))
        update_layout.addWidget(check_button)

        layout.addLayout(update_layout)

        button_layout = QHBoxLayout()

        close_button = QPushButton("关闭")
        close_button.clicked.connect(dialog.accept)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)

        dialog.exec_()

    def get_download_urls(self, version):
        """获取多源下载链接"""
        base_filename = f"ShigureAI_{version}.exe"
        return [
            f"https://github.com/Arantir1028/ShigureAI/releases/download/{version}/{base_filename}",
            f"https://ghfast.top/https://github.com/Arantir1028/ShigureAI/releases/download/{version}/{base_filename}",
            f"https://mirror.ghproxy.com/https://github.com/Arantir1028/ShigureAI/releases/download/{version}/{base_filename}",
        ]

    def download_with_fallback(self, urls, dest_path):
        """多源下载机制"""
        for i, url in enumerate(urls):
            try:
                self.update_status_label.setText(f"尝试下载源 {i+1}/{len(urls)}...")
                QApplication.processEvents()
                
                response = requests.get(url, timeout=15, stream=True)
                if response.status_code == 200:
                    total_size = int(response.headers.get('content-length', 0))
                    downloaded = 0
                    
                    with open(dest_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                downloaded += len(chunk)
                                if total_size > 0:
                                    progress = (downloaded / total_size) * 100
                                    self.update_status_label.setText(f"下载中... {progress:.1f}%")
                                    QApplication.processEvents()
                    
                    self.update_status_label.setText("下载完成！")
                    self.update_status_label.setStyleSheet("color: green;")
                    return True
                    
            except Exception as e:
                print(f"下载源 {i+1} 失败: {e}")
                continue
        
        self.update_status_label.setText("所有下载源均不可用")
        self.update_status_label.setStyleSheet("color: red;")
        return False

    def check_for_updates(self, parent_dialog):
        try:
            self.update_status_label.setText("正在检查更新...")
            self.update_status_label.setStyleSheet("color: blue;")
            QApplication.processEvents()

            api_urls = [
                "https://api.github.com/repos/Arantir1028/ShigureAI/releases/latest",
                "https://ghfast.top/https://api.github.com/repos/Arantir1028/ShigureAI/releases/latest",
                "https://mirror.ghproxy.com/https://api.github.com/repos/Arantir1028/ShigureAI/releases/latest"
            ]
            
            release_data = None
            for api_url in api_urls:
                try:
                    response = requests.get(api_url, timeout=10)
                    if response.status_code == 200:
                        release_data = response.json()
                        break
                except:
                    continue
            
            if not release_data:
                self.update_status_label.setText("无法连接到更新服务器")
                self.update_status_label.setStyleSheet("color: red;")
                return

            latest_version = release_data['tag_name']
            current_version = __version__.lstrip('v')
            latest_version_num = latest_version.lstrip('v')

            if self.compare_versions(latest_version_num, current_version) > 0:
                self.update_status_label.setText(f"发现新版本: {latest_version}")
                self.update_status_label.setStyleSheet("color: green;")

                reply = QMessageBox.question(
                    parent_dialog,
                    "发现新版本",
                    f"当前版本: {__version__}\n"
                    f"最新版本: {latest_version}\n\n"
                    f"是否直接下载更新?",
                    QMessageBox.Yes | QMessageBox.No
                )

                if reply == QMessageBox.Yes:
                    download_urls = self.get_download_urls(latest_version)
                    dest_path = f"ShigureAI_{latest_version}.exe"
                    
                    if self.download_with_fallback(download_urls, dest_path):
                        QMessageBox.information(
                            parent_dialog,
                            "下载完成",
                            f"新版本已下载到: {dest_path}\n请关闭当前程序后运行新版本。"
                        )
                    else:
                        QMessageBox.warning(
                            parent_dialog,
                            "下载失败",
                            "所有下载源均不可用，请手动前往GitHub下载页面。"
                        )
                        webbrowser.open("https://github.com/Arantir1028/ShigureAI/releases/latest")
            else:
                self.update_status_label.setText(f"当前已是最新版本: {__version__}")
                self.update_status_label.setStyleSheet("color: green;")

                QMessageBox.information(
                    parent_dialog,
                    "版本检查",
                    f"当前版本 {__version__} 已是最新版本！"
                )

        except Exception as e:
            self.update_status_label.setText("检查更新失败")
            self.update_status_label.setStyleSheet("color: red;")
            
            QMessageBox.warning(
                parent_dialog,
                "检查更新",
                f"检查更新时发生错误: {str(e)}"
            )

        except ImportError:
            self.update_status_label.setText("缺少requests库")
            self.update_status_label.setStyleSheet("color: red;")

            QMessageBox.warning(
                parent_dialog,
                "依赖缺失",
                "需要安装requests库来检查更新。\n"
                "请运行: pip install requests"
            )

        except Exception as e:
            self.update_status_label.setText("检查失败")
            self.update_status_label.setStyleSheet("color: red;")

            QMessageBox.warning(
                parent_dialog,
                "检查更新",
                f"检查更新时发生错误:\n{str(e)}"
            )

    def compare_versions(self, version1, version2):
        """比较版本号 (返回1: v1>v2, 0: v1=v2, -1: v1<v2)"""
        def version_to_tuple(v):
            return tuple(map(int, v.split('.')))

        v1_tuple = version_to_tuple(version1)
        v2_tuple = version_to_tuple(version2)

        if v1_tuple > v2_tuple:
            return 1
        elif v1_tuple < v2_tuple:
            return -1
        else:
            return 0
