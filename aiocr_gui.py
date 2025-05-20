import sys
import os
import yaml
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QLineEdit, QTextEdit, QFileDialog, QComboBox, QSpinBox, QVBoxLayout, QHBoxLayout, QFormLayout, QMessageBox, QDialog
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('详细设置')
        self.resize(350, 340)
        self.setWindowOpacity(1.0)  # 设置窗口整体不透明
        self.setStyleSheet('background: white;')  # 强制背景为白色
        self.setModal(True)  # 设置为模态对话框，防止主界面穿透
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()
        self.openai_baseurl_edit = QLineEdit('https://api.openai.com/v1')
        layout.addRow('OpenAI BaseURL:', self.openai_baseurl_edit)
        self.openai_key_edit = QLineEdit()
        self.openai_key_edit.setEchoMode(QLineEdit.Password)
        layout.addRow('OpenAI API Key:', self.openai_key_edit)
        self.openai_model_edit = QLineEdit('gpt-4-vision-preview')
        layout.addRow('OpenAI模型:', self.openai_model_edit)
        self.genai_key_edit = QLineEdit()
        self.genai_key_edit.setEchoMode(QLineEdit.Password)
        layout.addRow('GenAI API Key:', self.genai_key_edit)
        self.genai_model_edit = QLineEdit('gemini-1.5-flash-latest')
        layout.addRow('GenAI模型:', self.genai_model_edit)
        self.bind_spin = QSpinBox()
        self.bind_spin.setRange(1, 100)
        self.bind_spin.setValue(10)
        layout.addRow('每批处理图片数:', self.bind_spin)
        self.translate_edit = QLineEdit('简体中文')
        layout.addRow('翻译目标语言:', self.translate_edit)
        self.proxy_edit = QLineEdit()
        layout.addRow('代理服务器:', self.proxy_edit)
        self.max_workers_spin = QSpinBox()
        self.max_workers_spin.setRange(1, 32)
        self.max_workers_spin.setValue(5)
        layout.addRow('最大并发线程数:', self.max_workers_spin)
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(10, 600)
        self.timeout_spin.setValue(30)
        layout.addRow('超时时间(秒):', self.timeout_spin)
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton('保存设置')
        self.save_btn.clicked.connect(self.save_settings)
        self.back_btn = QPushButton('返回')
        self.back_btn.clicked.connect(self.handle_back)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.back_btn)
        layout.addRow(btn_layout)
        self.setLayout(layout)

    def save_settings(self):
        self.accept() # 使用 accept() 来表示用户确认了更改

    def handle_back(self):
        self.reject() # 使用 reject() 来表示用户取消了更改

    def get_settings(self):
        return {
            'openai_baseurl': self.openai_baseurl_edit.text().strip(),
            'openai_key': self.openai_key_edit.text().strip(),
            'openai_model': self.openai_model_edit.text().strip(),
            'genai_key': self.genai_key_edit.text().strip(),
            'genai_model': self.genai_model_edit.text().strip(),
            'bind': self.bind_spin.value(),
            'translateTo': self.translate_edit.text().strip(),
            'proxy': self.proxy_edit.text().strip(),
            'max_workers': self.max_workers_spin.value(),
            'timeout': self.timeout_spin.value()
        }

class ProcessThread(QThread):
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()
    error_signal = pyqtSignal(str)

    def __init__(self, input_dir, output_dir, client_type, openai_baseurl, openai_key, openai_model,
                 genai_key, genai_model, bind, translate_to, max_workers, timeout, parent=None):
        super().__init__(parent)
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.client_type = client_type
        self.openai_baseurl = openai_baseurl
        self.openai_key = openai_key
        self.openai_model = openai_model
        self.genai_key = genai_key
        self.genai_model = genai_model
        self.bind = bind
        self.translate_to = translate_to
        self.max_workers = max_workers
        self.timeout = timeout

    def run(self):
        try:
            import main
            main.process_directory(
                self.input_dir,
                self.output_dir,
                self.client_type,
                self.openai_baseurl,
                self.openai_key,
                self.openai_model,
                self.genai_key,
                self.genai_model,
                self.bind,
                self.translate_to,
                self.max_workers,
                self.timeout,
                logger_callback=self.log_signal.emit
            )
            self.finished_signal.emit()
        except ImportError:
            self.error_signal.emit('错误: main.py 未找到或无法导入。请确保文件存在。')
        except Exception as e:
            self.error_signal.emit(f'处理过程中发生错误: {str(e)}')

class AiOCRGui(QWidget):
    def __init__(self):
        super().__init__()
        self.settings = {
            'input': '',
            'output': '',
            'openai_baseurl': 'https://api.openai.com/v1',
            'openai_key': '',
            'openai_model': 'gpt-4-vision-preview',
            'genai_key': '',
            'genai_model': 'gemini-1.5-flash-latest',
            'bind': 10,
            'translateTo': '简体中文',
            'clientType': 'openai',
            'proxy': '',
            'max_workers': 5,
            'timeout': 30
        }
        self.load_config()
        self.init_ui()
        self.process_thread = None

    def load_config(self):
        if getattr(sys, 'frozen', False):
            # 如果应用程序是作为捆绑包运行的（例如，由PyInstaller打包）
            application_path = os.path.dirname(sys.executable)
        else:
            # 如果应用程序是作为普通的Python脚本运行的
            application_path = os.path.dirname(__file__)
        config_path = os.path.join(application_path, 'config.yaml')
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f)
                    if config_data:
                        mapping = {
                            'input': 'input',
                            'output': 'output',
                            'openai_base_url': 'openai_baseurl',
                            'openai_api_key': 'openai_key',
                            'openai_model': 'openai_model',
                            'genai_api_key': 'genai_key',
                            'genai_model': 'genai_model',
                            'bind': 'bind',
                            'translateTo': 'translateTo',
                            'clientType': 'clientType',
                            'proxy': 'proxy',
                            'max_workers': 'max_workers',
                            'timeout': 'timeout'
                        }
                        for yaml_key, settings_key in mapping.items():
                            if yaml_key in config_data:
                                self.settings[settings_key] = config_data[yaml_key]
            except Exception as e:
                print(f'加载配置文件出错: {e}')

    def save_config(self):
        if getattr(sys, 'frozen', False):
            # 如果应用程序是作为捆绑包运行的（例如，由PyInstaller打包）
            application_path = os.path.dirname(sys.executable)
        else:
            # 如果应用程序是作为普通的Python脚本运行的
            application_path = os.path.dirname(__file__)
        config_path = os.path.join(application_path, 'config.yaml')
        config_to_save = {
            'input': self.settings.get('input', ''),
            'output': self.settings.get('output', ''),
            'openai_base_url': self.settings.get('openai_baseurl', 'https://api.openai.com/v1'),
            'openai_api_key': self.settings.get('openai_key', ''),
            'openai_model': self.settings.get('openai_model', 'gpt-4-vision-preview'),
            'genai_api_key': self.settings.get('genai_key', ''),
            'genai_model': self.settings.get('genai_model', 'gemini-1.5-flash-latest'),
            'bind': self.settings.get('bind', 10),
            'translateTo': self.settings.get('translateTo', '简体中文'),
            'clientType': self.settings.get('clientType', 'openai'),
            'proxy': self.settings.get('proxy', ''),
            'max_workers': self.settings.get('max_workers', 5),
            'timeout': self.settings.get('timeout', 30)
        }
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_to_save, f, allow_unicode=True, sort_keys=False)
            self.append_log_message('设置已保存到 config.yaml')
        except Exception as e:
            self.append_log_message(f'保存配置文件出错: {e}')
            QMessageBox.warning(self, '错误', f'保存配置文件出错: {e}')

    def init_ui(self):
        self.setWindowTitle('AiOCR 批量图片文字识别工具')
        self.resize(500, 300)
        form_layout = QFormLayout()
        self.input_edit = QLineEdit()
        self.input_edit.setText(self.settings.get('input', ''))
        btn_input = QPushButton('选择文件夹')
        btn_input.clicked.connect(self.select_input_folder)
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.input_edit)
        input_layout.addWidget(btn_input)
        form_layout.addRow('图片输入目录:', input_layout)
        self.output_edit = QLineEdit()
        self.output_edit.setText(self.settings.get('output', ''))
        btn_output = QPushButton('选择文件夹')
        btn_output.clicked.connect(self.select_output_folder)
        output_layout = QHBoxLayout()
        output_layout.addWidget(self.output_edit)
        output_layout.addWidget(btn_output)
        form_layout.addRow('文本输出目录:', output_layout)
        self.client_combo = QComboBox()
        self.client_combo.addItems(['openai', 'genai'])
        self.client_combo.setCurrentText(self.settings.get('clientType', 'openai'))
        form_layout.addRow('客户端类型:', self.client_combo)
        self.translate_edit = QLineEdit('简体中文')
        self.translate_edit.setText(self.settings.get('translateTo', '简体中文'))
        form_layout.addRow('翻译目标语言:', self.translate_edit)
        self.settings_btn = QPushButton('设置')
        self.settings_btn.clicked.connect(self.open_settings)
        self.start_btn = QPushButton('开始处理')
        self.start_btn.clicked.connect(self.start_process)
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.settings_btn)
        btn_layout.addWidget(self.start_btn)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addLayout(btn_layout)
        layout.addWidget(QLabel('日志输出:'))
        layout.addWidget(self.log_text)
        self.setLayout(layout)

    def select_input_folder(self):
        folder = QFileDialog.getExistingDirectory(self, '选择图片输入目录')
        if folder:
            self.input_edit.setText(folder)
            self.settings['input'] = folder

    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, '选择文本输出目录')
        if folder:
            self.output_edit.setText(folder)
            self.settings['output'] = folder

    def open_settings(self):
        dlg = SettingsDialog(self)
        dlg.openai_baseurl_edit.setText(self.settings.get('openai_baseurl', 'https://api.openai.com/v1'))
        dlg.openai_key_edit.setText(self.settings.get('openai_key', ''))
        dlg.openai_model_edit.setText(self.settings.get('openai_model', 'gpt-4-vision-preview'))
        dlg.genai_key_edit.setText(self.settings.get('genai_key', ''))
        dlg.genai_model_edit.setText(self.settings.get('genai_model', 'gemini-1.5-flash-latest'))
        dlg.bind_spin.setValue(self.settings.get('bind', 10))
        dlg.translate_edit.setText(self.settings.get('translateTo', '简体中文'))
        dlg.proxy_edit.setText(self.settings.get('proxy', ''))
        dlg.max_workers_spin.setValue(self.settings.get('max_workers', 5))
        dlg.timeout_spin.setValue(self.settings.get('timeout', 30))
        
        if dlg.exec_() == QDialog.Accepted:
            self.settings.update(dlg.get_settings())
            self.client_combo.setCurrentText(self.settings.get('clientType', 'openai'))
            self.translate_edit.setText(self.settings.get('translateTo', '简体中文'))
            self.save_config()

    def append_log_message(self, message):
        self.log_text.append(message)

    def start_process(self):
        if self.process_thread and self.process_thread.isRunning():
            QMessageBox.information(self, "提示", "处理任务正在进行中，请稍候。")
            return

        self.settings['input'] = self.input_edit.text().strip()
        self.settings['output'] = self.output_edit.text().strip()
        self.settings['clientType'] = self.client_combo.currentText()
        self.settings['translateTo'] = self.translate_edit.text().strip()
        self.save_config()

        input_dir = self.settings.get('input')
        output_dir = self.settings.get('output')
        client_type = self.settings.get('clientType')
        translate_to = self.settings.get('translateTo')
        openai_baseurl = self.settings.get('openai_baseurl', 'https://api.openai.com/v1')
        openai_key = self.settings.get('openai_key', '')
        openai_model = self.settings.get('openai_model', 'gpt-4-vision-preview')
        genai_key = self.settings.get('genai_key', '')
        genai_model = self.settings.get('genai_model', 'gemini-1.5-flash-latest')
        bind = self.settings.get('bind', 10)
        proxy = self.settings.get('proxy', '')
        max_workers = self.settings.get('max_workers', 5)
        timeout = self.settings.get('timeout', 30)

        if not input_dir or not output_dir:
            QMessageBox.warning(self, '参数错误', '请输入输入和输出目录！')
            return
        if client_type == 'openai' and not openai_key:
            QMessageBox.warning(self, '参数错误', '请输入 OpenAI API Key！（在设置中）')
            return
        if client_type == 'genai' and not genai_key:
            QMessageBox.warning(self, '参数错误', '请输入 GenAI API Key！（在设置中）')
            return
            
        self.append_log_message(f'使用设置开始处理: Client={client_type}, TranslateTo={translate_to}, Input={input_dir[:50]}...')
        
        if proxy:
            os.environ['HTTP_PROXY'] = proxy
            os.environ['HTTPS_PROXY'] = proxy
        else:
            os.environ.pop('HTTP_PROXY', None)
            os.environ.pop('HTTPS_PROXY', None)

        self.start_btn.setEnabled(False)
        self.settings_btn.setEnabled(False)

        self.process_thread = ProcessThread(
            input_dir, output_dir, client_type, openai_baseurl, openai_key, openai_model,
            genai_key, genai_model, bind, translate_to, max_workers, timeout
        )
        self.process_thread.log_signal.connect(self.append_log_message)
        self.process_thread.finished_signal.connect(self.handle_process_finished)
        self.process_thread.error_signal.connect(self.handle_process_error)
        self.process_thread.start()

    def handle_process_finished(self):
        self.append_log_message('所有图片处理完成！')
        QMessageBox.information(self, '完成', '所有图片处理完成！')
        self.start_btn.setEnabled(True)
        self.settings_btn.setEnabled(True)

    def handle_process_error(self, error_message):
        self.append_log_message(error_message)
        QMessageBox.critical(self, '处理错误', error_message)
        self.start_btn.setEnabled(True)
        self.settings_btn.setEnabled(True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AiOCRGui()
    window.show()
    sys.exit(app.exec_())
