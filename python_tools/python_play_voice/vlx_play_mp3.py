# coding=utf-8
# import vlc
# # https://wiki.videolan.org/Python_bindings
# #英文太差没看懂 怎么安装这个VLC 的...
# p = vlc.MediaPlayer("file:///path/to/track.mp3")
# p.play()
#
# p.stop()


import os
#   居然说没有权限不知道什么鬼 ..
# sh: 1: /home/yuan/mydocker/odoo_config/python_tools/python_play_voice/auido.mp3: Permission denied
os.system('/home/yuan/mydocker/odoo_config/python_tools/python_play_voice/auido.mp3')