# coding:utf-8
# auth: wendynail98@outlook.com

import os
import shutil
import tkinter as tk
from tkinter import simpledialog
import tkinter.messagebox as msg
from PIL import Image, ImageTk


class ImageHelperGUI(tk.Tk):
    """
    图片分类器的用户界面
    """

    def __init__(self):
        """Constructor"""
        super().__init__()
        
        self.title('图片分类助手')
        # self.geometry("800x600")
        
        # 默认分类
        self.categories = ['色图', '表情包', '美女', '待删除']
        # 源文件列表
        self.filelist = None
        # 当前图片的名字
        self.current_filename = None
        
        self.setupUI()
        
    def setupUI(self):
        '''创建控件和布局'''
        
        # 使用两个变量表示存储图片的路径和需要将图片保存的路径
        self.source_dir_var = tk.StringVar()
        self.dest_dir_var = tk.StringVar()
        
        # 源路径和目标路径的输入框
        tk.Label(self, text="源路径:", width=10).grid(row=0, column=0, ipadx=20)
        tk.Entry(self, textvariable=self.source_dir_var, width=15).grid(row=0, column=1)
        tk.Label(self, text="目标路径:", width=10).grid(row=0, column=2, ipadx=20)
        tk.Entry(self, textvariable=self.dest_dir_var, width=15).grid(row=0, column=3)        
        
        # 路径确认按钮，点击后调用modify_dir函数
        tk.Button(self, text="确认路径", command=self.modify_dir, width=10).grid(row=0, column=5)
        
        # 显示图片，打开初始图片并显示
        img_open = Image.open('confirm.png')
        self.img_png = ImageTk.PhotoImage(img_open)
        self.label_img = tk.Label(self, image=self.img_png, width=300, height=400)
        self.label_img.grid(row=1, column=0, columnspan=4)
        self.label_img.bind("<Button-1>", self.set_focus_to_window)

        # 分类栏容器
        self.right_frame = tk.Frame(self, width=200, height=400)
        self.right_frame.grid(row=1, column=5)

    def set_focus_to_window(self, me):
        self.label_img.focus_set()
        
    def setupCategoriesUI(self):
        '''构建分类栏的UI界面以及用户操作'''
        
        
        # 分类容器
        self.category_canvas = tk.Canvas(self.right_frame)
        self.category_frame = tk.Frame(self.category_canvas)
        
        # 滚动条
        self.scrollbar = tk.Scrollbar(self.category_canvas, orient="vertical", command=self.category_canvas.yview)
        self.category_canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # 创建分类列表
        for i, category in enumerate(self.categories):
            category_label = tk.Label(self.category_frame, text="{}\t{}".format(i+1, category), pady=10)
            category_label.bind("<Button-1>", self.category_clicked)
            category_label.pack(side=tk.TOP, fill=tk.X)
        
        # 添加分类
        self.category_create = tk.Button(self.right_frame, text="添加分类", command=self.add_category)
        
        # 布局
        self.category_canvas.pack(fill=tk.X)
        self.category_frame.pack(fill=tk.X)
        self.category_create.pack(side=tk.BOTTOM, fill=tk.X)

        

        # 绑定键盘按键事件
        self.bind("<Key>", self.key_pressed)
    
    # 处理添加分类
    def add_category(self):
        category = simpledialog.askstring("输入分类", "输入分类名").strip()

        if len(category) > 0:
            self.categories.append(category)
            
            new_category = tk.Label(self.category_frame, text="{}\t{}".format(len(self.categories), category), pady=10)

            new_category.bind("<Button-1>", self.category_clicked)
            new_category.pack(side=tk.TOP, fill=tk.X)
        
    # 处理键盘按键事件
    def key_pressed(self, me):
        if me.char in list('123456789'):
            ind = int(me.char) - 1
            if ind < len(self.categories):
                category = self.categories[ind]
                self.classify(category)
    
    # 处理标签被点击的事件
    def category_clicked(self, me):
        # 获取被点击的对象
        category_label = me.widget
        category = category_label.cget("text")
        
        # 删除分类
        if msg.askyesno("删除分类", "确认删除  " + category + "  吗?"):
            me.widget.destroy()
            self.categories.remove(category)
            # 重排序号
            for widget in self.category_frame.winfo_children():
                widget.destroy()
            for i, category in enumerate(self.categories):
                category_label = tk.Label(self.category_frame, text="{}\t{}".format(i+1, category), pady=10)
                category_label.bind("<Button-1>", self.category_clicked)
                category_label.pack(side=tk.TOP, fill=tk.X)            
            
    # 处理图片分类
    def classify(self, category):
        # 移动文件
        src = os.path.join(self.source_dir, self.current_filename)
        dst = os.path.join(self.dest_dir, category)
        shutil.move(src, dst)
        
        # 渲染下一张图片
        ind = self.filelist.index(self.current_filename)
        if ind == len(self.filelist) - 1:
            # 这是最后一张图片
            msg.showinfo('提示','最后一张图片已完成分类')
        else:
            next_filename = self.filelist[ind+1]
            self.change_img(os.path.join(self.source_dir, next_filename))
            self.current_filename = next_filename
        
    # 确认路径的函数
    def modify_dir(self):
        # 确认路径合法
        self.source_dir = self.source_dir_var.get()
        self.dest_dir = self.dest_dir_var.get()
        
        if os.path.exists(self.source_dir):
            # 源路径存在
            self.filelist = os.listdir(self.source_dir)
            # 原路径不能为空
            if len(self.filelist) == 0:
                msg.showerror('错误','源路径下必须有文件')
                return
            self.current_filename = self.filelist[0]
            # 显示图片
            self.change_img(os.path.join(self.source_dir, self.current_filename))
            
            if not os.path.exists(self.dest_dir):
                a = msg.askokcancel('提示', '目标路径不存在，是否在当前路径下创建？')
                if a:
                    # 在当前路径下创建
                    os.mkdir(self.dest_dir)
                else:
                    # 重新输入路径
                    return
            if msg.askyesno("确认", "是否使用默认分类？"):
                for category in self.categories:
                    os.mkdir(os.path.join(self.dest_dir, category))
            elif msg.askyesno("确认", "是否使用目标分类？"):
                self.categories = []
                for f in os.listdir(self.dest_dir):
                    if os.path.isdir(os.path.join(self.dest_dir, f)):
                        self.categories.append(f)
            else:
                self.categories = []
            
            # 构建分类栏
            self.setupCategoriesUI()
            
        else:
            msg.showerror('错误','源路径不存在')
            return
    
    # 修改显示图片的函数
    def change_img(self, filename):
        # 打开图片
        img_open = Image.open(filename)
        
        # 获取图片大小
        w, h = img_open.size
        
        # 调整图片大小
        f1 = 300 / w
        f2 = 400 / h  
        factor = min([f1, f2])  
    
        width = int(w*factor)  
        height = int(h*factor)  
        img_open = img_open.resize((width, height), Image.ANTIALIAS)   
        
        # 更换图片
        self.img_png = ImageTk.PhotoImage(img_open)
        self.label_img.configure(image=self.img_png)


gui = ImageHelperGUI()
gui.mainloop()
