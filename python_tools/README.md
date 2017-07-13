# odoo_config

just some small python program(or demo)
方面的使用或者数据处理之类的



一键转换 文件的编码方式
iconv -t utf-8 -f gb18030 -c all.csv > county.csv
命令    目标编码  原来编码    原文件    转码后的文件


 # 在shell 脚本中执行的代码 subprocess.call
 #构造一个shell 的环境 把里面的命令 在shell 里面执行
subprocess.call(['ffmpeg', '-i', 'auido.mp3', 'auido.wav'])