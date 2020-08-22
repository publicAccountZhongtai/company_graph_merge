# coding=utf-8
import xlrd


def readexcel(xlsx):
    book = xlrd.open_workbook(xlsx)
    sheet = book.sheets()[0]
    elements = {}
    for j in range(sheet.ncols):
       elements[sheet.cell(0,j).value] = [i for i in sheet.col_values(j) if i != ''][1:]
    elements['概念'] = ['股东', '董监高法', '证券产品', '所属行业', '主营业务', '关联机构', '对外投资']
    return elements