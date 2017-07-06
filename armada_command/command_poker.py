import random
import sys
import wave

CHUNK = 1024


def command_poker(args):
    try:
        import pyaudio

        so_sick = '/opt/armada/armada_command/utils/so_sick/{}.wav'.format(random.randint(1, 11))
        wf = wave.open(so_sick, 'rb')
        p = pyaudio.PyAudio()

        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)

        data = wf.readframes(CHUNK)
        while data != '':
            stream.write(data)
            data = wf.readframes(CHUNK)
        stream.stop_stream()
        stream.close()

        p.terminate()
    except ImportError:
        print("So sick!")
        print("  Want more sickness? Try getting python-pyaudio.")
    except Exception:
        pass

    with open('/opt/armada/armada_command/utils/so_sick/poker', 'rb') as im:
        for line in im:
            sys.stdout.write(line)
