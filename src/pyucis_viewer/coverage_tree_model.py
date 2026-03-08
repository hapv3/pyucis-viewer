'''
Created on Mar 29, 2020

@author: ballance
'''
from typing import Dict

from PyQt5 import QtWidgets, QtCore
from PyQt5.Qt import QStandardItemModel, QStandardItem, Qt

from pyucis_viewer.data_model_listener import DataModelListener
from ucis.report.coverage_report import CoverageReport
from ucis.report.coverage_report_builder import CoverageReportBuilder


class CoverageTreeModel(QStandardItemModel, DataModelListener):
    
    def __init__(self, waive_manager=None):
        QStandardItemModel.__init__(self, 0, 4)  # 4 columns: Name, Coverage, Status, Action
        self.db = None
        self.report = None
        self.waive_manager = waive_manager
        # Map QStandardItem to item path for waive tracking
        self.item_path_map = {}

#        self.setColumnCount(2)        
        

    def data_loaded(self, db):
        self.clear()
        self.db = db

        self.report = self.build_report(self.db)
        
        self.populate_model()
        # Note: must populate column names after model
        self.setHeaderData(0, Qt.Horizontal, "Name")
        self.setHeaderData(1, Qt.Horizontal, "Coverage")
        self.setHeaderData(2, Qt.Horizontal, "Status")
        self.setHeaderData(3, Qt.Horizontal, "Action")
        
    def build_report(self, db)->CoverageReport:
        report = CoverageReportBuilder.build(db)
        return report
    
    def populate_model(self):
        self.clear()
        self.item_path_map.clear()
        root = self.invisibleRootItem()
        
        for cg in self.report.covergroups:
            cg_n = QStandardItem("TYPE: " + cg.instname)
            cov_n = QStandardItem("%0.2f%%" % cg.coverage)
            cov_p = QStandardItem()
            cov_p.setData(round(cg.coverage, 2), QtCore.Qt.UserRole+1000)
            
            # Add action column
            action_n = QStandardItem()
            item_path = f"TYPE:{cg.instname}"
            self.item_path_map[id(cg_n)] = item_path
            if cg.coverage < 100.0:
                action_n.setData(item_path, QtCore.Qt.UserRole+3000)
                if self.waive_manager and self.waive_manager.is_waived(item_path):
                    action_n.setData(True, QtCore.Qt.UserRole+3001)  # Mark as waived
            
            root.appendRow([cg_n, cov_n, cov_p, action_n])
            
            # Add type coverpoints
            for cp in cg.coverpoints:
                self.populate_coverpoint(cg_n, cp, f"TYPE:{cg.instname}")
                
            for cr in cg.crosses:
                self.populate_cross(cg_n, cr, f"TYPE:{cg.instname}")

            for cg_i in cg.covergroups:                
                self.populate_covergroup_model(cg_n, cg_i, f"TYPE:{cg.instname}")
            
    def populate_covergroup_model(self, inst_n, cg, parent_path):
        cg_n = QStandardItem("INST: " + cg.name)
        cov_n = QStandardItem("%0.2f%%" % cg.coverage)
        cov_p = QStandardItem()
        cov_p.setData(round(cg.coverage, 2), QtCore.Qt.UserRole+1000)
        
        # Add action column
        action_n = QStandardItem()
        item_path = f"{parent_path}/INST:{cg.name}"
        self.item_path_map[id(cg_n)] = item_path
        if cg.coverage < 100.0:
            action_n.setData(item_path, QtCore.Qt.UserRole+3000)
            if self.waive_manager and self.waive_manager.is_waived(item_path):
                action_n.setData(True, QtCore.Qt.UserRole+3001)  # Mark as waived
        
        inst_n.appendRow([cg_n, cov_n, cov_p, action_n])
        
        for cp in cg.coverpoints:
            self.populate_coverpoint(cg_n, cp, item_path)
            
        for cr in cg.crosses:
            self.populate_cross(cg_n, cr, item_path)
    
    def populate_coverpoint(self, cg_n, cp, parent_path):
        cp_n = QStandardItem("CVP: " + cp.name)
        cov_n = QStandardItem("%0.2f%%" % cp.coverage)
        cov_p = QStandardItem()
        cov_p.setData(round(cp.coverage, 2), QtCore.Qt.UserRole+1000)
        
        # Add action column
        action_n = QStandardItem()
        item_path = f"{parent_path}/CVP:{cp.name}"
        self.item_path_map[id(cp_n)] = item_path
        if cp.coverage < 100.0:
            action_n.setData(item_path, QtCore.Qt.UserRole+3000)
            if self.waive_manager and self.waive_manager.is_waived(item_path):
                action_n.setData(True, QtCore.Qt.UserRole+3001)  # Mark as waived
        
        cg_n.appendRow([cp_n, cov_n, cov_p, action_n])
        
        for bn in cp.bins:
            self.populate_coverpoint_bin(cp_n, bn, item_path)
            

    def populate_coverpoint_bin(self, cp_n, bn, parent_path):
        bn_n = QStandardItem(bn.name)
        cov_n = QStandardItem("%d" % bn.count)
        cov_p = QStandardItem()
        cov_p.setData(bn.count, QtCore.Qt.UserRole+2000)
        
        # Add action column
        action_n = QStandardItem()
        item_path = f"{parent_path}/BIN:{bn.name}"
        self.item_path_map[id(bn_n)] = item_path
        if bn.count < bn.goal:
            action_n.setData(item_path, QtCore.Qt.UserRole+3000)
            if self.waive_manager and self.waive_manager.is_waived(item_path):
                action_n.setData(True, QtCore.Qt.UserRole+3001)  # Mark as waived
        
        cp_n.appendRow([bn_n, cov_n, cov_p, action_n])
        
    def populate_cross(self, cg_n, cr, parent_path):
        cr_n = QStandardItem("CROSS: " + cr.name)
        cov_n = QStandardItem("%0.2f%%" % cr.coverage)
        cov_p = QStandardItem()
        cov_p.setData(round(cr.coverage, 2), QtCore.Qt.UserRole+1000)
        
        # Add action column
        action_n = QStandardItem()
        item_path = f"{parent_path}/CROSS:{cr.name}"
        self.item_path_map[id(cr_n)] = item_path
        if cr.coverage < 100.0:
            action_n.setData(item_path, QtCore.Qt.UserRole+3000)
            if self.waive_manager and self.waive_manager.is_waived(item_path):
                action_n.setData(True, QtCore.Qt.UserRole+3001)  # Mark as waived
        
        cg_n.appendRow([cr_n, cov_n, cov_p, action_n])
        
        for bn in cr.bins:
            self.populate_coverpoint_bin(cr_n, bn, item_path)
    
