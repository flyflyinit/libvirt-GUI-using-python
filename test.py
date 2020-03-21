from PyQt5.QtCore import QDateTime, Qt
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import (QWidget, QHeaderView, QHBoxLayout, QTableView,
                               QSizePolicy)
from PyQt5 import *
from qtpy import QtCharts

#from table_model import CustomTableModel


class Widget(QWidget):
    def __init__(self, data):
        QWidget.__init__(self)

        # Getting the Model
        #self.model = CustomTableModel(data)

        # Creating a QTableView
        self.table_view = QTableView()
        self.table_view.setModel(self.model)

        # QTableView Headers
        self.horizontal_header = self.table_view.horizontalHeader()
        self.vertical_header = self.table_view.verticalHeader()
        self.horizontal_header.setSectionResizeMode(QHeaderView.ResizeToContents)
        self.vertical_header.setSectionResizeMode(QHeaderView.ResizeToContents)
        self.horizontal_header.setStretchLastSection(True)

        # Creating QChart
        self.chart = QtCharts.QChart()
        self.chart.setAnimationOptions(QtCharts.QChart.AllAnimations)

        # Creating QChartView
        self.chart_view = QtCharts.QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)

        # QWidget Layout
        self.main_layout = QHBoxLayout()
        size = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        ## Left layout
        size.setHorizontalStretch(1)
        self.table_view.setSizePolicy(size)
        self.main_layout.addWidget(self.table_view)

        ## Right Layout
        size.setHorizontalStretch(4)
        self.chart_view.setSizePolicy(size)
        self.main_layout.addWidget(self.chart_view)

        # Set the layout to the QWidget
        self.setLayout(self.main_layout)
