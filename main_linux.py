import sys

if sys.platform == 'win32':
    from Default import AudioVisualiser
else:
    from Default import AudioVisualiserLinux as AudioVisualiser

if __name__ == '__main__':
    AudioVisualiser.AudioVisualiser()
