'''
Created on Nov 25, 2025

@author: HaPham
'''
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                              QTextEdit, QPushButton, QDialogButtonBox)
from PyQt5.QtCore import Qt


class WaiveDialog(QDialog):
    """
    Dialog for entering waive messages for coverage items.
    """
    
    def __init__(self, item_name: str, coverage: float, parent=None):
        """
        Initialize the waive dialog.
        
        Args:
            item_name: Name of the coverage item being waived
            coverage: Current coverage percentage
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.item_name = item_name
        self.coverage = coverage
        self.waive_message = ""
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the dialog UI components."""
        self.setWindowTitle("Waive Coverage Item")
        self.setMinimumWidth(500)
        self.setMinimumHeight(300)
        
        # Main layout
        layout = QVBoxLayout()
        
        # Item information
        info_label = QLabel(f"<b>Coverage Item:</b> {self.item_name}")
        layout.addWidget(info_label)
        
        coverage_label = QLabel(f"<b>Current Coverage:</b> {self.coverage:.2f}%")
        layout.addWidget(coverage_label)
        
        # Separator
        layout.addSpacing(10)
        
        # Message label
        message_label = QLabel("<b>Waive Reason:</b>")
        layout.addWidget(message_label)
        
        # Message text edit
        self.message_edit = QTextEdit()
        self.message_edit.setPlaceholderText(
            "Enter the reason for waiving this coverage item...\n\n"
            "Examples:\n"
            "- This coverpoint is not reachable in the current test environment\n"
            "- This bin represents an illegal state that cannot occur\n"
            "- Feature is deprecated and will be removed"
        )
        layout.addWidget(self.message_edit)
        
        # Button box
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        
        # Set focus to message edit
        self.message_edit.setFocus()
    
    def accept(self):
        """Handle OK button click."""
        self.waive_message = self.message_edit.toPlainText().strip()
        
        # Require a non-empty message
        if not self.waive_message:
            # Show error - message is required
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "Message Required",
                "Please enter a reason for waiving this coverage item."
            )
            return
            
        super().accept()
    
    def get_message(self) -> str:
        """
        Get the waive message entered by the user.
        
        Returns:
            The waive message text
        """
        return self.waive_message
