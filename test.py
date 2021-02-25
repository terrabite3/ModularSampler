import mido
from time import sleep
from CvDriver import CvDriver
from MidiHandler import MidiHandler
from Audio import *
import sys
from os import path
import glob


class Main:
    def __init__(self, mode, sample_list = None):
        self.cv = CvDriver()
        self.midi = MidiHandler(self._note_on_callback, self._note_off_callback, self._message_callback)
        self.audio = Audio(0, 2, 2, 48000)
        self.library = SampleLibrary(sample_list)
        self._mode = mode
        self._recording_note = None
        self.verbose = False

    def set_mode(self, mode):
        self._log('Switching mode to ' + mode)
        # TODO: Handle mode transitions well
        self._mode = mode

        self.midi.notify_mode(self._mode)

    def _note_on_callback(self, note):
        if self._mode == 'midi_cv':
            self.cv.note_on(note)
            self._log('playing note ' + str(note))

        elif self._mode == 'record':
            if self._recording_note is None:
                self._recording_note = note
                self.cv.note_on(note)
                self.audio.recorder.start_recording()
                self._log('recording note ' + str(note))
            else:
                self._log('ignoring note on ' + str(note))

        elif self._mode == 'play':
            sample = self.library.get_sample(note)
            if sample:
                self.audio.mixer.play_sample(sample)
                self._log('playing note ' + str(note))
            else:
                self._log('ignoring note ' + str(note) + ' - no sample')

    def _note_off_callback(self, note):
        if self._mode == 'midi_cv':
            self.cv.note_off()
            self._log('stopping note ' + str(note))

        elif self._mode == 'record':
            if note == self._recording_note:
                self._recording_note = None
                self.cv.note_off()
                file_name = str(note) + '.wav'
                record_sample = self.audio.recorder.save_recording(file_name)
                self.library.add_sample(note, file_name)
                self._log('saving note ' + str(note) + ' to ' + file_name)
            else:
                self._log('ignoring note off ' + str(note))

        elif self._mode == 'play':
            sample = self.library.get_sample(note)
            if sample:
                self.audio.mixer.stop_sample(sample)
                self._log('stopping note ' + str(note))
            else:
                self._log('ignoring note off ' + str(note) + ' - no sample')

    def _message_callback(self, message):
        if message == self._mode:
            return
        self.set_mode(message)
            

    def _log(self, message):
        if self.verbose:
            print(self._mode + ': ' + message)

mode = 'midi_cv'
if len(sys.argv) >= 2:
    mode = sys.argv[1]

sample_list = {}
for f in glob.glob('*.wav'):
    name, ext = path.splitext(f)
    try:
        note = int(name)
        sample_list[note] = f
    except ValueError:
        continue


main = Main(mode, sample_list)
main.verbose = True
main.set_mode(mode)


while True:
    new_mode = input('Enter a new mode: m(idi_cv) p(lay) r(ecord) e(x)it: ')
    if len(new_mode) == 0:
        continue
    if new_mode[0] == 'm':
        main.set_mode('midi_cv')
    if new_mode[0] == 'p':
        main.set_mode('play')
    if new_mode[0] == 'r':
        main.set_mode('record')
    if new_mode[0] == 'x':
        print('Exiting')
        break