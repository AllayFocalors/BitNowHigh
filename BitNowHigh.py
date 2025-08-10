import subprocess, pathlib, sys, os
def generate(srcfilepath,outfilename='output',outfilepath='./',width=1920,height=1080,qual=30,encoder="libx264"):
    '''
    生成视频
    :param srcfilepath:str,源文件路径，可以相对可以绝对
    :param outfilename:str,输出文件基础名称（输出视频名会在基础名后加上表示规格的字符）
    :param outfilepath:str,末尾带斜杠的文件输出路径（不含文件名）
    :param width,height:int,宽高
    :param qual:int,画质crf值，默认为30，取值1~51，越低画质越高，体积越大
    :param encoder:str,编码器，默认为libx264。有两个选择：'libx264'与'libx265'，前者效率高体积大
    :return: dict,按照以下格式存储信息：{'code':'000','err':none,}，000表示顺利完成
    '''
    outfilepath=fr"{outfilepath}{outfilename}[{qual}-{width}x{height}].mp4"
    src = pathlib.Path(srcfilepath)
    dst = pathlib.Path(outfilepath)

    if not src.exists():
        sys.exit(f"找不到文件 {src}")
        return {'code':'001','err':f"找不到文件 {src}"}

    cmd = [
        "ffmpeg", "-y",
        "-i", str(src),
        "-vf", f"scale={width}:{height}",
        "-c:v", encoder, "-preset", "ultrafast", "-crf", f"{qual}",
        "-c:a", "copy",
        str(dst)
    ]

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

    return {
        'code':'000',
        'file':str(dst),
        'err':None,
    }

if __name__ == "__main__":
    generate(r"ab.mp4")