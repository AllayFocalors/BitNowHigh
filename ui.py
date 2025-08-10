# 用户界面模块

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import os
import BitNowHigh as bnh
from fractions import Fraction
import cv2
import os
import webbrowser


def get_video_info_opencv(video_path):
    """
    使用 OpenCV 获取视频信息
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"文件不存在: {video_path}")

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise ValueError("无法打开视频文件")

    # 获取视频属性
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    aspect_ratio = str(Fraction(width, height))
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # 计算时长
    duration = frame_count / fps if fps > 0 else 0

    # 转换为时分秒格式
    hours = int(duration // 3600)
    minutes = int((duration % 3600) // 60)
    seconds = int(duration % 60)
    duration_formatted = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    # 获取文件大小
    file_size_bytes = os.path.getsize(video_path)

    def format_file_size(size_bytes):
        if size_bytes == 0:
            return "0 B"
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        return f"{size_bytes:.2f} {size_names[i]}"

    file_size_formatted = format_file_size(file_size_bytes)

    cap.release()

    return {
        'width': width,
        'height': height,
        'aspect_ratio': aspect_ratio.replace('/', ':'),
        'duration_seconds': duration,
        'duration_formatted': duration_formatted,
        'file_size_bytes': file_size_bytes,
        'file_size_formatted': file_size_formatted,
        'fps': fps,
        'frame_count': frame_count
    }


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

        # 创建显示视频信息区域
        self.create_file_info()

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
        srcfile_frame = ttk.Frame(section_frame)
        srcfile_frame.pack(fill = tk.X, pady = 5)

        self.file_entry = ttk.Entry(srcfile_frame, state = 'readonly', width = 50)
        self.file_entry.pack(side = tk.LEFT, fill = tk.X, expand = True, padx = (0, 10))

        browse_btn = ttk.Button(
            srcfile_frame,
            text = "浏览源文件...",
            command = self.browse_file
        )
        browse_btn.pack(side = tk.RIGHT)

        outfile_frame = ttk.Frame(section_frame)
        outfile_frame.pack(fill = tk.X, pady = 5)

        self.Etr_output_filepath = ttk.Entry(outfile_frame, state = 'readonly', width = 50)
        self.Etr_output_filepath.pack(side = tk.LEFT, fill = tk.X, expand = True, padx = (0, 10))
        browse_btn = ttk.Button(
            outfile_frame,
            text = "浏览导出路径...",
            command = self.browse_output_dir
        )
        browse_btn.pack(side = tk.RIGHT)


    def create_file_info(self):
        section_frame = ttk.LabelFrame(
            self.main_frame,
            text = "视频信息",
            padding = (15, 10)
        )
        section_frame.pack(fill = tk.X, pady = 5)

        self.Lab_video_info = ttk.Label(section_frame,text="点击“浏览”并选择视频以查看信息", justify="left")
        self.Lab_video_info.pack(fill=tk.X)


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


        custom_frame = ttk.Frame(mode_frame)
        custom_frame.pack(fill = tk.X, padx = (20, 0), pady = 2,side='left')
        # 按比例缩放功能开发中
        # Lab_scale = ttk.Label(mode_frame,text="缩放倍数:")
        # Lab_scale.pack(side='left')
        #
        # scale_frame = ttk.Frame(mode_frame)
        # scale_frame.pack(fill = tk.X, padx = (20, 0), pady = 2)
        #
        # Scl_scale = ttk.Scale(
        #     scale_frame,
        #     from_ = 0.1,
        #     to = 24.0,
        #     variable = self.scale_factor,
        #     length = 150
        # )
        # Scl_scale.pack(side='left',padx=20)
        # # scale_entry = ttk.Entry(scale_frame, textvariable = self.scale_factor, width = 8)
        # # scale_entry.pack(side = tk.LEFT)
        # Lab_scale_value=ttk.Label(scale_frame, text = "倍")
        # Lab_scale_value.pack(side = tk.LEFT, padx = (5, 0))
        # self.scale_factor.trace_add("write", self.update_scale_label)


        width_entry = ttk.Entry(custom_frame, textvariable = self.custom_width, width = 6)
        width_entry.pack(side = tk.LEFT)
        ttk.Label(custom_frame, text = "x").pack(side = tk.LEFT, padx = 5)
        height_entry = ttk.Entry(custom_frame, textvariable = self.custom_height, width = 6)
        height_entry.pack(side = tk.LEFT)

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
            
            padding = 10,
            command = self.export_video
        )
        export_btn.pack(side = tk.RIGHT, padx = 10)

        # 开发者按钮
        dev_btn = ttk.Button(
            button_frame,
            text = "By AllayCloud",
            
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
            print("Selected file:", file_path)
            print(get_video_info_opencv(file_path))
            # 更新视频信息展示
            self.update_video_info()

    def browse_output_dir(self):
        self.output_dir = filedialog.askdirectory(
            title = "选择导出目录"
        )
        if self.output_dir:
            self.Etr_output_filepath.config(state = 'normal')
            self.Etr_output_filepath.delete(0, tk.END)
            self.Etr_output_filepath.insert(0, self.output_dir)
            self.Etr_output_filepath.config(state = 'readonly')
            print("Selected output directory:", self.output_dir)

    def update_video_info(self):
        video_info = get_video_info_opencv(self.selected_file)
        video_info = f'''帧宽度：{video_info['width']}
帧高度：{video_info['height']}
画幅比例：{video_info['aspect_ratio']} ({int(video_info['aspect_ratio'].split(':')[0])/int(video_info['aspect_ratio'].split(':')[1]):.2f}:1)
长度：{video_info['duration_formatted']}
视频大小：{video_info['file_size_formatted']}
帧速率：{video_info['fps']}
帧数量：{video_info['frame_count']}
'''

        self.Lab_video_info.config(text = video_info)

    def update_scale_label(self):#功能开发中
        # 获取当前缩放值并更新标签
        scale_value = self.scale_factor.get()
        # 如果 Lab_scale_value 存在则更新它
        if hasattr(self, 'Lab_scale_value'):
            self.Lab_scale_value.config(text = f"{scale_value:.1f}x")

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
        confirmation = (f'''
确认导出设置:
视频文件: {self.selected_file}
导出目录：{self.output_dir}
{resolution_info}
画质: {int(quality)}
分辨率：{width}x{height}
倍速: {speed:.1f}倍
编码: {codec}\n
是否开始导出视频?
提示：
FFmpeg主要使用的是CPU，请确保CPU性能足够！
''')
        if int(quality) <= 10:
            confirmation += '\n您选择的画质过高，请确保硬盘预留足够的空间！'
        if int(width) * int(height) >= 1920*1080*16:
            confirmation += '\n您选择的分辨率过大，已超过8K规格，请确保硬盘预留足够的空间，并确保CPU与运存性能足够！'

        if messagebox.askyesno("确认导出", confirmation):
            messagebox.showinfo("导出开始", "视频导出过程已开始，请稍候...")
            print('start generating')
            outfilepath = self.output_dir#这里的路径一定一定要以斜杠作为末尾
            outfilename = 'output'
            if not os.path.exists(outfilepath):
                os.mkdir(outfilepath)
            code = bnh.generate(
                self.selected_file,
                outfilename,
                outfilepath=outfilepath,
                width=width,
                height=height,
                qual=quality,
                encoder = ((codec=='H.264')*'libx264'+(codec=='H.265')*'libx265')
            )
            print('done')
            print(code)
            if code['code'] == '000':
                if os.path.isfile(code['file']):
                    messagebox.showinfo("导出完成", f"视频导出完成！已放在目录{outfilepath}下。感谢使用哪炸闹海！\n（去B站给悦灵一个关注好嘛？）")
                    webbrowser.open('https://space.bilibili.com/660052393')
                else:
                    messagebox.showerror("导出失败", "视频导出被异常中断，请检查终端输出内容。")
            else:
                messagebox.showerror("导出失败", f"视频导出失败！信息：{code}")

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
    root = tk.Tk()
    app = VideoEditorUI(root)
    root.mainloop()