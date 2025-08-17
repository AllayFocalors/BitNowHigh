# BitNowHigh
哪炸闹海(BitNowHigh)是一个基于Python的视频编辑工具。用户可以自由更改视频分辨率、画质以调节视频体积。

## 如何使用？
注意，公布的源代码不包含ffmpeg的依赖，请自行下载最新版本的ffmpeg，并将exe与dll文件放在py文件同级目录下。<br>
BtbN的ffmpeg下载链接：https://github.com/BtbN/FFmpeg-Builds/releases<br>
请注意选择支持qsv加速的ffmpeg版本。
<br>
ui文件是ui.py,视频生成文件是BitNowHigh.py,各位可以自行将其加入到其他项目的库，便于调用。

## 简单错误解决
### 1. 点击“导出视频”后没有任何输出
> 检查依赖文件，ffmpeg.exe以及相关dll文件是否放置在根目录下

### 2. 报错信息`unknown encoder 'xxx_qsv'`
> 当前设备不支持基于qsv的硬件加速，关闭“GPU加速”即可
 
### 3. 运行时报错`ModuleNotFoundError: No module named 'xxx'`
> 缺少必要的模块，终端运行`pip install xxx`即可
 


## 联系悦灵
对于程序的任何反馈or相关信息咨询可联系： <br>
AllayFocalors[at]163.com