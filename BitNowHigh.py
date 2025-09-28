# 视频生成与导出模块
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
import subprocess, pathlib, sys, os

VERSION = '0.0.2'

def generate_command(srcfilepath,outfilename='output',outfilepath='./',width=1920,height=1080,fps=60,qual=30,speed=1.0,encoder="libx264"):
    '''
    生成视频
    :param srcfilepath:str,源文件路径，可以相对可以绝对
    :param outfilename:str,输出文件基础名称（输出视频名会在基础名后加上表示规格的字符）
    :param outfilepath:str,末尾带斜杠的文件输出路径（不含文件名）
    :param width,height:int,宽高
    :param fps:float,帧率,为None则使用原视频帧率
    :param qual:int,画质crf值，默认为30，取值1~51，越低画质越高，体积越大
    :param speed:float,播放倍速，默认为1
    :param encoder:str,编码器，默认为libx264。有两个选择：'libx264'与'libx265'，前者效率高体积大
    :return: command:list,代码列表。要得到一行代码需要' '.join(list)
    '''

    if outfilepath[-1] != '/':
        outfilepath += '/'
    outfilepath=fr"{outfilepath}{outfilename}[{qual}-{width}x{height}].mp4"
    src = pathlib.Path(srcfilepath)
    dst = pathlib.Path(outfilepath)

    if not src.exists():
        sys.exit(f"找不到文件 {src}")
        return {'code':'001','err':f"找不到文件 {src}"}


    video_filters = [f"scale={width}:{height}"]
    audio_filters = []

    if speed != 1.0:
        video_filters.append(f"setpts=PTS/{speed}")

        if speed != 1.0:
            video_filters.append(f"setpts=PTS/{speed}")

            if speed >= 0.5 and speed <= 2.0:
                audio_filters.append(f"atempo={speed}")
            elif speed > 2.0:
                temp_speed = speed
                while temp_speed > 2.0:
                    audio_filters.append("atempo=2.0")
                    temp_speed /= 2.0
                if temp_speed > 0.5:
                    audio_filters.append(f"atempo={temp_speed}")
            elif speed < 0.5:
                temp_speed = speed
                while temp_speed < 0.5:
                    audio_filters.append("atempo=0.5")
                    temp_speed /= 0.5
                if temp_speed < 2.0 and temp_speed >= 0.5:
                    audio_filters.append(f"atempo={temp_speed}")

    cmd = [
        "ffmpeg", "-y",
        "-i", str(src),
        "-c:v", encoder,
        "-preset", "7",
        "-crf", f"{qual}",
        "-c:a", "aac",
        '-r',f'{fps}',
    ]

    if video_filters:
        cmd.extend(['-vf',','.join(video_filters)])

    if audio_filters:
        cmd.extend(['-af',','.join(audio_filters)])

    cmd.extend([str(dst)])

    return cmd


def generate_video_by_list(opts):
    '''
    通过传入

    '''

def generate_video(srcfilepath,outfilename='output',outfilepath='./',width=1920,height=1080,fps=60,qual=30,speed=1,encoder="libx264"):
    '''
    通过参数生成视频
    :param srcfilepath:str,源文件路径，可以相对可以绝对
    :param outfilename:str,输出文件基础名称（输出视频名会在基础名后加上表示规格的字符）
    :param outfilepath:str,末尾带斜杠的文件输出路径（不含文件名）
    :param width,height:int,宽高
    :param fps:float,帧率,为None则使用原视频帧率
    :param qual:int,画质crf值，默认为30，取值1~51，越低画质越高，体积越大
    :param speed:float,播放倍速，默认为1
    :param encoder:str,编码器，默认为libx264。有两个选择：'libx264'与'libx265'，前者效率高体积大
    :return: dict,按照以下格式存储信息：{'code':'000','err':none,}，000表示顺利完成
    '''
    dst = pathlib.Path(outfilepath)
    cmd=generate_command(srcfilepath,outfilename,outfilepath,width,height,fps,qual,speed,encoder)
    proc = subprocess.Popen(
        cmd,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    for line in proc.stdout:
        print(line, end='')
    proc.wait()
    print(str(dst))
    return {
        'code':'000',
        'file':str(dst),
        'err':None,
    }

if __name__ == "__main__":
    print(generate_command(r"video.mp4"))