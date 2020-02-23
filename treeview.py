# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtCore
 
class Item(object):
    def __init__(self, _parent=None, _dict={}):
        self.dict = _dict
        self.parent_item = _parent
        self.children = []
    
    def appendChild(self, item):
        self.children.append(item)

    def data(self, column):
        if column in self.dict.keys():
            return self.dict[column]
        return ''
 
    def setData(self, column, data):
        self.dict[column] = data
    
    def child(self, row):
        return self.children[row]

    def childrenCount(self):
        return len(self.children)

    def hasChildren(self):
        return not self.childrenCount() == 0

    def hasParent(self):
        return not self.parent_item is None

    def parent(self):
        return self.parent_item

    def removeChild(self, row):
        del self.children[row]

    def row(self):
        if self.parent_item:
            return self.parent_item.children.index(self)
        return 0

class Model(QtCore.QAbstractItemModel):
    def __init__(self, parent_=None):
        super(Model, self).__init__(parent_)
        self.root_item = Item()
        self.root_item.setData('ID', 'root item')
        self.columns = []
 
    def addColumns(self, columns, parent=QtCore.QModelIndex()):
        self.beginInsertColumns(parent, self.columnCount(), self.columnCount() + len(columns) - 1)
        self.columns.extend(columns)
        self.endInsertColumns()
 
    def addItem(self, _dict={}, parent=QtCore.QModelIndex()):
        if parent == QtCore.QModelIndex():
            parent_item = self.root_item
        else:
            parent_item = parent.internalPointer()
        item = Item(parent_item, _dict)
        row = parent_item.childrenCount()
        self.beginInsertRows(parent, row, row)
        parent_item.children.insert( row, item )
        self.endInsertRows()
        return self.index(row, 0, parent)
        
    def column(self, key):
        return self.columns[key]
 
    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self.columns)
 
    def data(self, index, role):
        if not index.isValid():
            return QtCore.QVariant()
        if role == QtCore.Qt.EditRole or role == QtCore.Qt.DisplayRole:
            return index.internalPointer().data( self.column(index.column()) )
        return QtCore.QVariant()
 
    def flags(self, index):
        return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
 
    def headerData(self, i, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.columns[i]
        if orientation == QtCore.Qt.Vertical and role == QtCore.Qt.DisplayRole:
            return i + 1
 
    def index(self, row, column, parent):
        if not parent.isValid():
            parent_item = self.root_item
        else:
            parent_item = parent.internalPointer()

        if parent_item.childrenCount() > 0:
            return self.createIndex(row, column, parent_item.child(row))
        return QtCore.QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()
        child_item = index.internalPointer()
        if not child_item:
            return QtCore.QModelIndex()
        parent_item = child_item.parent()
        if parent_item == self.root_item:
            return QtCore.QModelIndex()
        return self.createIndex(parent_item.row(), 0, parent_item)
        
    def removeAllColumns(self):
        self.beginRemoveColumns(QtCore.QModelIndex(), 0, self.columnCount()-1)
        self.columns = []
        self.endRemoveColumns()
 
    def removeAllItems(self):
        self.beginRemoveRows(QtCore.QModelIndex(), 0, self.rowCount()-1)
        self.root_item.children = []
        self.endRemoveRows()

    def removeItem(self, index):
        parent = index.parent()
        if parent == QtCore.QModelIndex():
            parent_item = self.root_item
        else:
            parent_item = parent.internalPointer()
        self.beginRemoveRows(parent, index.row(), index.row())
        parent_item.removeChild(index.row())
        self.endRemoveRows()
 
    def rowCount(self, parent=QtCore.QModelIndex()):
        if not parent.isValid():
            return self.root_item.childrenCount()
        return parent.internalPointer().childrenCount()

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if role == QtCore.Qt.EditRole:
            index.internalPointer().setData( self.column(index.column()), value )
            return True
        return False
 
class Delegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent=None, setModelDataEvent=None):
        super(Delegate, self).__init__(parent)
        self.setModelDataEvent = setModelDataEvent
 
    def createEditor(self, parent, option, index):
        return QtWidgets.QLineEdit(parent)
 
    def setEditorData(self, editor, index):
        value = index.model().data(index, QtCore.Qt.DisplayRole)
        editor.setText(str(value))
 
    def setModelData(self, editor, model, index):
        model.setData(index, editor.text())
        if not self.setModelDataEvent is None:
            self.setModelDataEvent()
