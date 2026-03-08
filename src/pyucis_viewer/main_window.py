'''
Created on Mar 28, 2020

@author: ballance
'''
import sys

from PyQt5 import QtWidgets, QtCore
from PyQt5.Qt import QWidget, QHBoxLayout, QTreeView, QMainWindow, QIcon
from PyQt5.QtWidgets import QLabel, QGroupBox, QGridLayout, QSplitter, QAction
from PyQt5.uic.Compiler.qtproxies import QtGui

from pyucis_viewer.coverage_tree_model import CoverageTreeModel
from pyucis_viewer.data_model import DataModel
from pyucis_viewer.data_model_listener import DataModelListener
from pyucis_viewer.instance_tree import InstanceTree
from pyucis_viewer.instance_tree_model import InstanceTreeModel
from pyucis_viewer.waive_manager import WaiveManager
from pyucis_viewer.waive_dialog import WaiveDialog
import os


class MainWindow(QMainWindow, DataModelListener):
    
    def __init__(self, data_model : DataModel):
        super().__init__()
        self.data_model = data_model
        self.data_model.add_listener(self)
        
        # Create waive manager
        self.waive_manager = WaiveManager()
        self.coverage_file_path = None
        
        width=640
        height=480

        self.setWindowTitle("PyUCIS Viewer")
        self.setGeometry(10, 10, width, height)
        
        self.statusBar()
        
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu("&File")
        
        # Save waive data action
        saveWaiveAction = QAction("Save &Waive Data", self)
        saveWaiveAction.setShortcut("Ctrl+W")
        saveWaiveAction.triggered.connect(self.save_waive_data)
        fileMenu.addAction(saveWaiveAction)
        
        # Load waive data action
        loadWaiveAction = QAction("&Load Waive Data", self)
        loadWaiveAction.triggered.connect(self.load_waive_data)
        fileMenu.addAction(loadWaiveAction)
        
        fileMenu.addSeparator()
        
        exitAction = QAction(QIcon('exit.png'), "E&xit", self)
        exitAction.triggered.connect(self.do_exit)
        fileMenu.addAction(exitAction)
        
        
#         self.splitter = QSplitter()
        
        
#        self.horizontalGroupBox = QGroupBox(self)
#        layout = QGridLayout()
#        layout.setColumnStretch(1, 4)
#        layout.setColumnStretch(2, 4)

#        layout = QHBoxLayout()


#         self.instTreeModel = InstanceTreeModel()
#         self.data_model.add_listener(self.instTreeModel)
#         self.instTreeView = QTreeView()
#         self.instTreeView.setModel(self.instTreeModel)
#         self.splitter.addWidget(self.instTreeView)

        self.coverageTreeModel = CoverageTreeModel(self.waive_manager)
        self.data_model.add_listener(self.coverageTreeModel)
        self.coverageTree = QTreeView()
        self.progress_delegate = MainWindow.ProgressDelegate(self.coverageTree)
        self.coverageTree.setItemDelegateForColumn(2, self.progress_delegate)
        
        # Add waive button delegate for action column
        self.waive_delegate = MainWindow.WaiveButtonDelegate(self.coverageTree, self)
        self.coverageTree.setItemDelegateForColumn(3, self.waive_delegate)
        
        self.coverageTree.setModel(self.coverageTreeModel)
        self.coverageTree.show()
#        self.splitter.addWidget(self.coverageTree)
        
#        layout.addWidget(self.coverageTree)
#        self.setLayout(layout)
        self.setCentralWidget(self.coverageTree)

        # Set the initial split to 30/70        
#        self.splitter.setSizes([int(width*0.3), int(width*0.7)])
#        layout.addWidget(self.splitter, 0, 0)
        
#        self.horizontalGroupBox.setLayout(layout)

        self.show()

    def data_loaded(self, db):
        # Auto-load waive file if it exists
        if self.coverage_file_path:
            waive_file = self.waive_manager.get_default_waive_filepath(self.coverage_file_path)
            if os.path.exists(waive_file):
                self.waive_manager.load_waive_file(waive_file)
                # Refresh the tree to show waived items
                self.coverageTreeModel.populate_model()
    
    
    def set_coverage_file_path(self, filepath):
        """Set the coverage file path for waive file association."""
        self.coverage_file_path = filepath
        self.waive_manager.set_coverage_file(os.path.basename(filepath))
    
    def save_waive_data(self):
        """Save waive data to file."""
        if self.coverage_file_path:
            waive_file = self.waive_manager.get_default_waive_filepath(self.coverage_file_path)
            if self.waive_manager.save_waive_file(waive_file):
                self.statusBar().showMessage(f"Waive data saved to {waive_file}", 3000)
            else:
                self.statusBar().showMessage("Failed to save waive data", 3000)
        else:
            self.statusBar().showMessage("No coverage file loaded", 3000)
    
    def load_waive_data(self):
        """Load waive data from file."""
        from PyQt5.QtWidgets import QFileDialog
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Load Waive Data",
            "",
            "Waive Files (*.waive.xml);;All Files (*.*)"
        )
        if filepath:
            if self.waive_manager.load_waive_file(filepath):
                self.statusBar().showMessage(f"Waive data loaded from {filepath}", 3000)
                # Refresh the tree to show waived items
                self.coverageTreeModel.populate_model()
            else:
                self.statusBar().showMessage("Failed to load waive data", 3000)
    
    def waive_item(self, item_path, item_name, coverage):
        """Handle waiving a coverage item."""
        dialog = WaiveDialog(item_name, coverage, self)
        if dialog.exec_() == WaiveDialog.Accepted:
            message = dialog.get_message()
            self.waive_manager.add_waive(item_path, message)
            
            # Auto-save waive data
            self.save_waive_data()
            
            # Refresh the tree to show waived status
            self.coverageTreeModel.populate_model()
    
    def do_exit(self):
        print("Exit")
        sys.exit()
        
    class ProgressDelegate(QtWidgets.QStyledItemDelegate):
        def paint(self, painter, option, index):
            if index.data(QtCore.Qt.UserRole+1000) is not None:
                progress = int(index.data(QtCore.Qt.UserRole+1000))
                opt = QtWidgets.QStyleOptionProgressBar()
                opt.rect = option.rect
                opt.minimum = 0
                opt.maximum = 100
                opt.progress = progress
                opt.text = "{}%".format(progress)
                opt.textVisible = True
                QtWidgets.QApplication.style().drawControl(QtWidgets.QStyle.CE_ProgressBar, opt, painter)
            elif index.data(QtCore.Qt.UserRole+2000) is not None:
                progress = index.data(QtCore.Qt.UserRole+2000)
                opt = QtWidgets.QStyleOptionProgressBar()
                opt.rect = option.rect
                opt.minimum = 0
                opt.maximum = 100
                opt.progress = 100 if progress > 0 else 0
                opt.text = "{}".format(progress)
                opt.textVisible = True
                QtWidgets.QApplication.style().drawControl(QtWidgets.QStyle.CE_ProgressBar, opt, painter)
    
    class WaiveButtonDelegate(QtWidgets.QStyledItemDelegate):
        """Delegate for rendering waive buttons in the action column."""
        
        def __init__(self, parent, main_window):
            super().__init__(parent)
            self.main_window = main_window
        
        def paint(self, painter, option, index):
            # Check if this item has waive data
            item_path = index.data(QtCore.Qt.UserRole+3000)
            is_waived = index.data(QtCore.Qt.UserRole+3001)
            
            if item_path:
                # Draw button
                button_style = QtWidgets.QStyleOptionButton()
                button_style.rect = option.rect.adjusted(2, 2, -2, -2)
                button_style.text = "Waived" if is_waived else "Waive"
                button_style.state = QtWidgets.QStyle.State_Enabled
                if not is_waived:
                    button_style.state |= QtWidgets.QStyle.State_Raised
                
                QtWidgets.QApplication.style().drawControl(
                    QtWidgets.QStyle.CE_PushButton, button_style, painter
                )
        
        def editorEvent(self, event, model, option, index):
            # Handle button clicks
            if event.type() == QtCore.QEvent.MouseButtonRelease:
                item_path = index.data(QtCore.Qt.UserRole+3000)
                is_waived = index.data(QtCore.Qt.UserRole+3001)
                
                if item_path and not is_waived:
                    # Get item name and coverage from the same row
                    name_index = index.sibling(index.row(), 0)
                    cov_index = index.sibling(index.row(), 1)
                    
                    item_name = name_index.data(QtCore.Qt.DisplayRole)
                    cov_text = cov_index.data(QtCore.Qt.DisplayRole)
                    
                    # Parse coverage value
                    try:
                        if '%' in str(cov_text):
                            coverage = float(str(cov_text).replace('%', ''))
                        else:
                            coverage = 0.0
                    except:
                        coverage = 0.0
                    
                    # Show waive dialog
                    self.main_window.waive_item(item_path, item_name, coverage)
                    return True
            
            return super().editorEvent(event, model, option, index)
                
        