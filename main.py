import ast
import logging
import os
import random
import sys
import time
import wave
from pathlib import Path

import pyaudio
from dotenv import load_dotenv

from silent_pyaudio import pyaudio as silent_pyaudio


def do_record(filename: str, record_time: int):
    chunk = 1024  # Record in chunks of 1024 samples
    sample_format = pyaudio.paInt16  # 16 bits per sample
    channels = 2
    fs = 44100  # Record at 44100 samples per second

    print("Recording")

    with silent_pyaudio() as p:
        p = pyaudio.PyAudio()  # Create an interface to PortAudio

        stream = p.open(
            format=sample_format,
            channels=channels,
            rate=fs,
            frames_per_buffer=chunk,
            input=True,
        )

        frames = []  # Initialize array to store frames

        # Store data in chunks for 3 seconds
        for i in range(0, int(fs / chunk * record_time)):
            data = stream.read(chunk)
            frames.append(data)

        # Stop and close the stream
        stream.stop_stream()
        stream.close()
        # Terminate the PortAudio interface
        p.terminate()

        # Save the recorded data as a WAV file
        wf = wave.open(filename, "wb")
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(sample_format))
        wf.setframerate(fs)
        wf.writeframes(b"".join(frames))
        wf.close()
    print("Recording succesful\n\n")
    time.sleep(1)


def manage_record(record_time: int, sound_multiplicity: int, sounds: list):
    # Record words in varying order to get more natural pronounciations
    for t in range(sound_multiplicity):
        shuffled_sounds = random.sample(sounds, len(sounds))
        for s in shuffled_sounds:
            print(f"Say: {s}")
            time.sleep(1)
            do_record(filename=f"audio_output/{s}/{s}_{t}.wav", record_time=record_time)


if __name__ == "__main__":
    # Load configuration from .env file
    load_dotenv()
    try:
        sounds = ast.literal_eval(os.getenv("SOUNDS"))
        record_time = ast.literal_eval(os.getenv("RECORD_TIME"))
        sound_multiplicity = ast.literal_eval(os.getenv("SOUND_MULTIPLICITY"))
    except ValueError as e:
        print(f"Configuration in .env file incorrect - {e}")
        sys.exit(1)

    # Create directory structure for saving files
    for sound in sounds:
        Path(f"audio_output/{sound}").mkdir(parents=True, exist_ok=True)

    print("Say the word in the terminal AFTER the 'Recording' line appears")
    input("Press any key to continue\n\n")

    manage_record(
        record_time=record_time, sound_multiplicity=sound_multiplicity, sounds=sounds
    )
