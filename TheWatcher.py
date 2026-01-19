import sys
import psutil
import threading
import time
import os
import getpass
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTableWidget, 
                             QTableWidgetItem, QVBoxLayout, QWidget, 
                             QSystemTrayIcon, QMenu, QStyle, QPushButton, 
                             QHBoxLayout, QLineEdit, QLabel, QComboBox)
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt, pyqtSignal, QObject

# Configuration for ignored elements
EXCLUDED_PATHS = ["AppData\\Local", "AppData\\Roaming", "Windows\\Prefetch", "NTUSER.DAT"]
EXCLUDED_PROCESSES = ["svchost.exe", "conhost.exe", "lsass.exe", "SearchHost.exe", "RuntimeBroker.exe"]

class MonitorSignals(QObject):
    """Signals for communication between threads and the GUI."""
    entry_received = pyqtSignal(list)

class FileChangeHandler(FileSystemEventHandler):
    """Handles file system events and filters ignored paths."""
    def __init__(self, signals):
        super().__init__()
        self.signals = signals

    def on_created(self, event):
        if not event.is_directory and not any(p in event.src_path for p in EXCLUDED_PATHS):
            self._emit_log("FILE CREATED", os.path.basename(event.src_path))

    def on_moved(self, event):
        if not any(p in event.dest_path for p in EXCLUDED_PATHS):
            change_detail = f"{os.path.basename(event.src_path)} -> {os.path.basename(event.dest_path)}"
            self._emit_log("FILE MOVED", change_detail)

    def _emit_log(self, action, details):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.signals.entry_received.emit([timestamp, getpass.getuser(), action, "-", details])

class SystemSentinel(QMainWindow):
    """Main application window for system monitoring."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("System Sentinel")
        self.resize(1100, 600)
        
        self.is_running = True
        self.active_pids = {p.pid for p in psutil.process_iter()}
        self.signals = MonitorSignals()
        self.signals.entry_received.connect(self.append_log_row)

        self.setup_ui()
        self.setup_tray_icon()
        self.start_background_tasks()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        toolbar_layout = QHBoxLayout()
        
        # User Filter
        toolbar_layout.addWidget(QLabel("User:"))
        self.user_filter = QComboBox()
        self.populate_user_list()
        toolbar_layout.addWidget(self.user_filter)
        
        # Search Filter
        toolbar_layout.addWidget(QLabel("Search:"))
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Filter events...")
        self.search_bar.textChanged.connect(self.apply_current_filters)
        toolbar_layout.addWidget(self.search_bar)
        
        # Clear Button
        self.clear_button = QPushButton("Clear History")
        self.clear_button.clicked.connect(self.clear_table)
        toolbar_layout.addWidget(self.clear_button)
        
        main_layout.addLayout(toolbar_layout)

        # Log Table
        self.log_table = QTableWidget()
        self.log_table.setColumnCount(5)
        self.log_table.setHorizontalHeaderLabels(["Time", "User", "Action", "PID", "Object"])
        self.log_table.horizontalHeader().setStretchLastSection(True)
        self.log_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.log_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        main_layout.addWidget(self.log_table)
        
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def setup_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
        
        tray_menu = QMenu()
        show_action = QAction("Show Window", self)
        exit_action = QAction("Exit Application", self)
        
        show_action.triggered.connect(self.show)
        exit_action.triggered.connect(self.shutdown_app)
        
        tray_menu.addAction(show_action)
        tray_menu.addSeparator()
        tray_menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def populate_user_list(self):
        found_users = set()
        for proc in psutil.process_iter(['username']):
            if proc.info['username']:
                clean_name = proc.info['username'].split('\\')[-1]
                found_users.add(clean_name)
        
        self.user_filter.addItem("ALL USERS")
        self.user_filter.addItems(sorted(list(found_users)))
        self.user_filter.setCurrentText(getpass.getuser())
        self.user_filter.currentTextChanged.connect(self.apply_current_filters)

    def apply_current_filters(self):
        query = self.search_bar.text().lower()
        target_user = self.user_filter.currentText().lower()
        
        for row in range(self.log_table.rowCount()):
            row_user = self.log_table.item(row, 1).text().lower()
            row_text = " ".join([self.log_table.item(row, col).text().lower() for col in range(5)])
            
            user_match = (target_user == "all users" or target_user == row_user)
            text_match = (query in row_text)
            
            self.log_table.setRowHidden(row, not (user_match and text_match))

    def monitor_processes(self):
        while self.is_running:
            for proc in psutil.process_iter(['pid', 'name', 'username']):
                try:
                    pid = proc.info['pid']
                    name = proc.info['name']
                    
                    if pid not in self.active_pids and name not in EXCLUDED_PROCESSES:
                        self.active_pids.add(pid)
                        user = str(proc.info['username'] or "").split('\\')[-1]
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        self.signals.entry_received.emit([timestamp, user, "PROCESS STARTED", str(pid), name])
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            time.sleep(1)

    def monitor_files(self):
        observer = Observer()
        observer.schedule(FileChangeHandler(self.signals), os.path.expanduser("~"), recursive=True)
        observer.start()
        while self.is_running: 
            time.sleep(1)
        observer.stop()

    def start_background_tasks(self):
        threading.Thread(target=self.monitor_processes, daemon=True).start()
        threading.Thread(target=self.monitor_files, daemon=True).start()

    def append_log_row(self, data_list):
        row_count = self.log_table.rowCount()
        self.log_table.insertRow(row_count)
        for index, value in enumerate(data_list):
            self.log_table.setItem(row_count, index, QTableWidgetItem(value))
        
        self.apply_current_filters()
        self.log_table.scrollToBottom()

    def clear_table(self):
        self.log_table.setRowCount(0)

    def closeEvent(self, event):
        if self.tray_icon.isVisible():
            self.hide()
            event.ignore()

    def shutdown_app(self):
        self.is_running = False
        QApplication.instance().quit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    window = SystemSentinel()
    window.show()
    
    sys.exit(app.exec())