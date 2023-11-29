import tkinter as tk
from tkinter import filedialog
import openpyxl
import json

class ExcelParserApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Excel Parser")
        self.master.geometry("400x320")

        self.choose_file_button = tk.Button(self.master, text="选择物流excel", command=self.choose_file)
        self.choose_file_button.pack(pady=10)

        self.choose_file_button2 = tk.Button(self.master, text="选择店铺excel", command=self.choose_file2)
        self.choose_file_button2.pack(pady=10)

        self.start_button = tk.Button(self.master, text="开始", command=self.start_parsing)
        self.start_button.pack(pady=20)
        self.file_path = None
        self.file_path2 = None

    def choose_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls")])

    def choose_file2(self):
        self.file_path2 = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls")])

    def start_parsing(self):
        if self.file_path is None or self.file_path2 is None:

            print("请先选择物流excel文件")
            return

        try:
            workbook = openpyxl.load_workbook(self.file_path)
            sheet = workbook.active

            data_dict = {}

            # 遍历C列和J列，形成json对象
            tempValue = ''
            for row in sheet.iter_rows(min_row=2, max_row=1000, min_col=3, max_col=11):
                waybill_number = row[0].value
                if(row[7].value !=  None):
                    value = row[7].value
                    tempValue = value
                else:
                    value = tempValue

                data_dict[waybill_number] = value

            # 将json对象打印出来
            print(json.dumps(data_dict, indent=2))

        except Exception as e:
            print(f"发生错误：{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ExcelParserApp(root)
    root.mainloop()
