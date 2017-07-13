# coding=utf-8

# 经过鉴定这个是可以用的
#只是要安装 两个包 一个是系统 包mpg123 一个是subprocess
import subprocess
subprocess.Popen(['mpg123', '-q', 'auido.mp3']).wait()