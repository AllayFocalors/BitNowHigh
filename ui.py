import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import os
import BitNowHigh as bnh


class VideoEditorUI:
    def __init__(self, root):
        self.root = root
        self.root.title("哪炸闹海 BitNowHigh")
        self.root.geometry("900x700")
        self.root.resizable(True, True)

        # 初始化变量（提前定义）
        self.selected_file = ""
        self.resolution_mode = tk.StringVar(value = "scale")
        self.scale_factor = tk.DoubleVar(value = 1.0)
        self.custom_width = tk.IntVar(value = 1920)
        self.custom_height = tk.IntVar(value = 1080)
        self.quality = tk.IntVar(value = 30)
        self.speed = tk.DoubleVar(value = 1.0)
        self.codec = tk.StringVar(value = "H.264")

        # 创建主框架
        self.main_frame = ttk.Frame(root, padding = 10)
        self.main_frame.pack(fill = tk.BOTH, expand = True)

        # 创建标题
        self.create_header()

        # 创建文件选择区域
        self.create_file_selection()

        # 创建输出设置区域
        self.create_output_settings()

        # 创建按钮区域
        self.create_action_buttons()

    def create_header(self):
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill = tk.X, pady = (0, 15))

        header_label = ttk.Label(
            header_frame,
            text = "BitNowHigh",
            padding = 10
        )
        header_label.pack(side = tk.LEFT, fill = tk.X, expand = True)

    def create_file_selection(self):
        section_frame = ttk.LabelFrame(
            self.main_frame,
            text = "视频文件选择",
            padding = (15, 10)
        )
        section_frame.pack(fill = tk.X, pady = 5)

        # 文件选择按钮和显示
        file_frame = ttk.Frame(section_frame)
        file_frame.pack(fill = tk.X, pady = 5)

        self.file_entry = ttk.Entry(file_frame, state = 'readonly', width = 50)
        self.file_entry.pack(side = tk.LEFT, fill = tk.X, expand = True, padx = (0, 10))

        browse_btn = ttk.Button(
            file_frame,
            text = "浏览...",
            command = self.browse_file
        )
        browse_btn.pack(side = tk.RIGHT)


    def create_output_settings(self):
        section_frame = ttk.LabelFrame(
            self.main_frame,
            text = "输出设置",
            padding = (15, 10)
        )
        section_frame.pack(fill = tk.X, pady = 5)

        # 分辨率设置
        res_frame = ttk.Frame(section_frame)
        res_frame.pack(fill = tk.X, pady = 5)

        res_label = ttk.Label(res_frame, text = "分辨率设置:", width = 15, anchor = tk.W)
        res_label.pack(side = tk.LEFT)

        # 分辨率模式选择
        mode_frame = ttk.Frame(res_frame)
        mode_frame.pack(side = tk.LEFT, padx = 10)

        scale_radio = ttk.Radiobutton(
            mode_frame,
            text = "缩放倍数:",
            variable = self.resolution_mode,
            value = "scale"
        )
        scale_radio.pack(anchor = tk.W)

        scale_frame = ttk.Frame(mode_frame)
        scale_frame.pack(fill = tk.X, padx = (20, 0), pady = 2)

        scale_entry = ttk.Entry(scale_frame, textvariable = self.scale_factor, width = 8)
        scale_entry.pack(side = tk.LEFT)
        ttk.Label(scale_frame, text = "倍").pack(side = tk.LEFT, padx = (5, 0))

        custom_radio = ttk.Radiobutton(
            mode_frame,
            text = "自定义分辨率:",
            variable = self.resolution_mode,
            value = "custom"
        )
        custom_radio.pack(anchor = tk.W, pady = (10, 0))

        custom_frame = ttk.Frame(mode_frame)
        custom_frame.pack(fill = tk.X, padx = (20, 0), pady = 2)

        width_entry = ttk.Entry(custom_frame, textvariable = self.custom_width, width = 6)
        width_entry.pack(side = tk.LEFT)
        ttk.Label(custom_frame, text = "x").pack(side = tk.LEFT, padx = 5)
        height_entry = ttk.Entry(custom_frame, textvariable = self.custom_height, width = 6)
        height_entry.pack(side = tk.LEFT)
        ttk.Label(custom_frame, text = "像素").pack(side = tk.LEFT, padx = (5, 0))

        # 画质设置
        quality_frame = ttk.Frame(section_frame)
        quality_frame.pack(fill = tk.X, pady = 5)

        quality_label = ttk.Label(quality_frame, text = "视频画质:", width = 15, anchor = tk.W)
        quality_label.pack(side = tk.LEFT)

        quality_scale = ttk.Scale(
            quality_frame,
            from_ = 1,
            to = 51,
            variable = self.quality,
            length = 200
        )
        quality_scale.pack(side = tk.LEFT, padx = 10)

        self.quality_value = ttk.Label(quality_frame, text = "30", width = 3)
        self.quality_value.pack(side = tk.LEFT)
        self.quality.trace_add("write", self.update_quality_label)

        # 倍速设置
        speed_frame = ttk.Frame(section_frame)
        speed_frame.pack(fill = tk.X, pady = 5)

        speed_label = ttk.Label(speed_frame, text = "播放倍速:（开发中）", width = 15, anchor = tk.W)
        speed_label.pack(side = tk.LEFT)

        speed_entry = ttk.Entry(speed_frame, textvariable = self.speed, width = 8)
        speed_entry.pack(side = tk.LEFT, padx = 10)
        ttk.Label(speed_frame, text = "倍 (0.5 - 6400)").pack(side = tk.LEFT)

        # 编码设置
        codec_frame = ttk.Frame(section_frame)
        codec_frame.pack(fill = tk.X, pady = 5)

        codec_label = ttk.Label(codec_frame, text = "视频编码:", width = 15, anchor = tk.W)
        codec_label.pack(side = tk.LEFT)

        codec_combo = ttk.Combobox(
            codec_frame,
            textvariable = self.codec,
            width = 18,
            state = "readonly"
        )
        codec_combo['values'] = ("H.264", "H.265")
        codec_combo.pack(side = tk.LEFT, padx = 10)

    def create_action_buttons(self):
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill = tk.X, pady = 20)

        # 导出按钮
        export_btn = ttk.Button(
            button_frame,
            text = "导出视频",
            style = 'Primary.TButton',
            padding = 10,
            command = self.export_video
        )
        export_btn.pack(side = tk.RIGHT, padx = 10)

        # 开发者按钮
        dev_btn = ttk.Button(
            button_frame,
            text = "By AllayCloud",
            style = 'Secondary.TButton',
            padding = 10,
            command = self.show_developer_info
        )
        dev_btn.pack(side = tk.RIGHT)

    def browse_file(self):
        filetypes = (
            ('视频文件', '*.mp4 *.avi *.mov *.mkv *.flv *.wmv'),
            ('所有文件', '*.*')
        )
        file_path = filedialog.askopenfilename(
            title = "选择视频文件",
            filetypes = filetypes
        )

        if file_path:
            # 检查文件是否为视频格式
            video_exts = ('.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv')
            if not file_path.lower().endswith(video_exts):
                messagebox.showerror("错误", "请选择有效的视频文件格式！")
                return

            self.selected_file = file_path
            self.file_entry.config(state = 'normal')
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, file_path)
            self.file_entry.config(state = 'readonly')

            # 更新预览图

            # 显示成功消息
            filename = os.path.basename(file_path)
            messagebox.showinfo("文件已选择", f"已选择视频文件: {filename}")

    def update_quality_label(self, *args):
        self.quality_value.config(text = str(int(self.quality.get())))

    def export_video(self):
        if not self.selected_file:
            messagebox.showerror("错误", "请先选择一个视频文件！")
            return

        # 获取设置
        resolution_mode = self.resolution_mode.get()
        scale_factor = self.scale_factor.get()
        width = self.custom_width.get()
        height = self.custom_height.get()
        quality = self.quality.get()
        speed = self.speed.get()
        codec = self.codec.get()

        # 验证输入
        errors = []
        if resolution_mode == "scale" and (scale_factor <= 0 or scale_factor > 10):
            errors.append("缩放倍数必须在0.1到10之间")
        if resolution_mode == "custom" and (width <= 0 or height <= 0):
            errors.append("分辨率宽高必须大于0")
        if speed < 0.5 or speed > 6400.0:
            errors.append("播放倍速必须在0.5到6400之间")

        if errors:
            messagebox.showerror("输入错误", "\n".join(errors))
            return

        # 显示确认对话框
        resolution_info = f"缩放倍数: {scale_factor:.1f}倍" if resolution_mode == "scale" else f"分辨率: {width}x{height}"
        confirmation = (
            f"确认导出设置:\n\n"
            f"视频文件: {self.selected_file}\n"
            f"{resolution_info}\n"
            f"画质: {int(quality)}\n"
            f"倍速: {speed:.1f}倍\n"
            f"编码: {codec}\n\n"
            f"是否开始导出视频?"
        )

        if messagebox.askyesno("确认导出", confirmation):
            # 这里可以调用实际的视频导出函数
            messagebox.showinfo("导出开始", "视频导出过程已开始，请稍候...")
            # 实际导出功能需要在此处实现,scales=scale_factor,qual=quality,encoder = ((codec=='H.264')*'libx264'+(codec=='H.265')*'libx265')
            print('start generating')
            bnh.generate(self.selected_file,'output')
            print('done')

    def show_developer_info(self):
        info = (
'''哪炸闹海 BitNowHigh
AllayCloud 2025
> By AllayCloud-Studio: 
>    AllayFocalors
> Bilibili@悦灵AllayFocalors
> GitHub: https://github.com/AllayFocalors/BitNowHigh
该项目基于 Apache 2.0 License 开源
悦灵云工作室保留所有权利
'''

            )
        messagebox.showinfo("开发者信息", info)



if __name__ == "__main__":
    bnh.generate(r"C:\Users\minec\Videos\BiliDownloads\哪吒之魔童闹海\nezhaout.mp4", 'output')
    # root = tk.Tk()
    # app = VideoEditorUI(root)
    # root.mainloop()