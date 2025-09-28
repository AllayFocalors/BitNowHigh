# 用户界面模块

from future.backports.email.utils import encode_rfc2231
from tkinter import ttk, messagebox, filedialog
from fractions import Fraction
from PIL import Image, ImageTk
import BitNowHigh as bnh
import tkinter as tk
import subprocess
import webbrowser
import pathlib
import cv2
import os

VERSION='0.1.2'

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
        self.root.geometry("900x800")
        self.root.resizable(True, True)

        self.selected_file = ""
        self.output_dir = ""
        self.resolution_mode = tk.StringVar(value = "scale")
        self.scale_factor = tk.DoubleVar(value = 1.0)
        self.custom_width = tk.IntVar(value = 1920)
        self.custom_height = tk.IntVar(value = 1080)
        self.quality = tk.IntVar(value = 30)
        self.speed = tk.DoubleVar(value = 1.0)
        self.codec = tk.StringVar(value = "H.264")
        self.GPUOn = tk.BooleanVar(value = False)
        self.fps = tk.Variable(value = 30.0)

        self.main_frame = ttk.Frame(root, padding = 10)
        self.main_frame.pack(fill = tk.BOTH, expand = True)

        self.create_scrollable_area()

        self.create_header()
        self.create_file_selection()

        self.create_scrollable_content()
        self.pack_scrollable_area()

        self.create_action_buttons()

    def pack_scrollable_area(self):
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def create_scrollable_area(self):
        self.canvas = tk.Canvas(self.main_frame)
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        self.scrollable_frame.bind("<MouseWheel>", _on_mousewheel)

        def _configure_canvas(event):
            canvas_width = event.width
            self.canvas.itemconfig(self.canvas.find_all()[0], width=canvas_width)

        self.canvas.bind("<Configure>", _configure_canvas)



    def create_header(self):
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill = tk.X, pady = (0, 15))

        header_label = ttk.Label(
            header_frame,
            text = f"哪炸闹海用户界面程序 BitNowHigh-UI-v{VERSION} BNH-v{BitNowHigh.VERSION}",
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
        Frm_srcfile = ttk.Frame(section_frame)
        Frm_srcfile.pack(fill = tk.X, pady = 5)
        self.Ent_file = ttk.Entry(Frm_srcfile, state = 'readonly', width = 50)
        self.Ent_file.pack(side = tk.LEFT, fill = tk.X, expand = True, padx = (0, 10))

        But_browseSrc = ttk.Button(
            Frm_srcfile,
            text = "浏览源文件...",
            width = 15,
            command = self.browse_file,
        )
        But_browseSrc.pack(side = tk.RIGHT)

        Frm_outfile = ttk.Frame(section_frame)
        Frm_outfile.pack(fill = tk.X, pady = 5)

        self.Ent_output_filepath = ttk.Entry(Frm_outfile, state = 'readonly', width = 50)
        self.Ent_output_filepath.pack(side = tk.LEFT, fill = tk.X, expand = True, padx = (0, 10))
        But_browseOut = ttk.Button(
            Frm_outfile,
            text = "浏览导出路径...",
            width = 15,
            command = self.browse_output_dir,
        )
        But_browseOut.pack(side = tk.RIGHT)

    def create_scrollable_content(self):
        self.create_file_info()
        self.create_output_settings()
        self.create_code_options()
        self.create_command_show()

    def create_file_info(self):
        section_frame = ttk.LabelFrame(
            self.scrollable_frame,
            text = "视频信息",
            padding = (15, 10)
        )
        section_frame.pack(fill = tk.X, pady = 5)

        self.Lab_video_info = ttk.Label(section_frame, text = "点击“浏览”并选择视频以查看信息", justify = "left")
        self.Lab_video_info.pack(fill = tk.X)

    def create_output_settings(self):
        section_frame = ttk.LabelFrame(
            self.scrollable_frame,
            text = "编辑选项",
            padding = (15, 10)
        )
        section_frame.pack(fill = tk.X, pady = 5)

        Frm_basename = ttk.Frame(section_frame)
        Frm_basename.pack(fill = tk.X, pady = 5)

        Lab_fileBaseName = ttk.Label(Frm_basename, text = "文件名:", width = 15, anchor = tk.W)
        Lab_fileBaseName.pack(side = tk.LEFT)

        self.Ent_fileBaseName = ttk.Entry(Frm_basename, width = 20)
        self.Ent_fileBaseName.pack(side = tk.LEFT, fill = tk.X, expand = True)

        Frm_res = ttk.Frame(section_frame)
        Frm_res.pack(fill = tk.X, pady = 5)

        Lab_res = ttk.Label(Frm_res, text = "分辨率设置:", width = 15, anchor = tk.W)
        Lab_res.pack(side = tk.LEFT)

        Frm_mode = ttk.Frame(Frm_res)
        Frm_mode.pack(side = tk.LEFT, padx = 0)

        Frm_custom = ttk.Frame(Frm_mode)
        Frm_custom.pack(fill = tk.X, padx = (5, 0), pady = 2, side = 'left')

        Ent_width = ttk.Entry(Frm_custom, textvariable = self.custom_width, width = 6)
        Ent_width.pack(side = tk.LEFT)
        ttk.Label(Frm_custom, text = "x").pack(side = tk.LEFT, padx = 0)
        Ent_height = ttk.Entry(Frm_custom, textvariable = self.custom_height, width = 6)
        Ent_height.pack(side = tk.LEFT)

        # 画质设置
        Frm_quality = ttk.Frame(section_frame)
        Frm_quality.pack(fill = tk.X, pady = 5)

        Lab_quality = ttk.Label(Frm_quality, text = "视频画质:", width = 15, anchor = tk.W)
        Lab_quality.pack(side = tk.LEFT)

        Scl_quality = ttk.Scale(
            Frm_quality,
            from_ = 1,
            to = 51,
            variable = self.quality,
            length = 200
        )
        Scl_quality.pack(side = tk.LEFT, padx = 10)

        self.Lab_quality_value = ttk.Label(Frm_quality, text = "30", width = 3)
        self.Lab_quality_value.pack(side = tk.LEFT)
        self.quality.trace_add("write", self.update_quality_label)

        Frm_speed = ttk.Frame(section_frame)
        Frm_speed.pack(fill = tk.X, pady = 5)

        Lab_speed = ttk.Label(Frm_speed, text = "播放倍速:", width = 15, anchor = tk.W)
        Lab_speed.pack(side = tk.LEFT)

        Ent_speed = ttk.Entry(Frm_speed, textvariable = self.speed, width = 8)
        Ent_speed.pack(side = tk.LEFT, padx = 10)
        ttk.Label(Frm_speed, text = "倍 (0.5 - 6400)").pack(side = tk.LEFT)

        Frm_fps = ttk.Frame(section_frame)
        Frm_fps.pack(fill = tk.X, pady = 5)

        Lab_fps = ttk.Label(Frm_fps, text = '帧率(fps)', width = 15, anchor = tk.W)
        Lab_fps.pack(side = tk.LEFT)

        self.Ent_fps = ttk.Entry(Frm_fps, textvariable = self.fps, width = 8)
        self.Ent_fps.pack(side = tk.LEFT, padx = 10)


    def printgpu(self):
        print(self.GPUOn)

    def create_code_options(self):
        section_frame = ttk.LabelFrame(
            self.scrollable_frame,
            text = "编码选项",
            padding = (15, 10)
        )
        section_frame.pack(fill = tk.X, pady = 5)

        Frm_codec = ttk.Frame(section_frame)
        Frm_codec.pack(fill = tk.X, pady = 5)

        Lab_codec = ttk.Label(Frm_codec, text = "视频编码:", width = 15, anchor = tk.W)
        Lab_codec.pack(side = tk.LEFT)

        Cmb_codec = ttk.Combobox(
            Frm_codec,
            textvariable = self.codec,
            width = 18,
            state = "readonly"
        )
        Cmb_codec['values'] = ("H.264", "H.265", "AV1")
        Cmb_codec.pack(side = tk.LEFT, padx = 10)

        Frm_graphic = ttk.LabelFrame(section_frame, text = "硬件加速:")
        Frm_graphic.pack(fill = tk.X, pady = 5)

        Ckb_GPUOn = ttk.Checkbutton(Frm_graphic, text = "使用GPU加速", variable = self.GPUOn, command = self.printgpu)
        Ckb_GPUOn.pack(side = tk.LEFT)

    def gene_cmd(self):
        if not self.selected_file:
            messagebox.showerror("错误", "请先选择一个视频文件！")
            return
        if not self.output_dir:
            messagebox.showerror("错误", "请先选择一个输出目录！")
            return
        resolution_mode = self.resolution_mode.get()
        scale_factor = self.scale_factor.get()
        width = self.custom_width.get()
        height = self.custom_height.get()
        quality = self.quality.get()
        speed = self.speed.get()
        codec = self.codec.get()
        basename = self.Ent_fileBaseName.get()
        fps = float(self.Ent_fps.get())

        if basename == "":
            basename = os.path.basename(self.selected_file)

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

        outfilepath = self.output_dir  # 这里的路径一定一定要以斜杠作为末尾
        outfilename = basename
        if not os.path.exists(outfilepath):
            os.mkdir(outfilepath)

        if self.GPUOn:
            encoder = (
                    (codec == 'H.264') * 'h264_qsv' +
                    (codec == 'H.265') * 'hevc_qsv' +
                    (codec == 'AV1') * 'av1_qsv'
            )
        else:
            encoder = (
                    (codec == 'H.264') * 'libx264' +
                    (codec == 'H.265') * 'libx265' +
                    (codec == 'AV1') * 'libsvtav1'
            )
        code = bnh.generate_command(
            srcfilepath = self.selected_file,
            outfilename = outfilename,
            outfilepath = outfilepath,
            width = width,
            height = height,
            fps = fps,
            speed = speed,
            qual = quality,
            encoder = encoder
        )
        return code

    def create_command_show(self):
        section_frame = ttk.LabelFrame(
            self.scrollable_frame,
            text = "命令预览",
            padding = (15, 10)
        )
        section_frame.pack(fill = tk.X, pady = 5)

        Frm_text = ttk.Frame(section_frame)
        Frm_text.pack(fill = tk.X, expand = True, side = tk.LEFT)

        self.Txt_cmdshow = tk.Text(
            Frm_text,
            height = 3,
            width = 50,
            wrap = tk.WORD,  # 自动换行
            state = 'disabled',
            font = ("consolas", 10),
        )
        self.Txt_cmdshow.pack(side = tk.LEFT, fill = tk.X, expand = True)

        Sbr_cmdshow = ttk.Scrollbar(Frm_text, orient = tk.VERTICAL, command = self.Txt_cmdshow.yview)
        Sbr_cmdshow.pack(side = tk.RIGHT, fill = tk.Y)
        self.Txt_cmdshow.config(yscrollcommand = Sbr_cmdshow.set)

        But_gene_cmd = ttk.Button(section_frame, text = "生成指令", command = self.update_cmdshow, width = 15)
        But_gene_cmd.pack(side = tk.RIGHT, padx = 10)

    def create_action_buttons(self):
        Frm_button = ttk.Frame(self.main_frame)
        Frm_button.pack(side=tk.RIGHT, anchor=tk.SE, pady = 20)

        But_export = ttk.Button(
            Frm_button,
            text = "导出视频",
            padding = 10,
            command = self.export_video
        )
        But_export.pack(side = tk.TOP, pady = (0,10))

        But_dev = ttk.Button(
            Frm_button,
            text = "By AllayCloud",
            padding = 10,
            command = self.show_developer_info
        )
        But_dev.pack(side = tk.TOP)

    def pack_scrollable_area(self):
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

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
            self.Ent_file.config(state = 'normal')
            self.Ent_file.delete(0, tk.END)
            self.Ent_file.insert(0, file_path)
            self.Ent_file.config(state = 'readonly')
            print("Selected file:", file_path)
            print(get_video_info_opencv(file_path))
            self.update_video_info()

    def browse_output_dir(self):
        self.output_dir = filedialog.askdirectory(
            title = "选择导出目录"
        )
        if self.output_dir:
            self.Ent_output_filepath.config(state = 'normal')
            self.Ent_output_filepath.delete(0, tk.END)
            self.Ent_output_filepath.insert(0, self.output_dir)
            self.Ent_output_filepath.config(state = 'readonly')
            print("Selected output directory:", self.output_dir)

    def update_video_info(self):
        video_info = get_video_info_opencv(self.selected_file)
        self.Ent_fps.delete(0, tk.END)
        self.Ent_fps.insert(0, video_info['fps'])
        video_info = f'''帧宽度：{video_info['width']}
帧高度：{video_info['height']}
画幅比例：{video_info['aspect_ratio']} ({int(video_info['aspect_ratio'].split(':')[0]) / int(video_info['aspect_ratio'].split(':')[1]):.2f}:1)
长度：{video_info['duration_formatted']}
视频大小：{video_info['file_size_formatted']}
帧速率：{video_info['fps']}
帧数量：{video_info['frame_count']}
'''
        self.Lab_video_info.config(text = video_info)

    def update_scale_label(self):  # 功能开发中
        # 获取当前缩放值并更新标签
        scale_value = self.scale_factor.get()
        # 如果 Lab_scale_value 存在则更新它
        if hasattr(self, 'Lab_scale_value'):
            self.Lab_scale_value.config(text = f"{scale_value:.1f}x")

    def update_quality_label(self, *args):
        self.Lab_quality_value.config(text = str(int(self.quality.get())))

    def update_cmdshow(self):
        '''更新cmd展示，这会在点击“生成代码”时被调用'''
        try:
            text = ' '.join(self.gene_cmd())
        except:
            return

        self.Txt_cmdshow.config(state = 'normal')  # 临时启用以修改文本
        self.Txt_cmdshow.delete(1.0, tk.END)  # 清空所有文本
        self.Txt_cmdshow.insert(tk.END, text)  # 插入新文本
        self.Txt_cmdshow.config(state = 'disabled')  # 恢复禁用状态

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
        fps = float(self.Ent_fps.get())

        errors = []
        if resolution_mode == "custom" and (width <= 0 or height <= 0):
            errors.append("分辨率宽高必须大于0")
        if speed < 0.5 or speed > 12800.0:
            errors.append("播放倍速必须在0.5到12800之间")
        if errors:
            messagebox.showerror("输入错误", "\n".join(errors))
            return

        # 显示确认对话框
        resolution_info = f"缩放倍数: {scale_factor:.1f}倍" if resolution_mode == "scale" else f"分辨率: {width}x{height}"
        confirmation = (f'''
确认导出设置:
视频文件: {self.selected_file}
导出目录：{self.output_dir}{(int(not (bool(len(self.output_dir)))) * '由于您没有选择导出目录，视频将会放置在程序运行根目录')}
{resolution_info}
画质: {int(quality)}（数字越高码率越低）
分辨率：{width}x{height}
帧率：{fps}
倍速: {speed:.1f}倍
编码: {codec}\n
是否开始导出视频?
提示：
若未启用GPU加速，FFmpeg对CPU算力要求较高，请确保CPU性能足够！
''')

        if int(quality) <= 10:
            confirmation += '\n您选择的画质过高，请确保硬盘预留足够的空间！'
        if int(width) * int(height) >= 1920 * 1080 * 16:
            confirmation += '\n您选择的分辨率过大，已超过8K规格，请确保硬盘预留足够的空间，并确保CPU与运存性能足够！'

        if messagebox.askyesno("确认导出", confirmation):
            messagebox.showinfo("导出开始", "视频导出过程已开始，请稍候...")
            print('start generating')
            cmd = self.gene_cmd()
            proc = subprocess.Popen(
                cmd,
                encoding = "utf-8",
                stdout = subprocess.PIPE,
                stderr = subprocess.STDOUT,
                text = True,
                bufsize = 1
            )
            for line in proc.stdout:
                print(line, end = '')
            proc.wait()
            dst = pathlib.Path(self.output_dir)
            print('done')
            messagebox.showinfo("导出完成",
                                f"视频导出完成！已放在目录{self.output_dir}下。感谢使用哪炸闹海！\n（去B站给悦灵一个关注好嘛？）")
            webbrowser.open('https://space.bilibili.com/660052393')

    def show_developer_info(self):
        info = (
            '''哪炸闹海 BitNowHigh
            AllayCloud 2025
            > By AllayCloud-Studio: AllayFocalors
            > Bilibili@悦灵AllayFocalors
            > GitHub仓库: https://github.com/AllayFocalors/BitNowHigh
            该项目基于 MIT License 开源
            悦灵云工作室保留所有权利
            '''
        )
        messagebox.showinfo("开发者信息", info)


if __name__ == "__main__":
    root = tk.Tk()
    app = VideoEditorUI(root)
    root.mainloop()