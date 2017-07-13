# -*- coding: utf-8 -*-
import xlwt
import xlrd

def new_excel():
    file = xlwt.Workbook()
    # 新建一个sheet
    table = file.add_sheet('info', cell_overwrite_ok=True)
    return file, table

def open_excel(file='file.xls'):
    try:
        data = xlrd.open_workbook(file)
        return data
    except Exception, e:
        print str(e)

def get_excel_table_data(file='file.xls', by_name=u'Sheet 1'):
    data = open_excel(file)
    table = data.sheet_by_name(by_name)
    nrows = table.nrows  #行数
    dict_data = {}
    index = 1
    for rownum in xrange(1, nrows):  #循环行数读取新文件中的数据
        row = table.row_values(rownum)
        dict_data.update({index: row})#结合要处理数据的逻辑处理数据的主要代码
    return dict_data


def main():
    table_data = get_excel_table_data(file='/home/yuan/product_uom.xls')# 读取文件　/home/yuan/product_uom.xls #excel文件地址
    new_file, new_excel_work_book = new_excel()#新建文件
    row_num = 0
    print table_data
    for key, val in table_data.iteritems(): #循环读取出来的数据 经过进一步的处理 写入新文件
         #new_excel_work_book.write(row_num, 0, str(key))   #对数据的处理　并写入新文件
         #new_excel_work_book.write(row_num, 1, ';'.join(list(set(val))))
         print "key", "----", key
         print "val", "----", val
    new_file.save('new_excel.xlsx') # 要保存的文件的位置

if __name__ == "__main__":
    main()

