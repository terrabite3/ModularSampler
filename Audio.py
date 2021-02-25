import pyaudio
import wave
import sys
import numpy as np


class Sample:
    def __init__(self, wav_file):
        self.file_name = wav_file
        # Load wav file
        wav = wave.open(wav_file, 'rb')
        self._sample = wav.readframes(wav.getnframes())
        self._frame_size = wav.getnchannels() * wav.getsampwidth()
        self._pointer = 0

    def get_frames(self, num_frames):
        frames_left_in_sample = len(self._sample) // self._frame_size - self._pointer // self._frame_size
        frames_to_get_from_sample = min(num_frames, frames_left_in_sample)
        frames_to_pad = num_frames - frames_to_get_from_sample
        result = self._sample[self._pointer : self._pointer + frames_to_get_from_sample * self._frame_size] + bytes(frames_to_pad * self._frame_size)
        self._pointer += frames_to_get_from_sample * self._frame_size
        return result

    def reset(self):
        self._pointer = 0


class SampleLibrary:
    def __init__(self, sample_list = None):
        self._library = {}
        if sample_list:
            for note, file_name in sample_list.items():
                self.add_sample(note, file_name)

    def get_sample(self, note):
        if note in self._library:
            return self._library[note]
        return None

    def add_sample(self, note, file_name):
        self._library[note] = Sample(file_name)


class Mixer:
    def __init__(self, num_channels, sample_width):
        self._num_channels = num_channels
        self._sample_width = sample_width
        self._active_samples = []

    def play_sample(self, sample):
        if sample in self._active_samples:
            # TODO: It could make sense to reset the sample instead
            return
        sample.reset()
        self._active_samples.append(sample)

    def stop_sample(self, sample):
        if sample in self._active_samples:
            self._active_samples.remove(sample)

    def get_frames(self, num_frames):
        # result_ints = [0] * num_frames * self._num_channels
        # result = bytes(num_frames * self._num_channels * self._sample_width)
        # Use 32-bit here so we don't overflow
        result_np = np.zeros(num_frames * self._num_channels, dtype=np.int32)

        if self._sample_width == 1:
            dt = np.int8
        elif self._sample_width == 2:
            dt = np.int16
        elif self._sample_width == 3:
            raise Exception('Still need to implement 24-bit audio')
        elif self._sample_width == 4:
            dt = np.int32
        else:
            raise Exception('Invalid sample width ' + str(self._sample_width))

        for sample in self._active_samples:
            frames = sample.get_frames(num_frames)
            # convert to list of ints
            sample_np = np.frombuffer(frames, dtype=dt)
            result_np += sample_np

        # Create an output array of the correct datatype
        result = np.zeros(num_frames * self._num_channels, dtype=dt)
        np.clip(result_np, np.iinfo(dt).min, np.iinfo(dt).max, result)
        return result.tobytes()


class Recorder:
    def __init__(self, num_channels, sample_width, sample_rate):
        self._num_channels = num_channels
        self._sample_width = sample_width
        self._sample_rate = sample_rate
        self._frames = None

    def is_recording(self):
        return self._frames is not None

    def start_recording(self):
        if self.is_recording():
            raise Exception('Already recording')
        self._frames = b''

    def save_recording(self, wav_file):
        if not self.is_recording():
            raise Exception('Nothing has been recorded')
        
        wf = wave.open(wav_file, 'wb')
        wf.setnchannels(self._num_channels)
        wf.setsampwidth(self._sample_width)
        wf.setframerate(self._sample_rate)
        wf.writeframes(self._frames)
        wf.close()

        self._frames = None

    def append_frames(self, frames):
        if self.is_recording():
            self._frames += frames


class Audio:
    def __init__(self, device_index, num_channels, sample_width, sample_rate):
        self._py_audio = pyaudio.PyAudio()
        self._stream = self._py_audio.open(
            format = self._py_audio.get_format_from_width(sample_width),
            channels = num_channels,
            rate = sample_rate,
            input = True,
            output = True,
            input_device_index = device_index,
            output_device_index = device_index,
            stream_callback = self._callback
        )

        self.mixer = Mixer(num_channels, sample_width)
        self.recorder = Recorder(num_channels, sample_width, sample_rate)

        self._stream.start_stream()

    def __del__(self):
        self._stream.stop_stream()
        self._stream.close()
        self._py_audio.terminate()

    def _callback(self, in_data, frame_count, time_info, status):
        self.recorder.append_frames(in_data)
        out_data = self.mixer.get_frames(frame_count)
        return (out_data, pyaudio.paContinue)

    