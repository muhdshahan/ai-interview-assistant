
import sounddevice as sd
import wavio
import speech_recognition as sr


def record_audio_file(filename='output.wav',duration=10,fs=44100):
    print('Recording started')

    recoding=sd.rec(int(duration*fs),samplerate=fs,channels=1)
    sd.wait()
    wavio.write(filename,recoding,fs,sampwidth=2)
    print('Recording Finished')
    return filename


def transcribe_audio_file(filename="output.wav"):
    recognizer = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return "Sorry, could not understand."
    except sr.RequestError:
        return "API Error: Check your connection."


# | Library              | What it Does                               | Why It's Used                          |
# | -------------------- | ------------------------------------------ | -------------------------------------- |
# | sounddevice          | Lets Python record audio from your mic     | Used to **record voice**               |
# | wavio                | Saves the audio as a `.wav` file           | Converts recording into a file format  |
# | speech_recognitio`   | Google's API for converting speech to text | Used to **transcribe audio into text** |
