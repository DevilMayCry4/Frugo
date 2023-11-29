import tkinter as tk
from tkinter import filedialog
import openpyxl
import json
import pandas as pd
import requests
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
        self.procesArray = None

    def choose_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls")])

    def choose_file2(self):
        self.file_path2 = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls")])

    def start_parsing(self):
        self.procesArray = self.parse_excel_to_array()
        self.process_nested_arrays()
        if self.file_path is None or self.file_path2 is None:
            if self.file_path is None:
                tk.messagebox.showinfo("提示", "请先选择物流excel文件")
            else:
                tk.messagebox.showinfo("提示", "请先选择店铺excel文件")
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

    def parse_excel_to_array(self):
        try:
            # 读取 Excel 文件的第一个表单
            df = pd.read_excel(self.file_path, sheet_name=0)

            # 将数据框转换为数组对象
            array_data = df.values.tolist()

            return array_data

        except Exception as e:
            # 如果发生异常，打印错误信息并返回空数组
            print(f"Error parsing Excel file: {e}")
            return []

    def process_nested_arrays(self):
        data_array = self.procesArray
        for item in data_array:
            if isinstance(item, list):
                # 取第3个值拼接到接口后面
                tracking_number = item[2]
                api_url = f"http://api.track.yw56.com.cn/api/tracking?nums={tracking_number}"

                # 取第7个值设置请求头
                authorization_header = {"Authorization": str(item[7])}

                # 发送请求
                try:
                    response = requests.get(api_url, headers=authorization_header)
                    response_data = response.json()

                    # 解析接口返回的结果
                    if isinstance(response_data, dict) and response_data.get("code") == 0:
                        print(f"成功: {response_data}")
                    else:
                        print(f"接口返回错误: {response_data}")

                except requests.RequestException as e:
                    print(f"请求错误: {e}")
if __name__ == "__main__":
    root = tk.Tk()
    app = ExcelParserApp(root)
    root.mainloop()
