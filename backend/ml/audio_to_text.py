import sounddevice as sd
import wavio
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

def record_audio(filename='output.wav',duration=10,fs=44100):
    print('Recording started')

    # Start recoding using microphone
    recoding=sd.rec(
        int(duration*fs),
        samplerate=fs,      # Sampling rate.
        channels=1          # Mono recording (audio comes from only one channel).
        )
    sd.wait()               # Wait till recording gets complete.

    # Write recorded audio to WAV file.
    wavio.write(    
        filename,
        recoding,
        fs,
        sampwidth=2
        )

    print('Recording Finished')
    return filename


def transcribe_audio_file(filename="output.wav"):
    try:
        with open(filename, "rb") as f:
            transcription = client.audio.transcriptions.create(
                file=("audio.wav", f, "audio/wav"),
                model="whisper-large-v3",   # Groq Fast Whisper - Model name
            )

        return transcription.text

    except Exception as e:
        print("Transcription Error:", e)
        return "Error in transcription."


if __name__ == "__main__":
    file = record_audio(duration=30)   # record 5 seconds
    text = transcribe_audio_file(file)
    print("Transcribed Text:", text)