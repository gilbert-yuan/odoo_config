# coding=utf-8
import wave
import subprocess
# wave 这个模块直接播放mp3 文件会报错
# wave.Error: file does not start with RIFF id

#建议先转换mp3文件
# 还要 安装  ffmpeg(安装这个还是比较耗费资源(16兆..))
#安装方式很是复杂..  https://trac.ffmpeg.org/wiki/CompilationGuide/Ubuntu

# subprocess.call(['ffmpeg', '-i', 'auido.mp3', 'auido.wav'])
#查找资料据说可以 转换成功 但是我本机没有安装成功 ffmpeg 所以测试(没有具体的测试)
#https://stackoverflow.com/questions/25672289/failed-to-open-file-file-wav-as-a-wav-due-to-file-does-not-start-with-riff-id
#w = wave.open("./auido.mp3", "r")
#
from pydub import AudioSegment
song = AudioSegment.from_mp3("/home/yuan/mydocker/odoo_config/python_tools/python_play_voice/auido.mp3")
song.export("final.wav", format="wav")

#w = wave.open("final.wave", "r")


