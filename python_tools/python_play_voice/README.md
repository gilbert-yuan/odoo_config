# odoo_config
 https://stackoverflow.com/questions/20021457/playing-mp3-song-on-python

 参考 上面的链接 实验一些python 播放音乐文件的程序





23
down vote
favorite
8
I want to play my song (mp3) from python, can you give me a simplest command to do that?

This is not correct:

import wave
w = wave.open("e:/LOCAL/Betrayer/Metalik Klinik1-Anak Sekolah.mp3","r")
python audio mp3
shareimprove this question
edited Nov 16 '13 at 17:34

Ashish Nitin Patil
4,66142447
asked Nov 16 '13 at 17:28

The Mr. Totardo
170118
1
Check out pygame, and read this question on raspberrypi.stackexchange. – Steinar Lima Nov 16 '13 at 17:36

You're right thanks! – The Mr. Totardo Mar 25 '15 at 18:26

Possible duplicate of Playing MP3 files with Python – user Jun 19 '16 at 22:32
add a comment
10 Answers
active oldest votes
up vote
25
down vote
accepted
You may try this, simplistic but not the best method maybe.

from pygame import mixer # Load the required library

mixer.init()
mixer.music.load('e:/LOCAL/Betrayer/Metalik Klinik1-Anak Sekolah.mp3')
mixer.music.play()
Please note that the support for MP3 is limited (as told in the docs)

For installation instructions, visit http://pygame.org/install.html

shareimprove this answer
edited Nov 17 '13 at 3:47
answered Nov 16 '13 at 17:38

Ashish Nitin Patil
4,66142447

how can I get pygame? I had this error: ImportError: No module named pygame – The Mr. Totardo Nov 16 '13 at 17:44

For installation instructions, visit pygame.org/install.html – Ashish Nitin Patil Nov 17 '13 at 3:48

Tester out pygame's mixer and it seems to a lot less intrusive than pyglet's media player. Probably because pyglet's player is also a video player, so if you don't need video it's a bit overkill! It's a shame pybass don't have python 3 support. That used to be the bomb. – Grimmy Mar 29 at 17:12
add a comment

up vote
42
down vote
Grab the VLC Python module, vlc.py, which provides full support for libVLC and pop that in site-packages. Then:

>>> import vlc
>>> p = vlc.MediaPlayer("file:///path/to/track.mp3")
>>> p.play()
And you can stop it with:

>>> p.stop()
That module offers plenty beyond that (like pretty much anything the VLC media player can do), but that's the simplest and most effective means of playing one MP3.

You could play with os.path a bit to get it to find the path to the MP3 for you, given the filename and possibly limiting the search directories.

Full documentation and pre-prepared modules are available here. Current versions are Python 3 compatible.

shareimprove this answer
answered Sep 17 '14 at 19:51

Ben
1,427620
3
This is likely the best answer as VLC has done 99% of the work. PyPi version is out dated but the VLC wiki is a good alternative src - wiki.videolan.org/Python_bindings – David Sep 16 '15 at 5:22
1
I think the PyPI version was compiled from an older version of VLC and there was definitely differences between 2.1.x and 2.2 which broke things. Compiling VLC from source with the vlc.py generation should always produce a working copy because vlc.py will always have the correct ctypes set for the compiled version of libvlc. – Ben Sep 25 '15 at 11:52

Scatch that, the version on PyPI is a completely unrelated thing. The result of someone writing their own wrapper and not checking for a naming conflict with the original project and similar to the python-gnupg vs. gnupg conflict (except in that case the second project deliberately set out to sabotage the first). No doubt there are others. I guess that's one thing java got right in order to guarantee different and unique names. – Ben Sep 25 '15 at 12:42
add a comment
up vote
6
down vote
You are trying to play a .mp3 as if it were a .wav.

You could try using pydub to convert it to .wav format, and then feed that into pyAudio.

Example:

from pydub import AudioSegment

song = AudioSegment.from_mp3("original.mp3")
song.export("final.wav", format="wav")
Alternatively, use pygame, as mentioned in the other answer.

shareimprove this answer
edited Mar 7 '14 at 17:15

Toni Almeida
5,77753351
answered Nov 16 '13 at 17:41

David
65654
add a comment
up vote
4
down vote
As it wasn't already suggested here, but is probably one of the easiest solutions:

import subprocess

def play_mp3(path):
    subprocess.Popen(['mpg123', '-q', path]).wait()
It depends on any mpg123 compliant player, which you get e.g. for Debian using:

apt-get install mpg123
or

apt-get install mpg321
shareimprove this answer
answered May 18 '15 at 15:48

Michael
2,9311843
add a comment
up vote
4
down vote
A simple solution:

import webbrowser
webbrowser.open("C:\Users\Public\Music\Sample Music\Kalimba.mp3")
cheers...

shareimprove this answer
answered Jul 6 '15 at 18:15

toufikovich
416414

Cute, but what if the only browser is lynx or even if the others are available on the system, the user only has command line access? It is a nice little quick & dirty workstation solution, though. – Ben Sep 25 '15 at 12:56

Thank you Michael, but how i can add "playlist" instead one file? – Amaroc Jul 24 '16 at 23:31
add a comment
up vote
2
down vote
See also playsound

pip install playsound

import playsound
playsound.playsound('/path/to/filename.mp3', True)
shareimprove this answer
answered Jan 22 at 2:20

Shuge Lee
18511

This library has a history of problems on Linux, unfortunately: github.com/TaylorSMarks/playsound/issues/1 – Gorkamorka Feb 18 at 14:37
add a comment
up vote
2
down vote
Another quick and simple option...

import os

os.system('start path/to/player/executable path/to/file.mp3')
Now you might need to make some slight changes to make it work. For example, if the player needs extra arguments or you don't need to specify the full path. But this is a simple way of doing it.

shareimprove this answer
answered Feb 28 at 16:49

The Unnamed Engineer
233
add a comment
up vote
2
down vote
If you're working in the Jupyter (formerly IPython) notebook, you can

import IPython.display as ipd
ipd.Audio(filename='path/to/file.mp3')
shareimprove this answer
edited Mar 23 at 22:42
answered Feb 22 at 16:54

mdeff
417
add a comment
up vote
1
down vote
from win32com.client import Dispatch

wmp=Dispatch('WMPlayer.OCX')

liste=[r"F:\Mp3\rep\6.Evinden Uzakta.mp3",
       r"F:\Mp3\rep\07___SAGOPA_KAJMER___BIR__I.MP3",
       r"F:\Mp3\rep\7.Terzi.mp3",
       r"F:\Mp3\rep\08. Rüya.mp3",
       r"F:\Mp3\rep\8.Battle Edebiyatı.mp3",
       r"F:\Mp3\rep\09_AUDIOTRACK_09.MP3",
       r"F:\Mp3\rep\02. Sagopa Kajmer - Uzun Yollara Devam.mp3",
       r"F:\Mp3\rep\2Pac_-_CHANGE.mp3",
       r"F:\Mp3\rep\03. Herkes.mp3",
       r"F:\Mp3\rep\06. Sagopa Kajmer - Istakoz.mp3"


for x in liste:
    mp3=wmp.newMedia(x)
    wmp.currentPlaylist.appendItem(mp3)


wmp.controls.play()
shareimprove this answer
answered May 4 '14 at 15:43

hsyn
111
add a comment
up vote
0
down vote
At this point, why not mentioning python-audio-tools:

GitHub: https://github.com/tuffy/python-audio-tools
docs: http://audiotools.sourceforge.net/programming/audiotools.html?highlight=seek#module-audiotools
It's the best solution I found.

(I needed to install libasound2-dev, on Raspbian)

Code excerpt loosely based on:
https://github.com/tuffy/python-audio-tools/blob/master/trackplay

#!/usr/bin/python

import os
import re
import audiotools.player


START = 0
INDEX = 0

PATH = '/path/to/your/mp3/folder'

class TracklistPlayer:
    def __init__(self,
                 tr_list,
                 audio_output=audiotools.player.open_output('ALSA'),
                 replay_gain=audiotools.player.RG_NO_REPLAYGAIN,
                 skip=False):

        if skip:
            return

        self.track_index = INDEX + START - 1
        if self.track_index < -1:
            print('--> [track index was negative]')
            self.track_index = self.track_index + len(tr_list)

        self.track_list = tr_list

        self.player = audiotools.player.Player(
                audio_output,
                replay_gain,
                self.play_track)

        self.play_track(True, False)

    def play_track(self, forward=True, not_1st_track=True):
        try:
            if forward:
                self.track_index += 1
            else:
                self.track_index -= 1

            current_track = self.track_list[self.track_index]
            audio_file = audiotools.open(current_track)
            self.player.open(audio_file)
            self.player.play()

            print('--> index:   ' + str(self.track_index))
            print('--> PLAYING: ' + audio_file.filename)

            if not_1st_track:
                pass  # here I needed to do something :)

            if forward:
                pass  # ... and also here

        except IndexError:
            print('\n--> playing finished\n')

    def toggle_play_pause(self):
        self.player.toggle_play_pause()

    def stop(self):
        self.player.stop()

    def close(self):
        self.player.stop()
        self.player.close()


def natural_key(el):
    """See http://www.codinghorror.com/blog/archives/001018.html"""
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', el)]


def natural_cmp(a, b):
    return cmp(natural_key(a), natural_key(b))


if __name__ == "__main__":

    print('--> path:    ' + PATH)

    # remove hidden files (i.e. ".thumb")
    raw_list = filter(lambda element: not element.startswith('.'), os.listdir(PATH))

    # mp3 and wav files only list
    file_list = filter(lambda element: element.endswith('.mp3') | element.endswith('.wav'), raw_list)

    # natural order sorting
    file_list.sort(key=natural_key, reverse=False)

    track_list = []
    for f in file_list:
        track_list.append(os.path.join(PATH, f))


    TracklistPlayer(track_list)