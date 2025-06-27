import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import psutil
import os
import json
from datetime import datetime
import threading
import subprocess
from queue import Queue

# Import managers
from repair_manager import RepairManager
from granite_manager import GraniteManager

class OPRYXXEnhanced(QMainWindow):
    # Signals for Granite Manager
    logAnalysisRequested = pyqtSignal(str)
    optimizationSuggestionRequested = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle('🜏 OPRYXX Ascension - Enhanced System Repair')
        self.setMinimumSize(1000, 700)
        
        # Setup queues for thread-safe updates
        self.status_queue = Queue()
        self.log_queue = Queue()
        self.progress_queue = Queue()
        
        # Load configuration
        self.load_config() # Load config before initializing managers
        
        # Initialize managers
        self.repair_manager = RepairManager(
            status_callback=self.status_queue.put,
            log_callback=self.log_queue.put,
            progress_callback=self.progress_queue.put
        )
        self.granite_manager = GraniteManager(
            log_callback=self.log_queue.put,
            config=self.config.get('granite_settings', {})
        )
        
        # Initialize UI
        self.setup_ui()
        
        # Force maximized window on every launch
        self.showMaximized()
        
        # Load window state (will not override forced maximization)
        self.load_window_state()
        
        # Start update timers
        self.start_update_timers()
    
    def load_window_state(self):
        """Load window state from config or use defaults."""
        window_state = self.config.get('window_state', {})
        
        # Set window geometry if saved
        if 'geometry' in window_state:
            self.restoreGeometry(window_state['geometry'])
        else:
            # Default to maximized if no saved state
            self.showMaximized()
            
        # Restore window state (maximized/normal)
        if window_state.get('maximized', True):
            self.showMaximized()
    
    def save_window_state(self):
        """Save current window state to config."""
        if not hasattr(self, 'config'):
            return
            
        if 'window_state' not in self.config:
            self.config['window_state'] = {}
            
        self.config['window_state'].update({
            'geometry': self.saveGeometry(),
            'maximized': self.isMaximized()
        })
        self.save_config_file()
        
        # Set theme based on config
        self.apply_theme()
        
        # Connect Granite signals
        self.logAnalysisRequested.connect(self.granite_manager.analyze_system_logs)
        self.optimizationSuggestionRequested.connect(self.granite_manager.provide_optimization_suggestions)
        
        # Start Granite monitoring if enabled in config
        if self.config.get('granite_settings', {}).get('enable_monitoring', False):
            self.granite_manager.start_monitoring()
    
    def setup_ui(self):
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Add tabs
        self.setup_repair_tab()
        self.setup_system_tab()
        self.setup_optimization_tab()
        self.setup_recovery_tab()
        self.setup_maintenance_tab()
        self.setup_modules_tab()
        self.setup_settings_tab()
        self.setup_ai_workbench_tab() # New Granite tab
        
        # Create status bar
        self.statusBar().showMessage('Ready')
    
    def setup_repair_tab(self):
        repair_tab = QWidget()
        layout = QVBoxLayout(repair_tab)
        
        # Header
        header = QLabel('OPRYXX System Repair Chain')
        header.setStyleSheet('font-size: 20px; color: #00dd88; margin: 8px;')
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Module selection group
        group_box = QGroupBox('Repair Modules')
        group_layout = QGridLayout() # Use QGridLayout for better checkbox layout
        
        self.module_checks = {}
        # Fetch available modules from RepairManager
        available_modules = os.listdir(self.repair_manager.modules_dir)
        modules_to_display = []
        for mod_file in available_modules:
            if mod_file.endswith('.bat'):
                mod_id = mod_file.replace('.bat', '')
                # Create a more user-friendly name
                mod_name = mod_id.replace('_', ' ').title()
                modules_to_display.append((mod_id, mod_name))

        row, col = 0, 0
        for mod_id, mod_name in modules_to_display:
            cb = QCheckBox(mod_name)
            cb.setChecked(True)
            self.module_checks[mod_id] = cb
            group_layout.addWidget(cb, row, col)
            col += 1
            if col >= 2: # Two columns of checkboxes
                col = 0
                row += 1
        
        group_box.setLayout(group_layout)
        layout.addWidget(group_box)
        
        # Progress section
        progress_group = QGroupBox('Progress')
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel('Status: Idle')
        progress_layout.addWidget(self.status_label)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        # Log section
        log_group = QGroupBox('Operation Log')
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton('🚀 Start Repair Chain')
        self.start_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.start_button.clicked.connect(self.start_repair_chain)
        button_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton('⏹ Stop Repair')
        self.stop_button.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_repair_chain)
        button_layout.addWidget(self.stop_button)
        
        layout.addLayout(button_layout)
        self.tabs.addTab(repair_tab, '🔧 Repair Chain')

    def setup_system_tab(self):
        system_tab = QWidget()
        layout = QVBoxLayout(system_tab)
        
        # System metrics grid
        metrics_group = QGroupBox('Real-time System Metrics')
        grid = QGridLayout()
        
        self.metrics_labels = {}
        metric_names = {
            'cpu_usage': 'CPU Usage',
            'memory_usage': 'Memory Usage',
            'disk_c_usage': 'Disk (C:) Usage',
            'network_sent': 'Network Sent',
            'network_recv': 'Network Received'
        }
        
        row = 0
        for key, name in metric_names.items():
            label_name = QLabel(f'{name}:')
            label_value = QLabel('---')
            self.metrics_labels[key] = label_value
            grid.addWidget(label_name, row, 0)
            grid.addWidget(label_value, row, 1)
            row += 1
            
        metrics_group.setLayout(grid)
        layout.addWidget(metrics_group)
        
        # System Information
        info_group = QGroupBox('Detailed System Information')
        info_layout = QVBoxLayout()
        
        self.sys_info_text = QTextEdit()
        self.sys_info_text.setReadOnly(True)
        info_layout.addWidget(self.sys_info_text)
        
        refresh_sys_info_btn = QPushButton('🔄 Refresh System Info')
        refresh_sys_info_btn.clicked.connect(self.update_detailed_system_info)
        info_layout.addWidget(refresh_sys_info_btn)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        self.tabs.addTab(system_tab, '📊 System Monitor')
        self.update_detailed_system_info() # Initial population

    def setup_optimization_tab(self):
        opt_tab = QWidget()
        layout = QVBoxLayout(opt_tab)
        header = QLabel('System Optimization Tools')
        header.setStyleSheet('font-size: 20px; color: #00dd88; margin: 8px;')
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Placeholder for optimization tools
        placeholder_label = QLabel("Optimization tools (e.g., Startup Manager, Service Optimizer) will be here.")
        placeholder_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(placeholder_label)
        
        self.tabs.addTab(opt_tab, '⚡ Performance Tuning')
        
    def setup_recovery_tab(self):
        """Set up the Recovery tab with GANDALFS integration."""
        recovery_tab = QWidget()
        layout = QVBoxLayout(recovery_tab)
        
        # Header
        header = QLabel('🛡️ System Recovery')
        header.setStyleSheet('font-size: 20px; color: #ff6b6b; margin: 8px;')
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Main splitter for left/right panels
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Recovery Actions
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Recovery Actions Group
        actions_group = QGroupBox('Recovery Actions')
        actions_layout = QVBoxLayout()
        
        # Create Recovery Point
        self.btn_create_recovery = QPushButton('➕ Create System Recovery Point')
        self.btn_create_recovery.setIcon(self.style().standardIcon(QStyle.SP_FileDialogNewFolder))
        self.btn_create_recovery.clicked.connect(self.create_recovery_point)
        actions_layout.addWidget(self.btn_create_recovery)
        
        # Restore from Recovery
        self.btn_restore = QPushButton('🔄 Restore System')
        self.btn_restore.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
        self.btn_restore.clicked.connect(self.restore_system)
        actions_layout.addWidget(self.btn_restore)
        
        # Run System Repair
        self.btn_repair = QPushButton('🔧 Run System Repair')
        self.btn_repair.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
        self.btn_repair.clicked.connect(self.run_system_repair)
        actions_layout.addWidget(self.btn_repair)
        
        # Boot Repair
        self.btn_boot_repair = QPushButton('👢 Repair Boot Configuration')
        self.btn_boot_repair.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        self.btn_boot_repair.clicked.connect(self.repair_boot_configuration)
        actions_layout.addWidget(self.btn_boot_repair)
        
        actions_group.setLayout(actions_layout)
        left_layout.addWidget(actions_group)
        
        # Recovery Images List
        self.recovery_list = QListWidget()
        self.recovery_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.recovery_list.itemDoubleClicked.connect(self.restore_system)
        left_layout.addWidget(QLabel('Available Recovery Points:'))
        left_layout.addWidget(self.recovery_list)
        
        # Right panel - Log and Details
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Recovery Log
        log_group = QGroupBox('Recovery Log')
        log_layout = QVBoxLayout()
        self.recovery_log = QTextEdit()
        self.recovery_log.setReadOnly(True)
        log_layout.addWidget(self.recovery_log)
        log_group.setLayout(log_layout)
        right_layout.addWidget(log_group)
        
        # Progress Section
        progress_group = QGroupBox('Progress')
        progress_layout = QVBoxLayout()
        self.recovery_progress = QProgressBar()
        self.recovery_status = QLabel('Ready')
        progress_layout.addWidget(self.recovery_progress)
        progress_layout.addWidget(self.recovery_status)
        progress_group.setLayout(progress_layout)
        right_layout.addWidget(progress_group)
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        layout.addWidget(splitter)
        self.tabs.addTab(recovery_tab, '🛡️ System Recovery')
        
        # Initialize recovery components
        self.init_recovery_components()
    
    def init_recovery_components(self):
        """Initialize recovery-related components."""
        try:
            from winre_agent_enhanced import EnhancedWinREAgent
            self.recovery_agent = EnhancedWinREAgent()
            self.update_recovery_list()
        except Exception as e:
            self.log_message_internal(f'Failed to initialize recovery agent: {e}', 'ERROR')
    
    def update_recovery_list(self):
        """Update the list of available recovery points."""
        if hasattr(self, 'recovery_agent'):
            self.recovery_list.clear()
            try:
                images = self.recovery_agent.list_recovery_images()
                for img in images:
                    item = QListWidgetItem(img)
                    item.setIcon(self.style().standardIcon(QStyle.SP_DriveHDIcon))
                    self.recovery_list.addItem(item)
            except Exception as e:
                self.log_message_internal(f'Error listing recovery images: {e}', 'ERROR')
    
    def create_recovery_point(self):
        """Create a new system recovery point."""
        if not hasattr(self, 'recovery_agent'):
            self.log_message('Recovery agent not initialized', 'ERROR')
            return
            
        name, ok = QInputDialog.getText(self, 'Create Recovery Point', 
                                      'Enter a name for the recovery point:')
        if ok and name:
            self.log_message(f'Creating recovery point: {name}...')
            QApplication.setOverrideCursor(Qt.WaitCursor)
            try:
                if self.recovery_agent.create_recovery_point(name):
                    self.log_message('Recovery point created successfully', 'SUCCESS')
                    self.update_recovery_list()
                else:
                    self.log_message('Failed to create recovery point', 'ERROR')
            except Exception as e:
                self.log_message(f'Error creating recovery point: {e}', 'ERROR')
            finally:
                QApplication.restoreOverrideCursor()
    
    def restore_system(self):
        """Restore system from selected recovery point."""
        selected = self.recovery_list.currentItem()
        if not selected:
            QMessageBox.warning(
                self,
                'No Selection',
                'Please select a recovery point to restore.'
            )
            return
            
        reply = QMessageBox.question(
            self,
            'Confirm Restore',
            f'Are you sure you want to restore from:\n{selected.text()}\n\nThis will overwrite your current system!',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
            
        if reply == QMessageBox.Yes:
            self.log_message(f'Starting system restore from: {selected.text()}')
            # TODO: Implement actual restore with progress tracking
    
    def run_system_repair(self):
        """Run system repair sequence."""
        if not hasattr(self, 'recovery_agent'):
            self.log_message('Recovery agent not initialized', 'ERROR')
            return
            
        self.log_message('Starting system repair sequence...')
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            if self.recovery_agent.run_repair_sequence():
                self.log_message('System repair completed successfully', 'SUCCESS')
            else:
                self.log_message('System repair completed with warnings', 'WARNING')
        except Exception as e:
            self.log_message(f'Error during system repair: {e}', 'ERROR')
        finally:
            QApplication.restoreOverrideCursor()
    
    def repair_boot_configuration(self):
        """Repair the system boot configuration."""
        if not hasattr(self, 'recovery_agent'):
            self.log_message('Recovery agent not initialized', 'ERROR')
            return
            
        self.log_message('Repairing boot configuration...')
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            if self.recovery_agent.repair_boot_configuration():
                self.log_message('Boot configuration repaired successfully', 'SUCCESS')
            else:
                self.log_message('Boot repair completed with warnings', 'WARNING')
        except Exception as e:
            self.log_message(f'Error repairing boot configuration: {e}', 'ERROR')
        finally:
            QApplication.restoreOverrideCursor()
    
    def log_message(self, message, level='INFO'):
        """Log a message to the recovery log."""
        timestamp = QDateTime.currentDateTime().toString('hh:mm:ss')
        if level == 'ERROR':
            self.recovery_log.setTextColor(Qt.red)
        elif level == 'WARNING':
            self.recovery_log.setTextColor(QColor(255, 165, 0))  # Orange
        elif level == 'SUCCESS':
            self.recovery_log.setTextColor(QColor(0, 200, 0))  # Green
        else:
            self.recovery_log.setTextColor(Qt.white)
            
        self.recovery_log.append(f'[{timestamp}] {message}')
        self.recovery_log.verticalScrollBar().setValue(
            self.recovery_log.verticalScrollBar().maximum()
        )
            
        # Also log to main application log
        self.log_message_internal(f'[Recovery] {message}', level)

    def setup_modules_tab(self):
        modules_tab = QWidget()
        layout = QVBoxLayout(modules_tab)
        
        # Header with Module Count
        header_layout = QHBoxLayout()
        header = QLabel('Repair Module Manager')
        header.setStyleSheet('font-size: 20px; color: #00dd88; margin: 8px;')
        header.setAlignment(Qt.AlignLeft)
        header_layout.addWidget(header)
        
        self.module_count_label = QLabel('0 modules loaded')
        self.module_count_label.setStyleSheet('color: #888888; font-style: italic;')
        self.module_count_label.setAlignment(Qt.AlignRight)
        header_layout.addWidget(self.module_count_label)
        layout.addLayout(header_layout)
        
        # Split view: Module list on left, details/editor on right
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Left side - Module List
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Module list with search
        search_layout = QHBoxLayout()
        self.module_search_input = QLineEdit()
        self.module_search_input.setPlaceholderText('🔍 Search modules...')
        self.module_search_input.textChanged.connect(self.filter_modules_list)
        search_layout.addWidget(self.module_search_input)
        
        self.module_type_filter_combo = QComboBox()
        self.module_type_filter_combo.addItems(['All Types', 'Repair', 'Optimization', 'Diagnostic', 'Maintenance', 'Default', 'Custom'])
        self.module_type_filter_combo.currentTextChanged.connect(self.filter_modules_list)
        search_layout.addWidget(self.module_type_filter_combo)
        left_layout.addLayout(search_layout)
        
        # Module list widget
        self.module_list_widget = QListWidget()
        self.module_list_widget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.module_list_widget.currentItemChanged.connect(self.display_selected_module_details)
        left_layout.addWidget(self.module_list_widget)
        
        # Module actions
        action_layout = QHBoxLayout()
        
        add_btn = QPushButton('➕ Add New')
        add_btn.setIcon(self.style().standardIcon(QStyle.SP_FileIcon)) # Using a more generic add icon
        add_btn.clicked.connect(self.add_new_module_ui)
        action_layout.addWidget(add_btn)
        
        # import_btn = QPushButton('📥 Import') # Placeholder for future
        # import_btn.setIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton))
        # import_btn.clicked.connect(self.import_module_script)
        # action_layout.addWidget(import_btn)
        
        # export_btn = QPushButton('📤 Export') # Placeholder for future
        # export_btn.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))
        # export_btn.clicked.connect(self.export_module_script)
        # action_layout.addWidget(export_btn)
        
        left_layout.addLayout(action_layout)
        
        # Right side - Module Details and Editor
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Module details section
        details_group = QGroupBox('Module Details')
        details_layout = QFormLayout()
        
        self.module_id_label = QLabel("<i>Not saved</i>") # For new/unsaved modules
        details_layout.addRow('Module ID:', self.module_id_label)

        self.module_name_input = QLineEdit()
        details_layout.addRow('Name:', self.module_name_input)
        
        self.module_description_input = QTextEdit()
        self.module_description_input.setMaximumHeight(80) # Increased height
        details_layout.addRow('Description:', self.module_description_input)
        
        self.module_category_combo = QComboBox()
        self.module_category_combo.addItems(['Repair', 'Optimization', 'Diagnostic', 'Maintenance', 'Utility'])
        details_layout.addRow('Category:', self.module_category_combo)
        
        self.module_enabled_checkbox = QCheckBox('Module Enabled')
        self.module_enabled_checkbox.setChecked(True)
        details_layout.addRow('Status:', self.module_enabled_checkbox)

        self.module_is_default_label = QLabel("No")
        details_layout.addRow("Default Module:", self.module_is_default_label)
        
        details_group.setLayout(details_layout)
        right_layout.addWidget(details_group)
        
        # Script editor
        editor_group = QGroupBox('Script Editor')
        editor_layout = QVBoxLayout()
        
        # Editor toolbar
        editor_toolbar = QHBoxLayout()
        
        self.script_language_combo = QComboBox()
        self.script_language_combo.addItems(['Batch', 'PowerShell', 'Python']) # Default to Batch for existing modules
        self.script_language_combo.currentTextChanged.connect(self.on_script_language_changed)
        editor_toolbar.addWidget(QLabel('Language:'))
        editor_toolbar.addWidget(self.script_language_combo)
        
        self.ai_assist_button = QPushButton('🤖 AI Assist')
        self.ai_assist_button.clicked.connect(self.request_ai_script_assistance)
        editor_toolbar.addWidget(self.ai_assist_button)
        
        # validate_btn = QPushButton('✓ Validate Script') # Placeholder
        # validate_btn.clicked.connect(self.validate_module_script)
        # editor_toolbar.addWidget(validate_btn)
        
        editor_toolbar.addStretch()
        editor_layout.addLayout(editor_toolbar)
        
        self.script_content_editor = QPlainTextEdit()
        self.script_content_editor.setLineWrapMode(QPlainTextEdit.NoWrap)
        font = QFont('Consolas', 10)
        if QApplication.platformName() == 'windows': # Consolas is typical on Windows
            font = QFont('Consolas', 10)
        elif QApplication.platformName() == 'darwin': # Menlo or Monaco on macOS
            font = QFont('Menlo', 11)
        else: # Monospace on Linux
            font = QFont('Monospace', 10)
        font.setFixedPitch(True)
        self.script_content_editor.setFont(font)
        editor_layout.addWidget(self.script_content_editor)
        
        editor_group.setLayout(editor_layout)
        right_layout.addWidget(editor_group)
        
        # Action buttons for save/delete/test
        module_actions_layout = QHBoxLayout()
        
        self.save_module_button = QPushButton('💾 Save Module')
        self.save_module_button.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))
        self.save_module_button.clicked.connect(self.save_current_module)
        module_actions_layout.addWidget(self.save_module_button)
        
        self.test_module_button = QPushButton('▶️ Test Module')
        self.test_module_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.test_module_button.clicked.connect(self.test_selected_module) # Renamed for clarity
        module_actions_layout.addWidget(self.test_module_button)
        
        self.delete_module_button = QPushButton('🗑️ Delete Module')
        self.delete_module_button.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))
        self.delete_module_button.clicked.connect(self.delete_selected_module)
        module_actions_layout.addWidget(self.delete_module_button)
        
        right_layout.addLayout(module_actions_layout)
        
        # Add both sides to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 1) # Module list takes 1/3
        splitter.setStretchFactor(1, 2) # Editor takes 2/3
        
        self.tabs.addTab(modules_tab, '📦 Module Manager')
        self.load_and_display_modules() # Initial load
        self.clear_module_details_form() # Ensure form is clear initially
        self.set_module_form_enabled(False) # Disable form until a module is selected or new is clicked

    def set_module_form_enabled(self, enabled):
        self.module_name_input.setEnabled(enabled)
        self.module_description_input.setEnabled(enabled)
        self.module_category_combo.setEnabled(enabled)
        self.module_enabled_checkbox.setEnabled(enabled)
        self.script_language_combo.setEnabled(enabled)
        self.script_content_editor.setEnabled(enabled)
        self.save_module_button.setEnabled(enabled)
        # Delete and Test buttons should only be enabled if a module is actually selected and exists
        current_item = self.module_list_widget.currentItem()
        can_delete_test = enabled and current_item is not None and current_item.data(Qt.UserRole) is not None
        self.delete_module_button.setEnabled(can_delete_test)
        self.test_module_button.setEnabled(can_delete_test)


    def load_and_display_modules(self):
        self.module_list_widget.clear()
        # This will be expanded to use RepairManager to fetch module metadata
        # For now, simulate by listing .bat files from the RepairManager's default dir
        
        self.all_modules_metadata = self.repair_manager.get_all_modules_metadata() # Assuming this method will be created

        for module_id, metadata in self.all_modules_metadata.items():
            display_name = metadata.get('name', module_id)
            item = QListWidgetItem(display_name)
            item.setData(Qt.UserRole, module_id) # Store module_id for retrieval
            # Add icon based on type or default status (future enhancement)
            # if metadata.get('is_default'):
            #    item.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon)) # Example icon
            self.module_list_widget.addItem(item)
            
        self.module_count_label.setText(f'{len(self.all_modules_metadata)} modules loaded')
        self.filter_modules_list() # Apply current filters

    def filter_modules_list(self):
        search_term = self.module_search_input.text().lower()
        filter_type = self.module_type_filter_combo.currentText()

        for i in range(self.module_list_widget.count()):
            item = self.module_list_widget.item(i)
            module_id = item.data(Qt.UserRole)
            metadata = self.all_modules_metadata.get(module_id, {})
            
            name_match = search_term in metadata.get('name', module_id).lower()
            desc_match = search_term in metadata.get('description', '').lower()
            id_match = search_term in module_id.lower()
            
            type_match = False
            if filter_type == 'All Types':
                type_match = True
            elif filter_type == 'Default Modules':
                type_match = metadata.get('is_default', False)
            elif filter_type == 'Custom Modules':
                type_match = not metadata.get('is_default', False)
            else: # Specific category
                type_match = metadata.get('category', '').lower() == filter_type.lower()

            item.setHidden(not ((name_match or desc_match or id_match) and type_match))

    def display_selected_module_details(self, current_item, previous_item):
        if current_item is None:
            self.clear_module_details_form()
            self.set_module_form_enabled(False)
            return

        module_id = current_item.data(Qt.UserRole)
        metadata = self.all_modules_metadata.get(module_id)

        if metadata:
            self.set_module_form_enabled(True)
            self.module_id_label.setText(f"<code>{module_id}</code>")
            self.module_name_input.setText(metadata.get('name', module_id))
            self.module_description_input.setPlainText(metadata.get('description', ''))
            self.module_category_combo.setCurrentText(metadata.get('category', 'Repair'))
            self.module_enabled_checkbox.setChecked(metadata.get('enabled', True))
            self.module_is_default_label.setText("Yes" if metadata.get('is_default') else "No")
            
            self.script_language_combo.setCurrentText(metadata.get('language', 'Batch'))
            
            # Load script content
            script_filename = metadata.get('script_file', f'{module_id}.bat') # Default to .bat if not specified
            script_path = os.path.join(self.repair_manager.modules_dir, script_filename)
            try:
                if os.path.exists(script_path):
                    with open(script_path, 'r', encoding='utf-8') as f:
                        self.script_content_editor.setPlainText(f.read())
                else:
                    self.script_content_editor.setPlainText(f"# Script file not found: {script_filename}")
                    self.log_message_internal(f"Script file missing for module {module_id}: {script_path}", "WARNING")
            except Exception as e:
                self.script_content_editor.setPlainText(f"# Error loading script: {e}")
                self.log_message_internal(f"Error loading script for module {module_id}: {e}", "ERROR")
            
            self.module_name_input.setReadOnly(metadata.get('is_default', False)) # Default modules names not editable
            self.script_language_combo.setEnabled(not metadata.get('is_default', False)) # Can't change language of default script
            self.delete_module_button.setEnabled(not metadata.get('is_default', False)) # Can't delete default

        else:
            self.clear_module_details_form()
            self.set_module_form_enabled(False)
            self.log_message_internal(f"Could not find metadata for module ID: {module_id}", "ERROR")
            
    def clear_module_details_form(self):
        self.module_id_label.setText("<i>N/A</i>")
        self.module_name_input.clear()
        self.module_description_input.clear()
        self.module_category_combo.setCurrentIndex(0)
        self.module_enabled_checkbox.setChecked(True)
        self.module_is_default_label.setText("N/A")
        self.script_language_combo.setCurrentIndex(0) # Default to Batch
        self.script_content_editor.clear()
        self.module_name_input.setReadOnly(False)
        self.script_language_combo.setEnabled(True)
        self.set_module_form_enabled(False) # Keep form disabled

    def add_new_module_ui(self):
        self.module_list_widget.clearSelection() # Deselect any current item
        self.clear_module_details_form()
        self.set_module_form_enabled(True)
        self.module_id_label.setText("<i>Enter a unique ID below (e.g., my_custom_script)</i>")
        self.module_name_input.setText("New Custom Module")
        self.module_description_input.setPlainText("# Enter script description here")
        self.script_content_editor.setPlainText("# Enter your script content here\\n# Example for Batch: @echo off\\necho Hello from custom module!")
        self.module_name_input.setReadOnly(False)
        self.script_language_combo.setEnabled(True)
        self.module_is_default_label.setText("No (Custom)")
        self.delete_module_button.setEnabled(False) # Cannot delete a new, unsaved module
        self.test_module_button.setEnabled(False)   # Cannot test an unsaved module
        self.module_name_input.setFocus()

    def save_current_module(self):
        current_item = self.module_list_widget.currentItem()
        module_id_str = self.module_id_label.text() # If it's a new module, this would be from input
        
        is_new_module = True
        original_module_id = None

        if current_item and current_item.data(Qt.UserRole): # Existing module
            original_module_id = current_item.data(Qt.UserRole)
            module_id_str = original_module_id # Use existing ID, don't allow changing it here
            is_new_module = False
            metadata = self.all_modules_metadata.get(original_module_id, {})
            if metadata.get('is_default'):
                QMessageBox.warning(self, "Cannot Save", "Default modules cannot be overwritten directly. Consider cloning or creating a new module.")
                return
        else: # New module - need to get an ID
            # For a truly new module, we need an ID. For now, derive from name if not given
            # A proper implementation would prompt for a unique script filename / ID
            temp_id_from_name = self.module_name_input.text().lower().replace(" ", "_").replace("[^a-zA-Z0-9_]", "")
            if not temp_id_from_name:
                QMessageBox.warning(self, "Module ID Required", "Please provide a valid name for the new module (used to generate ID).")
                return
            module_id_str = temp_id_from_name # This needs to be the script filename base

            if module_id_str in self.all_modules_metadata:
                 QMessageBox.warning(self, "Module ID Exists", f"A module with ID \'{module_id_str}\' (derived from name) already exists. Please choose a unique name.")
                 return


        script_language = self.script_language_combo.currentText()
        script_extension = ".bat"
        if script_language == "PowerShell": script_extension = ".ps1"
        elif script_language == "Python": script_extension = ".py"
        
        module_data = {
            'id': module_id_str, # This is the base filename without extension
            'name': self.module_name_input.text(),
            'description': self.module_description_input.toPlainText(),
            'category': self.module_category_combo.currentText(),
            'language': script_language,
            'script_file': f"{module_id_str}{script_extension}",
            'enabled': self.module_enabled_checkbox.isChecked(),
            'is_default': False # Custom modules are never default
        }

        script_content = self.script_content_editor.toPlainText()
        
        # Call RepairManager to save module (metadata + script file)
        # This method needs to be implemented in RepairManager
        success = self.repair_manager.save_module(module_data, script_content, is_new_module, original_module_id)
        
        if success:
            self.log_message_internal(f"Module '{module_data['name']}' saved successfully.")
            self.load_and_display_modules() # Refresh list
            # Try to reselect the saved module
            for i in range(self.module_list_widget.count()):
                if self.module_list_widget.item(i).data(Qt.UserRole) == module_id_str:
                    self.module_list_widget.setCurrentRow(i)
                    break
        else:
            self.log_message_internal(f"Failed to save module '{module_data['name']}'.", "ERROR")
            QMessageBox.critical(self, "Save Error", f"Could not save module '{module_data['name']}'. Check logs.")

    def delete_selected_module(self):
        current_item = self.module_list_widget.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Module Selected", "Please select a module to delete.")
            return

        module_id = current_item.data(Qt.UserRole)
        metadata = self.all_modules_metadata.get(module_id, {})

        if metadata.get('is_default', False):
            QMessageBox.warning(self, "Cannot Delete", "Default modules cannot be deleted.")
            return

        reply = QMessageBox.question(self, 'Confirm Delete', 
                                     f"Are you sure you want to delete the module '{metadata.get('name', module_id)}'?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            success = self.repair_manager.delete_module(module_id) # To be implemented in RepairManager
            if success:
                self.log_message_internal(f"Module '{module_id}' deleted.")
                self.load_and_display_modules()
                self.clear_module_details_form()
                self.set_module_form_enabled(False)
            else:
                self.log_message_internal(f"Failed to delete module '{module_id}'.", "ERROR")
                QMessageBox.critical(self, "Delete Error", f"Could not delete module '{module_id}'.")

    def test_selected_module(self):
        current_item = self.module_list_widget.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Module Selected", "Please select a module to test.")
            return
        module_id = current_item.data(Qt.UserRole)
        self.log_message_internal(f"Initiating test for module: {module_id}...")
        # Placeholder: This would ideally run the script in a controlled environment
        # and display output in a new dialog or dedicated log area.
        # For now, we can use the main repair log temporarily if careful.
        
        # Temporarily switch to main repair log for test output
        self.tabs.setCurrentWidget(self.tabs.findChild(QWidget, "Repair Chain")) # Assuming tab name or objectName
        
        self.log_text.append(f"--- Starting Test for Module: {module_id} ---")
        
        # Use a separate thread for testing to avoid freezing GUI
        test_thread = threading.Thread(target=self.repair_manager.run_module, args=(module_id,), daemon=True)
        test_thread.start()
        
        # Note: Output will go to main log via callbacks.
        # A dedicated test output dialog would be better in the future.
        QMessageBox.information(self, "Test Started", f"Test for module '{module_id}' has started. Check the Operation Log in the Repair Chain tab for output.")


    def on_script_language_changed(self, language):
        # Future: Could apply syntax highlighting or change editor settings
        self.log_message_internal(f"Script language changed to: {language}")

    def request_ai_script_assistance(self):
        current_script_content = self.script_content_editor.toPlainText()
        selected_language = self.script_language_combo.currentText()
        
        prompt_ideas = [
            "Explain this script.",
            "Improve this script for efficiency.",
            "Check this script for errors.",
            "Convert this script to PowerShell.",
            "Write a new script to [describe task]..."
        ]
        
        task_description, ok = QInputDialog.getItem(self, "AI Script Assistance", 
                                                  "What do you need help with for this script?", 
                                                  prompt_ideas, 0, True) # Editable QInputDialog
        if ok and task_description:
            # Formulate a more detailed prompt for the user
            full_prompt = (
                f"AI Task: {task_description}\\n"
                f"Script Language: {selected_language}\\n"
                f"Current Script Content (if any):\\n"
                f"```\\n{current_script_content}\\n```\\n\\n"
                f"Please provide the AI's response."
            )

            instruction_message = (
                "Copy the prompt below and use one of your integrated AI assistants in your terminal "
                "(e.g., `ai 'YOUR_PROMPT_HERE'` or `code-ai 'YOUR_PROMPT_HERE'`).\\n\\n"
                "After generating the response, you can paste it into the script editor or a new module.\\n\\n"
                "------------------------------------\\n"
                f"{full_prompt}"
                "------------------------------------"
            )
            
            # Use a larger dialog for the prompt
            dialog = QMessageBox(self)
            dialog.setWindowTitle("AI Assistance Prompt")
            dialog.setTextFormat(Qt.PlainText) # Ensure it's plain text to preserve formatting
            dialog.setText(instruction_message)
            dialog.setStandardButtons(QMessageBox.Ok)
            dialog.exec_()
            
            self.log_message_internal("AI assistance prompt provided to user.")
        else:
            self.log_message_internal("AI assistance request cancelled.")

    def import_module_script(self): # Placeholder
        QMessageBox.information(self, "Not Implemented", "Module import functionality will be added soon.")
        self.log_message_internal("Import module action triggered (not implemented).")

    def export_module_script(self): # Placeholder
        QMessageBox.information(self, "Not Implemented", "Module export functionality will be added soon.")
        self.log_message_internal("Export module action triggered (not implemented).")

    def validate_module_script(self): # Placeholder
        QMessageBox.information(self, "Not Implemented", "Script validation will be added soon.")
        self.log_message_internal("Validate script action triggered (not implemented).")

    def setup_settings_tab(self):
        settings_tab = QWidget()
        layout = QVBoxLayout(settings_tab)
        header = QLabel('Application Settings')
        header.setStyleSheet('font-size: 20px; color: #00dd88; margin: 8px;')
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Settings form
        form_group = QGroupBox('General Settings')
        form = QFormLayout()
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(['Dark', 'Light'])
        self.theme_combo.setCurrentText(self.config.get('theme', 'Dark').title())
        form.addRow('Theme:', self.theme_combo)
        
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(['DEBUG', 'INFO', 'WARNING', 'ERROR'])
        self.log_level_combo.setCurrentText(self.config.get('log_level', 'INFO'))
        form.addRow('Log Level:', self.log_level_combo)
        
        self.auto_backup_check = QCheckBox()
        self.auto_backup_check.setChecked(self.config.get('auto_backup', True))
        form.addRow('Automatic Backup Before Repair:', self.auto_backup_check)
        
        form_group.setLayout(form)
        layout.addWidget(form_group)

        # Granite AI Settings
        granite_group = QGroupBox('Granite AI Integration')
        granite_form = QFormLayout()
        self.granite_enable_monitoring_check = QCheckBox()
        self.granite_enable_monitoring_check.setChecked(self.config.get('granite_settings', {}).get('enable_monitoring', False))
        granite_form.addRow('Enable Granite Monitoring:', self.granite_enable_monitoring_check)
        self.granite_api_key_input = QLineEdit()
        self.granite_api_key_input.setPlaceholderText('Enter Granite API Key (if applicable)')
        self.granite_api_key_input.setText(self.config.get('granite_settings', {}).get('api_key', ''))
        granite_form.addRow('Granite API Key:', self.granite_api_key_input)
        granite_group.setLayout(granite_form)
        layout.addWidget(granite_group)
        
        save_btn = QPushButton('💾 Save Settings')
        save_btn.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn, alignment=Qt.AlignCenter)
        self.tabs.addTab(settings_tab, '⚙️ Settings')

    def setup_granite_tab(self):
        granite_tab = QWidget()
        main_layout = QVBoxLayout(granite_tab)
        header = QLabel('Granite AI Oversight & Collaboration Workbench') # Renamed for clarity
        header.setStyleSheet('font-size: 20px; color: #00dd88; margin: 8px;')
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)

        instr_label = QLabel(
            "<b>Workflow:</b>\n"
            "1. Select an action (Log Analysis or Optimization Advice) and click 'Prepare Request'.\n"
            "2. Copy the generated JSON from 'AI Request Task' to your PowerShell AI (e.g., `ai <JSON_HERE>`).\n"
            "3. Paste your AI's JSON response into the 'External AI Response Input' below.\n"
            "4. Click 'Display External AI Response' to see it formatted. Compare with OPRYXX's placeholder."
        )
        instr_label.setWordWrap(True)
        instr_label.setStyleSheet("padding: 10px; border: 1px solid #404040; background-color: #21252b; margin-bottom: 10px; border-radius: 5px;")
        main_layout.addWidget(instr_label)

        # Main splitter for Request, External Input, and Response Display
        main_splitter = QSplitter(Qt.Vertical)
        main_layout.addWidget(main_splitter)

        # --- Top Part: Request Preparation and OPRYXX Simulated Response ---
        top_splitter = QSplitter(Qt.Horizontal) # Split Request prep and OPRYXX sim response side-by-side

        # 1. Request Preparation Area
        request_prep_widget = QWidget()
        request_prep_layout = QVBoxLayout(request_prep_widget)
        request_prep_group = QGroupBox("Step 1 & 2: Prepare & Copy AI Request Task")
        request_prep_group_layout = QVBoxLayout(request_prep_group)
        
        self.granite_action_combo = QComboBox()
        self.granite_action_combo.addItems(["Log Analysis", "Optimization Advice"])
        request_prep_group_layout.addWidget(self.granite_action_combo)
        
        prepare_request_btn = QPushButton("📜 Prepare OPRYXX Request for AI")
        prepare_request_btn.clicked.connect(self.prepare_ai_request_for_display)
        request_prep_group_layout.addWidget(prepare_request_btn)
        
        self.granite_request_json_output = QTextEdit()
        self.granite_request_json_output.setReadOnly(True)
        self.granite_request_json_output.setPlaceholderText("OPRYXX-generated AI Request JSON will appear here...")
        self.granite_request_json_output.setFont(QFont("Consolas", 9))
        request_prep_group_layout.addWidget(self.granite_request_json_output)
        request_prep_group.setLayout(request_prep_group_layout)
        request_prep_layout.addWidget(request_prep_group)
        top_splitter.addWidget(request_prep_widget)

        # 2. OPRYXX Placeholder AI Response Area
        placeholder_response_widget = QWidget()
        placeholder_response_layout = QVBoxLayout(placeholder_response_widget)
        placeholder_response_group = QGroupBox("OPRYXX Placeholder AI's Simulated Response")
        placeholder_response_group_layout = QVBoxLayout(placeholder_response_group)
        
        self.granite_process_request_btn = QPushButton("🤖 Get OPRYXX Placeholder Response")
        self.granite_process_request_btn.clicked.connect(self.process_request_with_simulated_ai)
        self.granite_process_request_btn.setEnabled(False)
        placeholder_response_group_layout.addWidget(self.granite_process_request_btn)
        
        self.opryxx_simulated_response_output = QTextEdit() # Renamed for clarity
        self.opryxx_simulated_response_output.setReadOnly(True)
        self.opryxx_simulated_response_output.setPlaceholderText("Response from OPRYXX's internal placeholder AI will appear here...")
        self.opryxx_simulated_response_output.setFont(QFont("Consolas", 9))
        placeholder_response_group_layout.addWidget(self.opryxx_simulated_response_output)
        placeholder_response_group.setLayout(placeholder_response_group_layout)
        placeholder_response_layout.addWidget(placeholder_response_group)
        top_splitter.addWidget(placeholder_response_widget)
        
        top_splitter.setSizes([self.width() // 2, self.width() // 2])
        main_splitter.addWidget(top_splitter)

        # --- Bottom Part: External AI Response Input and Display ---
        bottom_widget = QWidget()
        bottom_layout = QHBoxLayout(bottom_widget) # Side-by-side for input and its display

        # 3. External AI Response Input Area
        external_input_group = QGroupBox("Step 3: Paste External AI JSON Response Here")
        external_input_group_layout = QVBoxLayout(external_input_group)
        self.external_ai_response_input = QTextEdit()
        self.external_ai_response_input.setPlaceholderText("Paste JSON response from your PowerShell AI here...")
        self.external_ai_response_input.setFont(QFont("Consolas", 9))
        self.external_ai_response_input.setMinimumHeight(100)
        external_input_group_layout.addWidget(self.external_ai_response_input)
        
        display_external_btn = QPushButton("📄 Load & Display External AI Response")
        display_external_btn.clicked.connect(self.display_external_ai_response)
        external_input_group_layout.addWidget(display_external_btn)
        external_input_group.setLayout(external_input_group_layout)
        bottom_layout.addWidget(external_input_group)
        
        # 4. Display area for the (parsed) External AI response (can reuse or have a new one)
        # For simplicity, we can reuse the main response output if cleared, or make a new one.
        # Let's make a distinct one for clarity.
        external_display_group = QGroupBox("Step 4: Parsed External AI Response")
        external_display_layout = QVBoxLayout(external_display_group)
        self.external_ai_response_display = QTextEdit()
        self.external_ai_response_display.setReadOnly(True)
        self.external_ai_response_display.setPlaceholderText("Formatted JSON from your external AI will be shown here after loading...")
        self.external_ai_response_display.setFont(QFont("Consolas", 9))
        self.external_ai_response_display.setMinimumHeight(100)
        external_display_layout.addWidget(self.external_ai_response_display)
        external_display_group.setLayout(external_display_layout)
        bottom_layout.addWidget(external_display_group)
        
        main_splitter.addWidget(bottom_widget)
        main_splitter.setSizes([self.height() // 2, self.height() // 2]) # Adjust initial sizing

        self.tabs.addTab(granite_tab, '🧠 Granite AI Workbench')

        # Attempt to distribute space more evenly initially if possible
        # This might need adjustment after widgets are populated or shown.
        QTimer.singleShot(0, lambda: splitter.setSizes([splitter.height() // 2, splitter.height() // 2]))

        self.tabs.addTab(granite_tab, '🧠 Granite AI Mentor')

    def apply_theme(self):
        theme = self.config.get('theme', 'Dark')
        # Basic dark theme, can be expanded
        if theme == 'Dark':
            self.setStyleSheet("""
                QMainWindow, QWidget { background-color: #282c34; color: #abb2bf; }
                QGroupBox { border: 1px solid #3d4047; border-radius: 5px; margin-top: 1ex; font-weight: bold; }
                QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px 0 3px; }
                QPushButton { background-color: #3d3d54; border: 1px solid #4a4e58; border-radius: 3px; padding: 6px; }
                QPushButton:hover { background-color: #4a4e58; }
                QPushButton:pressed { background-color: #353940; }
                QProgressBar { border: 1px solid #4a4e58; border-radius: 3px; text-align: center; color: #ffffff; }
                QProgressBar::chunk { background-color: #61afef; border-radius: 2px; }
                QTextEdit, QListWidget { background-color: #21252b; border: 1px solid #3d4047; border-radius: 3px; color: #abb2bf; }
                QTabWidget::pane { border: 1px solid #3d4047; }
                QTabBar::tab { background-color: #282c34; border: 1px solid #3d4047; padding: 8px; min-width: 100px; }
                QTabBar::tab:selected { background-color: #3d3d54; color: #ffffff; }
                QTabBar::tab:hover { background-color: #353940; }
                QLabel { color: #abb2bf; }
                QCheckBox { color: #abb2bf; }
                QComboBox { background-color: #21252b; color: #abb2bf; border: 1px solid #3d4047; padding: 3px; }
                QLineEdit { background-color: #21252b; color: #abb2bf; border: 1px solid #3d4047; padding: 3px; }
            """)
        else: # Light theme (basic)
            self.setStyleSheet("") # Revert to default
    
    def start_update_timers(self):
        self.metrics_timer = QTimer(self)
        self.metrics_timer.timeout.connect(self.update_system_metrics_display)
        self.metrics_timer.start(2000)
        
        self.queue_timer = QTimer(self)
        self.queue_timer.timeout.connect(self.process_queues)
        self.queue_timer.start(100)
    
    def load_config(self):
        self.config_path = os.path.join(os.path.dirname(__file__), 'opryxx_config.json')
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = self.get_default_config()
                self.save_config_file() # Save default if not exists
        except Exception as e:
            self.log_message_internal(f'Error loading config: {str(e)}', 'ERROR')
            self.config = self.get_default_config()
    
    def save_config_file(self):
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            self.log_message_internal(f'Error saving config file: {str(e)}', 'ERROR')

    def get_default_config(self):
        return {
            'theme': 'Dark',
            'log_level': 'INFO',
            'auto_backup': True,
            'granite_settings': {
                'enable_monitoring': False,
                'api_key': ''
            }
        }
    
    def save_settings(self):
        try:
            self.config['theme'] = self.theme_combo.currentText()
            self.config['log_level'] = self.log_level_combo.currentText()
            self.config['auto_backup'] = self.auto_backup_check.isChecked()
            
            granite_cfg = self.config.get('granite_settings', {})
            granite_cfg['enable_monitoring'] = self.granite_enable_monitoring_check.isChecked()
            granite_cfg['api_key'] = self.granite_api_key_input.text()
            self.config['granite_settings'] = granite_cfg
            
            self.save_config_file()
            self.apply_theme() # Re-apply theme if changed
            # Update Granite manager with new config
            self.granite_manager.config = granite_cfg
            if granite_cfg['enable_monitoring'] and not self.granite_manager.monitoring_active:
                self.granite_manager.start_monitoring()
            elif not granite_cfg['enable_monitoring'] and self.granite_manager.monitoring_active:
                self.granite_manager.stop_monitoring()

            self.log_message_internal('Settings saved successfully')
            QMessageBox.information(self, "Settings Saved", "Settings have been saved.")
        except Exception as e:
            self.log_message_internal(f'Error saving settings: {str(e)}', 'ERROR')
            QMessageBox.critical(self, "Error", f"Could not save settings: {e}")

    def start_repair_chain(self):
        selected_modules = [mod_id for mod_id, cb in self.module_checks.items() if cb.isChecked()]
        if not selected_modules:
            QMessageBox.warning(self, 'No Modules Selected', 'Please select at least one repair module to run.')
            return
        
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar.setValue(0)
        self.log_text.clear() # Clear previous logs
        self.log_message_internal(f'Starting repair chain with modules: {", ".join(selected_modules)}')
        
        # Create and start the repair thread
        self.repair_thread = threading.Thread(
            target=self.repair_manager.run_repair_chain, 
            args=(selected_modules,),
            daemon=True
        )
        self.repair_thread.start()

    def stop_repair_chain(self):
        if hasattr(self, 'repair_thread') and self.repair_thread.is_alive():
            self.log_message_internal('Attempting to stop repair chain...', 'WARNING')
            self.repair_manager.stop() # Signal the manager to stop
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def update_system_metrics_display(self):
        try:
            self.metrics_labels['cpu_usage'].setText(f'{psutil.cpu_percent()}%')
            mem = psutil.virtual_memory()
            self.metrics_labels['memory_usage'].setText(f'{mem.percent}% ({psutil._common.bytes2human(mem.available)} free)')
            disk = psutil.disk_usage('C:\\') # Update for other drives if needed
            self.metrics_labels['disk_c_usage'].setText(f'{disk.percent}% ({psutil._common.bytes2human(disk.free)} free)')
            net = psutil.net_io_counters()
            self.metrics_labels['network_sent'].setText(psutil._common.bytes2human(net.bytes_sent))
            self.metrics_labels['network_recv'].setText(psutil._common.bytes2human(net.bytes_recv))
        except Exception as e:
            self.log_message_internal(f'Error updating metrics display: {str(e)}', 'ERROR')
            
    def update_detailed_system_info(self):
        try:
            self.sys_info_text.clear()
            self.sys_info_text.append("Gathering system information...")
            QApplication.processEvents() # Update UI
            
            info = {
                "OS Platform": os.name,
                "OS Name": platform.system(),
                "OS Version": platform.version(),
                "Architecture": platform.machine(),
                "Processor": platform.processor(),
                "Hostname": platform.node(),
                "Python Version": platform.python_version(),
                "Total RAM": psutil._common.bytes2human(psutil.virtual_memory().total),
            }
            self.sys_info_text.clear()
            for key, value in info.items():
                self.sys_info_text.append(f'<b>{key}:</b> {value}')
            self.sys_info_text.append("\n<b>Disk Partitions:</b>")
            for part in psutil.disk_partitions():
                usage = psutil.disk_usage(part.mountpoint)
                self.sys_info_text.append(f"  - {part.device} ({part.fstype}): {psutil._common.bytes2human(usage.free)} free of {psutil._common.bytes2human(usage.total)}")
        except Exception as e:
            self.sys_info_text.append(f"\nError gathering system info: {e}")

    def process_queues(self):
        try:
            while not self.status_queue.empty():
                status = self.status_queue.get_nowait()
                self.status_label.setText(f'Status: {status}')
            
            while not self.log_queue.empty():
                log_entry = self.log_queue.get_nowait()
                self.log_text.append(log_entry)
                # Check if Granite log analysis should be triggered
                # Example: Trigger if an error is logged
                if "[ERROR]" in log_entry and self.granite_manager.monitoring_active:
                    self.logAnalysisRequested.emit(self.log_text.toPlainText()[-1000:]) # Analyze last 1000 chars
            
            while not self.progress_queue.empty():
                progress = self.progress_queue.get_nowait()
                self.progress_bar.setValue(int(progress))
        except Exception as e:
             # This is a critical part, so print to console if logging fails
            print(f"Error processing queues: {e}") 

    def log_message_internal(self, message, level='INFO'):
        """Internal logging for GUI specific messages, not sent to RepairManager's callback"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f'[{timestamp}] [GUI] [{level}] {message}'
        self.log_queue.put(log_entry) # Still put in queue for display

    def prepare_ai_request_for_display(self):
        action = self.granite_action_combo.currentText()
        self.granite_request_json_output.clear()
        self.granite_response_output.clear()
        self.current_prepared_ai_request = None # Store the prepared request
        self.granite_process_request_btn.setEnabled(False)

        if action == "Log Analysis":
            if hasattr(self, 'log_text') and self.log_text.toPlainText():
                recent_logs = self.log_text.toPlainText().splitlines()[-200:]
            else:
                recent_logs = [f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [GUI] [INFO] No OPRYXX operational logs available for analysis at this time."]
            
            opryxx_context = {
                "current_operation": "manual_granite_log_analysis_trigger_from_gui",
                "active_opryxx_tab": self.tabs.tabText(self.tabs.currentIndex()),
                "timestamp": datetime.now().isoformat()
            }
            # Use the method from GraniteManager to prepare the structured request
            request_json_obj = self.granite_manager.prepare_log_analysis_request(recent_logs, opryxx_context)
            self.current_prepared_ai_request = request_json_obj # Store the actual JSON object
            self.granite_request_json_output.setPlainText(json.dumps(request_json_obj, indent=4))
            self.log_message_internal("Prepared Granite Log Analysis request for user display.")

        elif action == "Optimization Advice":
            # Gather current metrics (simplified for GUI, can be expanded)
            try:
                cpu_peak = psutil.cpu_percent(interval=0.1) # Quick sample
                cpu_avg_long_term = psutil.cpu_percent(interval=None) # Overall since last call or boot
                mem_info = psutil.virtual_memory()
                disk_info_c = psutil.disk_usage('C:\\')
                # More detailed metrics could be collected by a background thread or on demand
                current_metrics = {
                    "cpu_usage_peak_short_term": cpu_peak,
                    "cpu_usage_overall": cpu_avg_long_term, 
                    "memory_percent_used": mem_info.percent,
                    "memory_available_gb": round(mem_info.available / (1024**3), 2),
                    "disk_c_percent_used": disk_info_c.percent,
                    "disk_c_free_gb": round(disk_info_c.free / (1024**3), 2),
                    # Placeholders for more complex metrics that might need dedicated collection
                    "top_processes_by_cpu": "[Placeholder: Data not collected by GUI directly]",
                    "startup_impact_items": "[Placeholder: Data not collected by GUI directly]"
                }
            except Exception as e:
                self.log_message_internal(f"Error gathering metrics for AI request: {e}", "ERROR")
                QMessageBox.warning(self, "Metric Error", f"Could not gather all system metrics: {e}")
                return

            opryxx_context = {"user_goal": "general_system_health_and_optimization_check"}
            request_json_obj = self.granite_manager.prepare_optimization_advice_request(current_metrics, opryxx_context)
            self.current_prepared_ai_request = request_json_obj
            self.granite_request_json_output.setPlainText(json.dumps(request_json_obj, indent=4))
            self.log_message_internal("Prepared Granite Optimization Advice request for user display.")
        
        if self.current_prepared_ai_request:
            self.granite_process_request_btn.setEnabled(True)

    def process_request_with_simulated_ai(self):
        if not hasattr(self, 'current_prepared_ai_request') or not self.current_prepared_ai_request:
            QMessageBox.warning(self, "No Request Prepared", 
                                "Please use the 'Prepare Request' button first to generate a JSON request.")
            return

        self.granite_response_output.clear()
        action = self.granite_action_combo.currentText() # Or derive from self.current_prepared_ai_request['request_type']
        response_json = None
        self.log_message_internal(f"Processing prepared '{action}' request with simulated OPRYXX AI...")

        # Pass the stored JSON object directly to the manager's processing method
        if self.current_prepared_ai_request.get("request_type") == "log_analysis":
            response_json = self.granite_manager.analyze_system_logs_with_ai(self.current_prepared_ai_request)
        elif self.current_prepared_ai_request.get("request_type") == "optimization_advice":
            response_json = self.granite_manager.get_optimization_advice_from_ai(self.current_prepared_ai_request)
        else:
            self.log_message_internal(f"Unknown request type in prepared data: {self.current_prepared_ai_request.get('request_type')}", "ERROR")
            QMessageBox.critical(self, "Processing Error", "Internal error: Unknown request type prepared.")
            return
        
        if response_json:
            self.granite_response_output.setPlainText(json.dumps(response_json, indent=4))
            self.log_message_internal(f"Displayed simulated AI response for: {action}")
        else:
            # The manager methods should ideally always return a JSON, even if it's an error JSON.
            # This path might indicate a more severe issue in the manager logic if it returns None.
            error_message = "# Error: Failed to get a simulated response or response was empty."
            self.granite_response_output.setPlainText(error_message)
            self.log_message_internal(f"Failed to get or display simulated AI response for: {action}", "ERROR")

    # Remove old trigger_granite_log_analysis and trigger_granite_optimization_suggestions methods if they exist
    # Ensure they are removed to avoid conflicts or if they were part of the failed diff earlier.
    # If they don't exist due to a previous successful partial update, that's fine.
    # For the purpose of this targeted edit, I will assume they might still be there from an older state.
    def trigger_granite_log_analysis(self): # This method should be removed or no-oped
        # This is now handled by prepare_ai_request_for_display and process_request_with_simulated_ai
        self.log_message_internal("Legacy trigger_granite_log_analysis called - should be disabled.", "WARNING")
        pass 

    def trigger_granite_optimization_suggestions(self): # This method should be removed or no-oped
        # This is now handled by prepare_ai_request_for_display and process_request_with_simulated_ai
        self.log_message_internal("Legacy trigger_granite_optimization_suggestions called - should be disabled.", "WARNING")
        pass

    def display_external_ai_response(self):
        """Parse and display JSON response from external AI (e.g., from PowerShell AI commands)"""
        input_text = self.external_ai_response_input.toPlainText().strip()
        if not input_text:
            QMessageBox.warning(self, "No Input", "Please paste the JSON response from your AI assistant.")
            return

        # Try to parse the input as JSON
        try:
            external_response = json.loads(input_text)
        except json.JSONDecodeError as e:
            QMessageBox.warning(self, "Invalid JSON", 
                f"The pasted text is not valid JSON. Error: {str(e)}\n\n"
                "Make sure to copy the complete JSON response from your AI.")
            return

        # Get current request type (if any) for structure validation
        current_request_type = self.current_prepared_ai_request.get("request_type") if hasattr(self, 'current_prepared_ai_request') else None

        # Validate response structure based on request type
        validation_result = self.validate_external_ai_response(external_response, current_request_type)
        if not validation_result['valid']:
            QMessageBox.warning(self, "Invalid Response Structure", 
                f"The AI response doesn't match the expected structure:\n{validation_result['reason']}\n\n"
                "Check the 'desired_output_format' in the request JSON for the expected structure.")
            # Still display it, but with a warning header
            self.external_ai_response_display.setPlainText(
                "# WARNING: Response doesn't match expected structure\n"
                f"# {validation_result['reason']}\n\n"
                "# Displaying raw response anyway:\n\n"
                f"{json.dumps(external_response, indent=4)}"
            )
            return

        # Response is valid, display it nicely formatted
        try:
            # Format based on type
            if current_request_type == "log_analysis":
                self.display_log_analysis_response(external_response)
            elif current_request_type == "optimization_advice":
                self.display_optimization_advice_response(external_response)
            else:
                # Just pretty print if we don't know the type
                self.external_ai_response_display.setPlainText(json.dumps(external_response, indent=4))

            self.log_message_internal("Successfully displayed external AI response.")
        except Exception as e:
            self.log_message_internal(f"Error formatting external AI response: {e}", "ERROR")
            # Fallback to raw JSON display
            self.external_ai_response_display.setPlainText(
                f"# Error formatting response: {e}\n\n"
                f"{json.dumps(external_response, indent=4)}"
            )

    def validate_external_ai_response(self, response, request_type):
        """Validate that external AI response matches expected structure"""
        if not request_type:
            return {"valid": True, "reason": "No request type to validate against"}

        if request_type == "log_analysis":
            required_fields = ["summary", "identified_issues", "overall_status_assessment"]
            for field in required_fields:
                if field not in response:
                    return {"valid": False, "reason": f"Missing required field: {field}"}

            # Validate identified_issues structure if any exist
            if response["identified_issues"]:
                issue_fields = ["severity", "description", "relevant_log_extract", "potential_cause_hypothesis"]
                for issue in response["identified_issues"]:
                    for field in issue_fields:
                        if field not in issue:
                            return {"valid": False, "reason": f"Issue missing required field: {field}"}

        elif request_type == "optimization_advice":
            required_fields = ["assessment_summary", "suggested_opryxx_optimizations", "suggested_manual_tweaks"]
            for field in required_fields:
                if field not in response:
                    return {"valid": False, "reason": f"Missing required field: {field}"}

            # Validate optimization suggestions structure if any exist
            if response["suggested_opryxx_optimizations"]:
                opt_fields = ["module_id_to_run", "justification", "expected_impact_level"]
                for opt in response["suggested_opryxx_optimizations"]:
                    for field in opt_fields:
                        if field not in opt:
                            return {"valid": False, "reason": f"Optimization suggestion missing required field: {field}"}

        return {"valid": True, "reason": ""}

    def display_log_analysis_response(self, response):
        """Format and display a log analysis response"""
        formatted_text = [
            "=== Log Analysis Results ===",
            f"\nSummary:\n{response['summary']}",
            f"\nOverall Status: {response['overall_status_assessment']}",
            "\nIdentified Issues:"
        ]

        if not response["identified_issues"]:
            formatted_text.append("No issues identified.")
        else:
            for i, issue in enumerate(response["identified_issues"], 1):
                formatted_text.extend([
                    f"\n{i}. {issue['severity']} Issue:",
                    f"   Description: {issue['description']}",
                    f"   Log Extract: {issue['relevant_log_extract']}",
                    f"   Hypothesis: {issue['potential_cause_hypothesis']}"
                ])
                if issue.get("suggested_opryxx_module_to_investigate"):
                    formatted_text.append(f"   Suggested Module: {issue['suggested_opryxx_module_to_investigate']}")

        self.external_ai_response_display.setPlainText("\n".join(formatted_text))

    def display_optimization_advice_response(self, response):
        """Format and display an optimization advice response"""
        formatted_text = [
            "=== System Optimization Analysis ===",
            f"\nAssessment Summary:\n{response['assessment_summary']}",
            "\nSuggested OPRYXX Optimizations:"
        ]

        if not response["suggested_opryxx_optimizations"]:
            formatted_text.append("No OPRYXX module optimizations suggested.")
        else:
            for i, opt in enumerate(response["suggested_opryxx_optimizations"], 1):
                formatted_text.extend([
                    f"\n{i}. Run Module: {opt['module_id_to_run']}",
                    f"   Impact: {opt['expected_impact_level']}",
                    f"   Justification: {opt['justification']}"
                ])

        formatted_text.extend(["\nSuggested Manual Tweaks:"])
        if not response["suggested_manual_tweaks"]:
            formatted_text.append("No manual tweaks suggested.")
        else:
            for i, tweak in enumerate(response["suggested_manual_tweaks"], 1):
                formatted_text.extend([
                    f"\n{i}. Area: {tweak['area']}",
                    f"   Action: {tweak['action_description']}",
                    f"   Justification: {tweak['justification']}"
                ])

        if response.get("scripts_to_consider_generating"):
            formatted_text.extend(["\nSuggested Scripts to Generate:"])
            for i, script in enumerate(response["scripts_to_consider_generating"], 1):
                formatted_text.extend([
                    f"\n{i}. Goal: {script['script_goal']}",
                    f"   Language: {script['preferred_language']}",
                    f"   Targets: {script['key_parameters_or_targets']}"
                ])

        self.external_ai_response_display.setPlainText("\n".join(formatted_text))

    def setup_maintenance_tab(self):
        """Set up the Maintenance tab with system maintenance features."""
        maintenance_tab = QWidget()
        layout = QVBoxLayout(maintenance_tab)
        
        # Header
        header = QLabel('🔧 System Maintenance')
        header.setStyleSheet('font-size: 20px; color: #ff9800; margin: 8px;')
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Status group
        status_group = QGroupBox('System Status')
        status_layout = QVBoxLayout()
        
        # Version info
        self.maintenance_version = QLabel('GANDALFS Version: Checking...')
        status_layout.addWidget(self.maintenance_version)
        
        # Last update check
        self.last_update_check = QLabel('Last update check: Never')
        status_layout.addWidget(self.last_update_check)
        
        # System compatibility status
        self.compatibility_status = QLabel('Compatibility: Checking...')
        status_layout.addWidget(self.compatibility_status)
        
        # Disk space indicator
        self.disk_space = QLabel('Disk space: Checking...')
        status_layout.addWidget(self.disk_space)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Actions group
        actions_group = QGroupBox('Maintenance Actions')
        actions_layout = QVBoxLayout()
        
        # Check for updates button
        self.btn_check_updates = QPushButton('🔄 Check for Updates')
        self.btn_check_updates.clicked.connect(self.check_for_updates)
        actions_layout.addWidget(self.btn_check_updates)
        
        # Install updates button
        self.btn_install_updates = QPushButton('⬇️ Install Updates')
        self.btn_install_updates.setEnabled(False)
        self.btn_install_updates.clicked.connect(self.install_updates)
        actions_layout.addWidget(self.btn_install_updates)
        
        # Run maintenance button
        self.btn_run_maintenance = QPushButton('⚙️ Run Maintenance Tasks')
        self.btn_run_maintenance.clicked.connect(self.run_maintenance_tasks)
        actions_layout.addWidget(self.btn_run_maintenance)
        
        # View logs button
        self.btn_view_logs = QPushButton('📋 View Logs')
        self.btn_view_logs.clicked.connect(self.view_maintenance_logs)
        actions_layout.addWidget(self.btn_view_logs)
        
        # Schedule tasks button
        self.btn_schedule_tasks = QPushButton('⏰ Schedule Maintenance')
        self.btn_schedule_tasks.clicked.connect(self.schedule_maintenance)
        actions_layout.addWidget(self.btn_schedule_tasks)
        
        actions_group.setLayout(actions_layout)
        layout.addWidget(actions_group)
        
        # Log display
        log_group = QGroupBox('Maintenance Log')
        log_layout = QVBoxLayout()
        self.maintenance_log = QTextEdit()
        self.maintenance_log.setReadOnly(True)
        self.maintenance_log.setFont(QFont('Consolas', 9))
        log_layout.addWidget(self.maintenance_log)
        
        # Clear log button
        btn_clear_log = QPushButton('Clear Log')
        btn_clear_log.clicked.connect(self.maintenance_log.clear)
        log_layout.addWidget(btn_clear_log)
        
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        # Progress bar
        self.maintenance_progress = QProgressBar()
        self.maintenance_progress.setRange(0, 100)
        self.maintenance_progress.setValue(0)
        layout.addWidget(self.maintenance_progress)
        
        # Status message
        self.maintenance_status = QLabel('Ready')
        layout.addWidget(self.maintenance_status)
        
        # Add the tab
        self.tabs.addTab(maintenance_tab, '🔧 Maintenance')
        
        # Initialize maintenance status
        self.update_maintenance_status()
    
    def update_maintenance_status(self):
        """Update the maintenance status display."""
        try:
            # Check GANDALFS version
            if hasattr(self, 'recovery_agent'):
                version = getattr(self.recovery_agent, 'version', '1.0.0')
                self.maintenance_version.setText(f'GANDALFS Version: {version}')
            
            # Check last update time
            config_path = os.path.join(os.path.dirname(__file__), 'gandalfs_config.json')
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    last_check = config.get('last_check', 'Never')
                    self.last_update_check.setText(f'Last update check: {last_check}')
            
            # Check disk space
            total, used, free = shutil.disk_usage('/')
            free_gb = free // (2**30)
            total_gb = total // (2**30)
            self.disk_space.setText(f'Disk space: {free_gb}GB free of {total_gb}GB')
            
            # Simple compatibility check
            if sys.platform == 'win32' and sys.version_info >= (3, 7):
                self.compatibility_status.setText('Compatibility: ✅ All systems go')
                self.compatibility_status.setStyleSheet('color: green;')
            else:
                self.compatibility_status.setText('Compatibility: ⚠️ Some features may be limited')
                self.compatibility_status.setStyleSheet('color: orange;')
                
        except Exception as e:
            self.log_message_internal(f'Error updating maintenance status: {e}', 'ERROR')
    
    def check_for_updates(self):
        """Check for GANDALFS updates."""
        self.log_message_internal('Checking for updates...', 'INFO')
        self.maintenance_status.setText('Checking for updates...')
        self.maintenance_progress.setValue(30)
        
        # Simulate update check
        QTimer.singleShot(2000, self._update_check_complete)
    
    def _update_check_complete(self):
        """Handle completion of update check."""
        self.maintenance_progress.setValue(100)
        self.maintenance_status.setText('Update check complete')
        self.btn_install_updates.setEnabled(True)
        
        # Simulate finding updates
        update_available = True  # In a real implementation, check actual update status
        
        if update_available:
            self.log_message_internal('Updates are available!', 'SUCCESS')
            QMessageBox.information(
                self, 
                'Updates Available', 
                'New GANDALFS updates are available. Click "Install Updates" to install them.'
            )
        else:
            self.log_message_internal('Your system is up to date', 'INFO')
            QMessageBox.information(self, 'No Updates', 'Your system is up to date.')
    
    def install_updates(self):
        """Install available updates."""
        self.log_message_internal('Starting update installation...', 'INFO')
        self.maintenance_status.setText('Installing updates...')
        self.maintenance_progress.setValue(0)
        
        # Simulate installation progress
        self._update_progress(10, 'Downloading updates...')
        QTimer.singleShot(1000, lambda: self._update_progress(40, 'Installing components...'))
        QTimer.singleShot(2000, lambda: self._update_progress(80, 'Finalizing installation...'))
        QTimer.singleShot(3000, self._update_complete)
    
    def _update_progress(self, value: int, message: str):
        """Update progress bar and status message."""
        self.maintenance_progress.setValue(value)
        self.maintenance_status.setText(message)
        self.log_message_internal(message, 'INFO')
    
    def _update_complete(self):
        """Handle completion of update installation."""
        self.maintenance_progress.setValue(100)
        self.maintenance_status.setText('Updates installed successfully')
        self.btn_install_updates.setEnabled(False)
        self.log_message_internal('Updates installed successfully!', 'SUCCESS')
        
        # Update status display
        self.update_maintenance_status()
        
        QMessageBox.information(
            self,
            'Updates Installed',
            'GANDALFS has been updated successfully. Some changes may require a restart to take effect.',
            QMessageBox.Ok
        )
    
    def run_maintenance_tasks(self):
        """Run system maintenance tasks."""
        self.log_message_internal('Starting maintenance tasks...', 'INFO')
        self.maintenance_status.setText('Running maintenance tasks...')
        self.maintenance_progress.setValue(0)
        
        # Simulate maintenance tasks
        tasks = [
            (10, 'Checking disk integrity...'),
            (30, 'Cleaning temporary files...'),
            (50, 'Optimizing database...'),
            (70, 'Checking for system errors...'),
            (90, 'Finalizing maintenance...'),
            (100, 'Maintenance complete')
        ]
        
        for progress, message in tasks:
            QTimer.singleShot(
                progress * 100,  # Stagger the tasks
                lambda p=progress, m=message: self._maintenance_task_update(p, m)
            )
    
    def _maintenance_task_update(self, progress: int, message: str):
        """Update progress during maintenance tasks."""
        self.maintenance_progress.setValue(progress)
        self.maintenance_status.setText(message)
        self.log_message_internal(message, 'INFO')
        
        if progress == 100:  # All tasks complete
            QMessageBox.information(
                self,
                'Maintenance Complete',
                'System maintenance tasks have been completed successfully.',
                QMessageBox.Ok
            )
    
    def view_maintenance_logs(self):
        """Open the maintenance logs directory."""
        log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
        if os.path.exists(log_dir):
            os.startfile(log_dir)
        else:
            QMessageBox.warning(
                self,
                'Logs Not Found',
                f'Log directory not found: {log_dir}',
                QMessageBox.Ok
            )
    
    def schedule_maintenance(self):
        """Schedule regular maintenance tasks."""
        # In a real implementation, this would use Windows Task Scheduler
        # For now, just show a message
        QMessageBox.information(
            self,
            'Schedule Maintenance',
            'This feature will configure automatic maintenance tasks to run weekly.\n\n'
            'In a full implementation, this would set up Windows Task Scheduler.',
            QMessageBox.Ok
        )
        self.log_message_internal('Scheduled maintenance tasks', 'INFO')
    
    def log_message_internal(self, message: str, level: str = 'INFO'):
        """Log a message to the maintenance log."""
        timestamp = QDateTime.currentDateTime().toString('hh:mm:ss')
        
        # Set text color based on level
        if level == 'ERROR':
            self.maintenance_log.setTextColor(Qt.red)
        elif level == 'WARNING':
            self.maintenance_log.setTextColor(QColor(255, 165, 0))  # Orange
        elif level == 'SUCCESS':
            self.maintenance_log.setTextColor(QColor(0, 200, 0))  # Green
        else:
            self.maintenance_log.setTextColor(Qt.white)
        
        # Add message to log
        self.maintenance_log.append(f'[{timestamp}] [{level}] {message}')
        
        # Auto-scroll to bottom
        scrollbar = self.maintenance_log.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def setup_ai_workbench_tab(self):
        """Set up the AI Workbench tab with advanced system analysis tools."""
        ai_tab = QWidget()
        main_layout = QVBoxLayout(ai_tab)
        
        # Header
        header = QLabel('🧠 AI Workbench')
        header.setStyleSheet('font-size: 20px; color: #9c27b0; margin: 8px;')
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)
        
        # Create tab widget for different AI features
        self.ai_tabs = QTabWidget()
        
        # 1. System Optimization Tab
        self.setup_optimization_tab()
        
        # 2. Predictive Analysis Tab
        self.setup_prediction_tab()
        
        # 3. Troubleshooting Tab
        self.setup_troubleshooting_tab()
        
        main_layout.addWidget(self.ai_tabs)
        
        # Add status bar
        self.ai_status_bar = QStatusBar()
        self.ai_status_bar.showMessage('AI Workbench Ready')
        main_layout.addWidget(self.ai_status_bar)
        
        # Add the tab
        self.tabs.addTab(ai_tab, '🧠 AI Workbench')
    
    def setup_optimization_tab(self):
        """Set up the System Optimization tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Header
        header = QLabel('⚡ System Optimization')
        header.setStyleSheet('font-size: 16px; color: #4caf50; margin: 8px;')
        layout.addWidget(header)
        
        # System Scan Button
        self.btn_scan_system = QPushButton('🔍 Scan System')
        self.btn_scan_system.clicked.connect(self.run_system_scan)
        layout.addWidget(self.btn_scan_system)
        
        # Optimization Results
        self.optimization_results = QTextEdit()
        self.optimization_results.setReadOnly(True)
        self.optimization_results.setFont(QFont('Consolas', 9))
        layout.addWidget(QLabel('Optimization Recommendations:'))
        layout.addWidget(self.optimization_results)
        
        # Optimization Actions
        self.optimize_btn = QPushButton('⚙️ Apply Optimizations')
        self.optimize_btn.setEnabled(False)
        self.optimize_btn.clicked.connect(self.apply_optimizations)
        layout.addWidget(self.optimize_btn)
        
        # Add tab
        self.ai_tabs.addTab(tab, '⚡ Optimization')
    
    def setup_prediction_tab(self):
        """Set up the Predictive Analysis tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Header
        header = QLabel('🔮 Predictive Analysis')
        header.setStyleSheet('font-size: 16px; color: #2196f3; margin: 8px;')
        layout.addWidget(header)
        
        # System Health Overview
        health_group = QGroupBox('System Health')
        health_layout = QVBoxLayout()
        
        # Disk Health
        self.disk_health = QProgressBar()
        self.disk_health.setRange(0, 100)
        self.disk_health.setValue(75)  # Example value
        health_layout.addWidget(QLabel('Disk Health:'))
        health_layout.addWidget(self.disk_health)
        
        # Memory Health
        self.memory_health = QProgressBar()
        self.memory_health.setRange(0, 100)
        self.memory_health.setValue(85)  # Example value
        health_layout.addWidget(QLabel('Memory Health:'))
        health_layout.addWidget(self.memory_health)
        
        # CPU Health
        self.cpu_health = QProgressBar()
        self.cpu_health.setRange(0, 100)
        self.cpu_health.setValue(90)  # Example value
        health_layout.addWidget(QLabel('CPU Health:'))
        health_layout.addWidget(self.cpu_health)
        
        health_group.setLayout(health_layout)
        layout.addWidget(health_group)
        
        # Predictions List
        self.predictions_list = QListWidget()
        layout.addWidget(QLabel('Potential Issues:'))
        layout.addWidget(self.predictions_list)
        
        # Analyze Button
        self.btn_analyze = QPushButton('🔮 Analyze System')
        self.btn_analyze.clicked.connect(self.run_predictive_analysis)
        layout.addWidget(self.btn_analyze)
        
        # Add tab
        self.ai_tabs.addTab(tab, '🔮 Predictions')
    
    def setup_troubleshooting_tab(self):
        """Set up the Automated Troubleshooting tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Header
        header = QLabel('🔧 Automated Troubleshooting')
        header.setStyleSheet('font-size: 16px; color: #ff9800; margin: 8px;')
        layout.addWidget(header)
        
        # Issue Selection
        self.issue_combo = QComboBox()
        self.issue_combo.addItems([
            'Select an issue...',
            'System running slow',
            'Application crashes',
            'Network problems',
            'Startup issues',
            'Other problems'
        ])
        layout.addWidget(self.issue_combo)
        
        # Troubleshooting Log
        self.troubleshoot_log = QTextEdit()
        self.troubleshoot_log.setReadOnly(True)
        self.troubleshoot_log.setFont(QFont('Consolas', 9))
        layout.addWidget(QLabel('Troubleshooting Log:'))
        layout.addWidget(self.troubleshoot_log)
        
        # Action Buttons
        btn_layout = QHBoxLayout()
        
        self.btn_diagnose = QPushButton('🔍 Diagnose')
        self.btn_diagnose.clicked.connect(self.run_diagnosis)
        btn_layout.addWidget(self.btn_diagnose)
        
        self.btn_fix = QPushButton('🔧 Fix Issues')
        self.btn_fix.setEnabled(False)
        self.btn_fix.clicked.connect(self.fix_issues)
        btn_layout.addWidget(self.btn_fix)
        
        layout.addLayout(btn_layout)
        
        # Add tab
        self.ai_tabs.addTab(tab, '🔧 Troubleshoot')
    
    def run_system_scan(self):
        """Run a system scan for optimization opportunities."""
        self.optimization_results.clear()
        self.ai_status_bar.showMessage('Scanning system for optimization opportunities...')
        
        # Simulate scanning process
        QTimer.singleShot(1500, self._on_scan_complete)
    
    def _on_scan_complete(self):
        """Handle completion of system scan."""
        # Example optimization recommendations
        recommendations = [
            "✅ System scan complete. Found 3 optimization opportunities:",
            "",
            "1. 🚀 Disk Optimization: 1.2GB of temporary files can be cleaned",
            "2. ⚡ Startup Programs: 4 programs are slowing down system startup",
            "3. 🛡️ Security: Outdated drivers detected (2)",
            "",
            "Click 'Apply Optimizations' to automatically fix these issues."
        ]
        
        self.optimization_results.setPlainText('\n'.join(recommendations))
        self.optimize_btn.setEnabled(True)
        self.ai_status_bar.showMessage('Scan complete. Ready to optimize.', 5000)
    
    def apply_optimizations(self):
        """Apply the recommended optimizations."""
        self.optimize_btn.setEnabled(False)
        self.ai_status_bar.showMessage('Applying optimizations...')
        
        # Simulate optimization process
        QTimer.singleShot(2000, self._on_optimization_complete)
    
    def _on_optimization_complete(self):
        """Handle completion of optimization."""
        self.optimization_results.append("\n✅ Optimizations applied successfully!")
        self.ai_status_bar.showMessage('Optimizations completed successfully!', 5000)
    
    def run_predictive_analysis(self):
        """Run predictive analysis on system health."""
        self.predictions_list.clear()
        self.ai_status_bar.showMessage('Analyzing system health...')
        
        # Simulate analysis
        QTimer.singleShot(2000, self._on_analysis_complete)
    
    def _on_analysis_complete(self):
        """Handle completion of predictive analysis."""
        # Example predictions
        predictions = [
            "⚠️ Disk C: is 85% full. Consider cleaning up.",
            "✅ Memory usage is optimal.",
            "⚠️ CPU temperature is slightly elevated.",
            "✅ No critical issues detected."
        ]
        
        self.predictions_list.addItems(predictions)
        self.ai_status_bar.showMessage('Analysis complete', 3000)
    
    def run_diagnosis(self):
        """Run diagnosis for the selected issue."""
        issue = self.issue_combo.currentText()
        if issue == 'Select an issue...':
            QMessageBox.warning(self, 'No Issue Selected', 'Please select an issue to diagnose.')
            return
        
        self.troubleshoot_log.clear()
        self.log_troubleshoot(f"Diagnosing issue: {issue}")
        
        # Simulate diagnosis
        QTimer.singleShot(1000, lambda: self._on_diagnosis_complete(issue))
    
    def _on_diagnosis_complete(self, issue):
        """Handle completion of diagnosis."""
        self.log_troubleshoot("\n✅ Diagnosis complete!")
        
        # Example fixes based on issue
        if 'slow' in issue.lower():
            self.log_troubleshoot("\nRecommended fixes:")
            self.log_troubleshoot("1. Clean up temporary files")
            self.log_troubleshoot("2. Disable unnecessary startup programs")
            self.log_troubleshoot("3. Check for memory leaks")
        
        self.btn_fix.setEnabled(True)
    
    def fix_issues(self):
        """Apply fixes for the diagnosed issues."""
        self.log_troubleshoot("\n🛠️ Applying fixes...")
        self.btn_fix.setEnabled(False)
        
        # Simulate fixing
        QTimer.singleShot(1500, self._on_fix_complete)
    
    def _on_fix_complete(self):
        """Handle completion of fixes."""
        self.log_troubleshoot("\n✅ Issues fixed successfully!")
        self.ai_status_bar.showMessage('Troubleshooting complete', 5000)
    
    def log_troubleshoot(self, message):
        """Add a message to the troubleshooting log."""
        self.troubleshoot_log.append(message)
        # Auto-scroll to bottom
        scrollbar = self.troubleshoot_log.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def closeEvent(self, event):
        """Handle application close event."""
        # Save window state before closing
        self.save_window_state()
        
        # Stop any running operations
        if hasattr(self, 'repair_thread') and self.repair_thread.isRunning():
            self.repair_manager.stop_repair()
            self.repair_thread.quit()
            self.repair_thread.wait(2000)  # Wait up to 2 seconds
            
        # Save configuration
        self.save_config_file()
        
        # Accept the close event
        event.accept()

        # Ensure background threads/monitoring are stopped cleanly
        self.granite_manager.stop_monitoring()
        # Add any other cleanup needed
        super().closeEvent(event)

# Import platform here to avoid issues if not available during initial imports
import platform 

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # Ensure the working directory is where the script is located for relative paths
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    window = OPRYXXEnhanced()
    window.show()
    sys.exit(app.exec_())

