'''
Created on Nov 25, 2025

@author: HaPham
'''
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, Optional
import os


class WaiveManager(object):
    """
    Manages waive data for coverage items.
    Handles loading, saving, and querying waive status from XML files.
    """
    
    def __init__(self):
        # Dictionary mapping item paths to waive records
        # Format: {"path": {"message": str, "timestamp": str, "waived": bool}}
        self.waives: Dict[str, dict] = {}
        self.coverage_file: Optional[str] = None
        self.waive_file_path: Optional[str] = None
        
    def load_waive_file(self, filepath: str) -> bool:
        """
        Load waive data from an XML file.
        
        Args:
            filepath: Path to the waive XML file
            
        Returns:
            True if file was loaded successfully, False otherwise
        """
        if not os.path.exists(filepath):
            return False
            
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
            
            # Get coverage file name from root attributes
            self.coverage_file = root.get('coverageFile', '')
            self.waive_file_path = filepath
            
            # Clear existing waives
            self.waives.clear()
            
            # Parse waive entries
            for waive_elem in root.findall('Waive'):
                path = waive_elem.get('path', '')
                waived = waive_elem.get('waived', 'false').lower() == 'true'
                timestamp = waive_elem.get('timestamp', '')
                
                message_elem = waive_elem.find('Message')
                message = message_elem.text if message_elem is not None and message_elem.text else ''
                
                if path:
                    self.waives[path] = {
                        'waived': waived,
                        'message': message,
                        'timestamp': timestamp
                    }
                    
            return True
            
        except Exception as e:
            print(f"Error loading waive file {filepath}: {e}")
            return False
    
    def save_waive_file(self, filepath: Optional[str] = None) -> bool:
        """
        Save waive data to an XML file.
        
        Args:
            filepath: Path to save the waive XML file. If None, uses the last loaded path.
            
        Returns:
            True if file was saved successfully, False otherwise
        """
        if filepath is None:
            filepath = self.waive_file_path
            
        if filepath is None:
            return False
            
        try:
            # Create root element
            root = ET.Element('WaiveData')
            root.set('version', '1.0')
            if self.coverage_file:
                root.set('coverageFile', self.coverage_file)
            
            # Add waive entries
            for path, record in sorted(self.waives.items()):
                waive_elem = ET.SubElement(root, 'Waive')
                waive_elem.set('path', path)
                waive_elem.set('waived', 'true' if record['waived'] else 'false')
                waive_elem.set('timestamp', record['timestamp'])
                
                message_elem = ET.SubElement(waive_elem, 'Message')
                message_elem.text = record['message']
            
            # Create tree and write to file
            tree = ET.ElementTree(root)
            ET.indent(tree, space='  ')  # Pretty print
            tree.write(filepath, encoding='UTF-8', xml_declaration=True)
            
            self.waive_file_path = filepath
            return True
            
        except Exception as e:
            print(f"Error saving waive file {filepath}: {e}")
            return False
    
    def add_waive(self, item_path: str, message: str) -> None:
        """
        Add a waive entry for a coverage item.
        
        Args:
            item_path: Unique path identifier for the coverage item
            message: Waive message explaining the reason
        """
        timestamp = datetime.now().isoformat()
        self.waives[item_path] = {
            'waived': True,
            'message': message,
            'timestamp': timestamp
        }
    
    def remove_waive(self, item_path: str) -> None:
        """
        Remove a waive entry for a coverage item.
        
        Args:
            item_path: Unique path identifier for the coverage item
        """
        if item_path in self.waives:
            del self.waives[item_path]
    
    def is_waived(self, item_path: str) -> bool:
        """
        Check if a coverage item is waived.
        
        Args:
            item_path: Unique path identifier for the coverage item
            
        Returns:
            True if the item is waived, False otherwise
        """
        return item_path in self.waives and self.waives[item_path].get('waived', False)
    
    def get_waive_message(self, item_path: str) -> str:
        """
        Get the waive message for a coverage item.
        
        Args:
            item_path: Unique path identifier for the coverage item
            
        Returns:
            The waive message, or empty string if not waived
        """
        if item_path in self.waives:
            return self.waives[item_path].get('message', '')
        return ''
    
    def get_waive_timestamp(self, item_path: str) -> str:
        """
        Get the waive timestamp for a coverage item.
        
        Args:
            item_path: Unique path identifier for the coverage item
            
        Returns:
            The waive timestamp, or empty string if not waived
        """
        if item_path in self.waives:
            return self.waives[item_path].get('timestamp', '')
        return ''
    
    def set_coverage_file(self, coverage_file: str) -> None:
        """
        Set the associated coverage file name.
        
        Args:
            coverage_file: Name of the coverage file
        """
        self.coverage_file = coverage_file
    
    def get_default_waive_filepath(self, coverage_filepath: str) -> str:
        """
        Get the default waive file path for a coverage file.
        
        Args:
            coverage_filepath: Path to the coverage file
            
        Returns:
            Default path for the waive file
        """
        # Remove .xml extension if present and add .waive.xml
        base_path = coverage_filepath
        if base_path.endswith('.xml.gz'):
            base_path = base_path[:-7]
        elif base_path.endswith('.xml.lz4'):
            base_path = base_path[:-8]
        elif base_path.endswith('.xml'):
            base_path = base_path[:-4]
            
        return base_path + '.waive.xml'
