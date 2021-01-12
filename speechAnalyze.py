import os, re, time
import datetime

from osAPI import OSes
from pydub import AudioSegment
from pydub.silence import split_on_silence
from helperClasses import checkInternetConnection, SpeakText, Weather, calculateEquation
from speech_recognition import AudioFile, Microphone, RequestError, Recognizer, UnknownValueError


def answerUserQuestions(question):
    if "how are you" in question:
        SpeakText("Everything's good, how are you ?")
    elif "time" in question:
        currentTime = datetime.datetime.now().strftime('%H:%M:%S')
        SpeakText(f"The current time is: {currentTime}")
    elif "weather" in question:
        SpeakText(Weather().get_weather_data())
    elif "system" in question:
        osInterface = OSes()
        SpeakText(osInterface.actions('system usage'))
    elif "calculate" in question:
        calculateEquation(question)


class SpeechAnalyzer:
    def __init__(self):
        self.audioRecognizer = Recognizer()
        self.audioRecognizer.dynamic_energy_threshold = True
        self.actions = ["open", "search", "define", "launch", "play"]
        self.questions = ["how are you", "whats the time", "whats the weather",
                          "system usage", "show system info"]

    # TODO: make the regex only remove the unwanted words if they are a all word not inside it
    @staticmethod
    def checkInput(userInput):
        unwantedText = r"\b(i|we|they|to|hi|show|display|please|for|on)\b"

        # Check if the command is in the format -> Jarvis-actionToDo-OnWhatToDo
        if "jarvis" not in userInput:
            return "You need to start the command with Jarvis", -1

        filteredText = userInput.replace("run", "launch")
        filteredText = " ".join(filteredText.split()[1::])
        filteredText = re.sub(unwantedText, "", filteredText)
        return filteredText.strip().lower()

    def executeCommand(self, userCommand):
        if userCommand.lower() in self.questions:
            answerUserQuestions(userCommand)
        elif "calculate" in userCommand:
            calculateEquation(userCommand.replace("calculate", ""))
        elif userCommand.split()[0] in self.actions:
            print(f"executing user command: {userCommand}")
            SpeakText(f"executing user command: {userCommand}")
            OSes().actions(userCommand)

    def parseUserInput(self, voiceInput=""):
        if len(checkResult := self.checkInput(voiceInput)) != 2:
            self.executeCommand(checkResult)
        else:
            print(checkResult[0])
            SpeakText(checkResult[0])
            return -1

    def analyzeFileForOffline(self, FilePath):
        with AudioFile(FilePath) as source:
            # listen for the the mic, translate it to text and pass it to parsing
            audio_data = self.audioRecognizer.record(source)
            text = self.audioRecognizer.recognize_google(audio_data)
            self.parseUserInput(text)

    def getMicInput(self):
        with Microphone() as audioSource:

            # wait for a few moments to let the recognizer adjust to the surrounding noise
            self.audioRecognizer.adjust_for_ambient_noise(audioSource, duration=2.5)
            # listens for the user's input
            voiceCMD = self.audioRecognizer.listen(audioSource, phrase_time_limit=5)

            # Using google to recognize audio
            if checkInternetConnection():
                textCMD = self.audioRecognizer.recognize_google(voiceCMD)
            else:
                textCMD = self.audioRecognizer.recognize_sphinx(voiceCMD)

            return textCMD.lower()

    def liveUserSession(self):
        userCMD, exitWords = False, ["quit", "stop", "bye", "break", "see ya", "next time"]

        try:

            while userCMD not in exitWords:
                # use the microphone as source for input.
                SpeakText("Hello Sir, Jarvis at your service.")
                userCMD = "jarvis open test.txt"  # self.getMicInput()
                SpeakText(f"Did You Say {userCMD} ?")
                confirmCMD = "yes"  # self.getMicInput()

                if "yes" in confirmCMD:
                    self.parseUserInput(userCMD)
                time.sleep(5)

        except RequestError as e:
            SpeakText("Sorry an error has accrued.")
            print("Could not request results; {0}".format(e))
        except UnknownValueError as e:
            SpeakText("error look at console for more")
            print(f"unknown error accord {str(e)}")

    @staticmethod
    def get_large_audio_transcription(self, path):
        """
            Splitting the large audio file into chunks
            and apply speech recognition on each of these chunks
        """
        # open the audio file using pydub
        sound = AudioSegment.from_wav(path)
        # split audio sound where silence is 700 miliseconds or more and get chunks
        chunks = split_on_silence(sound,
                                  # experiment with this value for your target audio file
                                  min_silence_len=500,
                                  # adjust this per requirement
                                  silence_thresh=sound.dBFS - 14,
                                  # keep the silence for 1 second, adjustable as well
                                  keep_silence=500,
                                  )

        folder_name = "audio-chunks"

        # create a directory to store the audio chunks
        if not os.path.isdir(folder_name):
            os.mkdir(folder_name)
        whole_text = ""

        # process each chunk
        for i, audio_chunk in enumerate(chunks, start=1):
            # export audio chunk and save it in
            # the `folder_name` directory.
            chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
            audio_chunk.export(chunk_filename, format="wav")
            # recognize the chunk
            with AudioFile(chunk_filename) as source:
                audio_listened = self.audioRecognizer.record(source)
                # try converting it to text
                try:
                    text = self.audioRecognizer.recognize_google(audio_listened)
                except UnknownValueError as e:
                    print("Error:", str(e))
                else:
                    text = f"{text.capitalize()}. "
                    print(chunk_filename, ":", text)
                    whole_text += text

        # return the text for all chunks detected
        return whole_text
