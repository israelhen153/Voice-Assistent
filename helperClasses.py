import os
import psutil
import pyttsx3
import requests
import platform
import configparser
import wolframalpha
import multiprocessing as mp

from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
from multiprocessing import cpu_count
from concurrent.futures.thread import ThreadPoolExecutor


def get_file_location(filename, user_home_dir):
    # if we need find it first
    root_fs = dict.fromkeys(["linux", "darwin"], user_home_dir)
    base_dir = root_fs.get(platform.system().lower()).replace(" ", "")

    return ParallelFileSearch(base_dir).locateFileInSystem(filename)


def calculateTemperature():
    sum_avg, hw_pkg_ids = 0, {}

    for core in psutil.sensors_temperatures()['coretemp']:
        if "Package" in core.label and core.label not in hw_pkg_ids.keys():
            hw_pkg_ids[core.label] = core.current

    for pkg in hw_pkg_ids.values():
        sum_avg = sum_avg + pkg

    return f"pc heat {sum_avg / len(hw_pkg_ids)}"


def get_sys_data():
    cpuUsage = psutil.cpu_percent(1)
    ramUsage, temperature = psutil.virtual_memory().percent, calculateTemperature()

    return f"CPU usage: {cpuUsage}%\n memory Usage: {ramUsage}%\n{temperature} degrees"


def calculateEquation(userQuestion):
    try:
        SpeakText(WolframSolver().solve(userQuestion))
    except Exception as e:
        SpeakText("Internal Error!! maybe No internet connection ? Please try again later")
        print(str(e))


class SpeechEngine:
    def __init__(self):
        self.speechSpeed = 75
        self.addedOptions = False

    def __fineTune(self):
        pass

    def createTTSEngine(self):
        # Initialize the engine and speak
        speechEngine = pyttsx3.init()
        speakingSpeed = speechEngine.getProperty('rate')
        speakingSpeed = int(str(speakingSpeed)) - self.speechSpeed
        speechEngine.setProperty('rate', speakingSpeed)

        if self.addedOptions:
            self.__fineTune()

        return speechEngine


# Function to convert text to speech
def SpeakText(command):
    if checkInternetConnection():
        # save the audio file, replay it to the user and then delete it
        file = "speech.mp3"
        gTTS(text=command, lang='en', slow=False).save(file)
        song = AudioSegment.from_mp3(file)
        play(song)
        os.remove(file)
    else:
        engine = SpeechEngine().createTTSEngine()
        engine.say(command)
        engine.runAndWait()


def checkInternetConnection():

    try:
        requests.get("https://www.google.com", timeout=5)
        return True
    except requests.ConnectionError:
        print("No internet connection available.")

    return False


class Weather:
    def __init__(self):
        self.api_key = "OpenWeather_API_KEY"
        self.__key = self.get_conf_data()
        self.USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36" \
                          " (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36 "
        # US english
        self.LANGUAGE = "en-US,en;q=0.5"

    def get_conf_data(self):
        config = configparser.ConfigParser()
        config.read('configurations/apiKeys.ini')
        return config.get("KEYS", self.api_key)

    @staticmethod
    def convertToCelsius(value):
        return int((value - 32) / 1.8000)

    @property
    def get_local_city_data(self):
        # base_url variable to store url
        base_url = "http://api.openweathermap.org/data/2.5/weather?"
        city_name = "Ashdod, Israel"
        complete_url = '{0}appid={1}&q={2}'.format(base_url, self.__key, city_name)

        # get method of requests module return response object
        response = requests.get(complete_url).json()

        # Check the value of "cod" key is equal to "404", means city is found otherwise,
        # city is not found
        if response["cod"] != "404":
            current_temperature = self.convertToCelsius(int(response['main']["temp"]))
            current_humidity = str(response['main']["humidity"])
            weather_description = str(response['weather'][0]["description"])

            # Return the values collected
            return ("Temp:(in kelvin unit) = " +
                    str(self.convertToCelsius(current_temperature)) +
                    "\n humidity = " + str(current_humidity) + "\n description = " +
                    str(weather_description))

    def get_weather_data(self):
        return self.get_local_city_data


class WolframSolver:
    def __init__(self):
        self.apiKey = "WOLFRAME_API_KEY"
        self.__key = self.__get_conf_data()

    def __get_conf_data(self):
        config = configparser.ConfigParser()
        config.read('configurations/apiKeys.ini')
        return config.get("KEYS", self.apiKey)

    def solve(self, question):
        client = wolframalpha.Client(self.__key)
        res = client.query(question)
        if bool(res['@success']):
            answer = next(res.results).text
            print("The answer is " + answer)
            return f"The Answer to the question is: {answer}"
        else:
            raise Exception("error calculating the result")


class ParallelFileSearch:
    def __init__(self, baseDir):
        self.baseDir = baseDir
        self.results_queue = mp.Queue()
        self.dirContent = self.listFoldersInBaseDir()

    def findFile(self, folders, fileName):
        for folder in folders:
            for root, dirs, files in os.walk(folder, topdown=True):
                for file in files:
                    if fileName in file.lower():
                        self.results_queue.put(f'{os.path.join(root, file)}')

        print(f"finished traversing {len(folders)} folders, folders are {folders}")

    @staticmethod
    def checkPath(currentPath):
        # check if the path is related to python site-packages path or a hidden folder
        import re
        # TODO: check if the added regex works to find hidden folders
        hiddenFolders = "[0-9a-zA-Z]*.[0-9a-zA-Z]*"
        pythonPackages = "python[2,3]?.[0-9]+.?[0-9]*/site-packages/*"
        python_env = re.compile(pythonPackages, re.IGNORECASE)
        hiddenFolders = re.compile(hiddenFolders, re.IGNORECASE)
        isPathOK = lambda path: python_env.findall(path) and hiddenFolders.findall(path)

        return False if isPathOK(currentPath) else True

    def processResults(self, filePaths):
        """ This Function filters common app files like vscode, pycharm and etc from
            the found paths has well as other distractions to minimize the size"""
        resultFormat = lambda currPath: f'{self.baseDir}/{currPath}'
        removedBasedDir = map(lambda path: path.replace(f"{self.baseDir}/", ""), filePaths)

        return [resultFormat(path) for path in removedBasedDir if self.checkPath(path)]

    def listFoldersInBaseDir(self):
        pathFormat = lambda folder: f'{self.baseDir}/{folder}'
        TLFolders = next(os.walk(self.baseDir))[1]

        return [pathFormat(dirName) for dirName in TLFolders if dirName[0] != '.']

    def setupSearchPortions(self):
        numDirs, numCpus = len(self.dirContent), cpu_count()
        chunkSize = round(numDirs / numCpus)
        portions = range(0, numDirs, chunkSize)

        return [self.dirContent[chunk:chunk + chunkSize] for chunk in portions]

    def locateFileInSystem(self, fileName):
        chunks, filePaths = self.setupSearchPortions(), []

        with ThreadPoolExecutor() as executor:
            [executor.submit(self.findFile, portion, fileName) for portion in chunks]

        # If we found 0 matching files
        if self.results_queue.qsize() == 0:
            return False
        else:
            # collect the results
            while self.results_queue.qsize() > 0:
                filePaths.append(self.results_queue.get())

            return self.processResults(filePaths)
