#!/usr/bin/python3

# Copyright: University of Queensland, 2018
# Contributors: Ben Foley

# Writes a Kaldi segment file for long audio, based on detected silence
# Usage:
# python3 segment.py -i 6_1_1.wav -s b5d36158-d00d-47b3-9d3f-2590e6e75c28

from pydub import AudioSegment
import pydub.silence
import uuid
import subprocess
import argparse

parser = argparse.ArgumentParser(description='.', formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("-i", "--input_filename", dest="input_filename", help="Input filename", default="6_1_1.wav")
parser.add_argument("-s", "--speaker_id", dest="speaker_id", help="Test speaker id", default="TESTSPEAKERID")
args = parser.parse_args()
input_filename = args.input_filename
speaker_id = args.speaker_id

min_silence_len = 10
silence_thresh = -20

f_recordings = open("infer/wav.scp", "w", encoding="utf-8")
f_segments = open("infer/segments", "w", encoding="utf-8")
f_utt2spk = open("infer/utt2spk", "w", encoding="utf-8")

l_recordings, l_segments, l_utt2spk = [], [], []

print("hold tight, this may take a while...")

# generate recording id
# use this in segments, and to generate wav.scp
recording_id = str(uuid.uuid4())
l_recordings.append("%s data/%s\n" % (recording_id, "infer/" + input_filename))

# get start/end times of segments by silence thresholds ADJUST THESE
audio_file = AudioSegment.from_wav("infer/" + input_filename)
audio_chunks = pydub.silence.detect_silence(audio_file, min_silence_len=min_silence_len, silence_thresh=silence_thresh)

print("segmenting on these discovered chunks:")
print(audio_chunks)

for chunk in audio_chunks:

    # generate utterance_id - also use this to generate utt2spk
    utterance_id = str(uuid.uuid4())

    # write out line to segments
    l_segments.append("%s %s %f %f\n" % (utterance_id, recording_id, chunk[0] / 1000.0, chunk[1] / 1000.0))

    # write utt2spk
    l_utt2spk.append("%s %s\n" % (utterance_id, speaker_id))


l_recordings.sort()
f_recordings.write("".join(l_recordings))
f_recordings.close()

l_segments.sort()
f_segments.write("".join(l_segments))
f_segments.close()

l_utt2spk.sort()
f_utt2spk.write("".join(l_utt2spk))
f_utt2spk.close()


subprocess.call("perl utt2spk_to_spk2utt.pl infer/utt2spk > infer/spk2utt", shell=True)

print("Done")
