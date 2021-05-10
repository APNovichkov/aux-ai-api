from midi2audio import FluidSynth


if __name__ == '__main__':
    print("Converting")

    fs = FluidSynth()
    fs.midi_to_audio('../sample_music/sample.mid', '/sample_music/output_sample.wav')