import os
import argparse

from speechAnalyze import SpeechAnalyzer


def checkFileExists(file):
    if os.path.isfile(str(file)):
        return str(file)
    else:
        raise argparse.ArgumentTypeError("File not Found")


def parseArgs():
    parser = argparse.ArgumentParser(description='Jarvis virtual Assistant')
    parser.add_argument('--readFromFile',
                        type=checkFileExists,
                        help='Run the program with an audio input file')
    parser.add_argument('--openGui', "-G",
                        help='Run the program to read input from an audio file')
    parser.add_argument("--version", "-v",
                        type=str,
                        help="Prints version and exits")
    return parser.parse_args()


def main():
    speech, parsedArgs = SpeechAnalyzer(), parseArgs()

    if parsedArgs.readFromFile:
        speech.analyzeFileForOffline(parsedArgs.readFromFile)
    else:
        speech.liveUserSession() # Incase a user wants a live session


if __name__ == "__main__":
    main()
