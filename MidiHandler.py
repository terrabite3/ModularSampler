import mido

class MidiHandler:
    def __init__(self, note_on_callback, note_off_callback, message_callback = None):
        self._note_on_cb = note_on_callback
        self._note_off_cb = note_off_callback
        self._message_cb = message_callback
        self._apc = False

        avail_ports = mido.get_input_names()
        port_name = ''
        for p in avail_ports:
            if 'APC' in p:
                port_name = p
                self._apc = True
                break
            if 'Keystation' in p:
                port_name = p
                break

        self._in_port = mido.open_input(port_name, callback=self._callback)
        self._out_port = mido.open_output(port_name)


    def _callback(self, msg):
        if self._apc and self._message_cb and msg.channel == 0:
            # self._out_port.send(mido.Message('note_on', note=msg.note, velocity=1))
            
            # There's a button labeled REC, but for some reason they didn't put an LED under it!
            if msg.type == 'note_on':
                if msg.note == 68:
                    self._message_cb('midi_cv')
                    return
                if msg.note == 69:
                    self._message_cb('play')
                    return
                if msg.note == 70:
                    self._message_cb('record')
                    return

        if msg.type == 'note_on':
            self._note_on_cb(msg.note)
        elif msg.type == 'note_off':
            self._note_off_cb(msg.note)

    def notify_mode(self, mode):
        # 0 is off
        # 1 is green
        # 3 is red
        # 5 is yellow
        # 2, 4, 6 blink
        # Not all buttons have LEDs, not all buttons with LEDs have both colors
        if self._apc:
            self._out_port.send(mido.Message('note_on', note=68, velocity=0))
            self._out_port.send(mido.Message('note_on', note=69, velocity=0))
            self._out_port.send(mido.Message('note_on', note=70, velocity=0))
            if mode == 'midi_cv':
                self._out_port.send(mido.Message('note_on', note=68, velocity=3))
            elif mode == 'play':
                self._out_port.send(mido.Message('note_on', note=69, velocity=3))
            elif mode == 'record':
                self._out_port.send(mido.Message('note_on', note=70, velocity=3))
