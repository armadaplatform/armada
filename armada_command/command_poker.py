import random
import sys
import wave

from PIL import Image

from armada_command.utils import image_to_ansi

CHUNK = 1024


def command_poker(args):
    so_sick = '/opt/armada/armada_command/utils/so_sick/{}.wav'.format(random.randint(1, 11))
    wf = wave.open(so_sick, 'rb')
    # p = pyaudio.PyAudio()
    #
    # stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
    #                 channels=wf.getnchannels(),
    #                 rate=wf.getframerate(),
    #                 output=True)
    #
    # data = wf.readframes(CHUNK)
    #
    # while data != '':
    #     stream.write(data)
    #     data = wf.readframes(CHUNK)
    #
    # stream.stop_stream()
    # stream.close()
    #
    # p.terminate()

    im = Image.open('/opt/armada/armada_command/utils/so_sick/poker.png')
    im = im.resize((90, 60))
    for y in range(im.size[1]):
        for x in range(im.size[0]):
            p = im.getpixel((x, y))
            h = "%2x%2x%2x" % (p[0], p[1], p[2])
            short, rgb = image_to_ansi.rgb2short(h)
            sys.stdout.write("\033[48;5;%sm " % short)
        sys.stdout.write("\033[0m\n")
    sys.stdout.write("\n")
