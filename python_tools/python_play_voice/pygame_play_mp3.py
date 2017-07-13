# coding=utf-8
from pygame import mixer # Load the required library


#执行程序没有反应 ..
mixer.init()
mixer.music.load('/home/yuan/mydocker/odoo_config/python_tools/python_play_voice/auido.mp3')
mixer.music.play()