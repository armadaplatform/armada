import random
import sys
import wave
import pyaudio

from PIL import Image

from armada_command.utils import image_to_ansi

CHUNK = 1024


def command_poker(args):
    im = Image.open('/opt/armada/armada_command/utils/so_sick/poker.png')
    im = im.resize((120, 80))
    so_sick = '/opt/armada/armada_command/utils/so_sick/{}.wav'.format(random.randint(1, 11))
    wf = wave.open(so_sick, 'rb')
    p = pyaudio.PyAudio()

    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    data = wf.readframes(CHUNK)
    y = 0
    while data != '':
        if y < im.size[1]:
            draw_row(im, y)
            y += 1
        stream.write(data)
        data = wf.readframes(CHUNK)
    while y < im.size[1]:
        draw_row(im, y)
        y += 1
    sys.stdout.write("\n")
    stream.stop_stream()
    stream.close()

    p.terminate()


def draw_row(im, y):
    for x in range(im.size[0]):
        pixel = im.getpixel((x, y))
        h = "%2x%2x%2x" % (pixel[0], pixel[1], pixel[2])
        short, rgb = image_to_ansi.rgb2short(h)
        sys.stdout.write("\033[48;5;%sm " % short)
    sys.stdout.write("\033[0m\n")
