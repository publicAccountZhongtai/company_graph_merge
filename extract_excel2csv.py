# -*- coding: utf-8 -*-
"""
-------------------------------------------------
  File Name：   extract_excel2cav
  Description :
  Author :    sheng
  date：     2020/2/22
  filename:   extract_excel2csv

-------------------------------------------------
  Change Activity:
          2020/2/22:
-------------------------------------------------
"""
__author__ = 'sheng'

import xlrd
# import csv
# import xlwt
import pandas as pd

"""将excel表格中每个sheet导出到csv文件中"""


def csv_from_excel(excel_file):
    workbook = xlrd.open_workbook(excel_file)
    all_worksheets = workbook.sheet_names()
    for worksheet_name in all_worksheets:
        # data_xls = pd.read_excel(excel_file, worksheet_name, skiprows=[0], index_col=None)
        # if '_Details' in worksheet_name:
        data_xls = pd.read_excel(excel_file, worksheet_name, index_col=None)
        data_xls.to_csv(worksheet_name + '.csv', encoding='utf-8')
        # worksheet = workbook.sheet_by_name(worksheet_name)
    # your_csv_file = open(''.join([worksheet_name,'.csv']), 'wb')
    # wr = csv.writer(your_csv_file, quoting=csv.QUOTE_ALL)

    # for rownum in xrange(worksheet.nrows):
    #    wr.writerow([unicode(entry).encode("utf-8") for entry in worksheet.row_values(rownum)])
    # your_csv_file.close()


if __name__ == '__main__':
    filename = "documents/公司主体图谱实例.xlsx"
    csv_from_excel(filename)
