import re, os
import platform
import subprocess
import webbrowser

from guiConfigurations.fileChooser import fileDisplay
from helperClasses import get_sys_data, get_file_location, SpeakText


class Linux:
    def __init__(self):
        self.type = "linux"
        self.sys = platform.platform()
        self.scriptsFolder = f'{os.getcwd()}/scripts/linux/'
        self.userFolder = os.path.expanduser("~")

    @property
    def getFS_size(self):
        import shutil

        total, used, free = shutil.disk_usage("/")
        return int(total // (2 ** 30))

    @property
    def listInstalledApps(self):
        listScriptPath = f"{self.scriptsFolder}/listInstalledApps.sh"
        # subprocess.call(['chmod', '+x', f"{self.scriptsFolder}*.sh"], shell=True)
        installedApps = subprocess.check_output(["bash", "{0}".format(listScriptPath)])
        return installedApps.split()


class OSes:
    def __init__(self):
        self.oses = {"linux": Linux}
        self.host_os = self.oses[platform.system().lower()]()

    @staticmethod
    def __parseSearchQuery(searchQuery):
        sitesToRemove = r"\b(google|wikipedia|facebook|youtube|define)\b"
        query = searchQuery.lower().replace("for", "").replace("the", "")
        query = re.sub(sitesToRemove, "", query)
        return query

    def __SearchTheInternet(self, website):
        queryString = self.__parseSearchQuery(website)

        if "youtube" in website:
            queryString = f"https://www.youtube.com/results?search_query={queryString}"
        elif "wikipedia" in website:
            queryString = f"https://en.wikipedia.org/wiki/{queryString}"
        elif "google" in website:
            queryString = f"https://www.google.com/search?q={queryString}"
        elif "facebook" in website:
            queryString = f"https://www.facebook.com"
        else:
            queryString = f"https://www.google.com/search?q={queryString}"

        webbrowser.open(queryString, new=2)
        return True

    def __openFile(self, filepath):
        locatedFiles = get_file_location(filepath, self.host_os.userFolder)
        if len(locatedFiles) > 1:
            SpeakText("Found more than 1 file, Please choose one:")
            absPath = fileDisplay(locatedFiles).getUsersChoise()
        else:
            absPath = locatedFiles

        if self.host_os.type == "darwin":
            subprocess.call(['open', absPath], shell=True)
            return True
        elif self.host_os.type == "linux":
            subprocess.run(['xdg-open', absPath])
            return True
        elif self.host_os.type == "win32":
            os.startfile(absPath)
            return True

        return False

    def __openApplication(self, app):
        hostOSApps = self.host_os.listInstalledApps

        foundApps = [sys_app.decode() for sys_app in hostOSApps if app in str(sys_app.decode().lower())]

        if len(foundApps) == 1:
            print(f"Running the desktop app {foundApps}")
            subprocess.run([str(foundApps)], shell=True)
            return True
        elif foundApps is not []:
            print("found a number of apps, please choose one:")
            sys_app = fileDisplay(list(set(foundApps))).getUsersChoise()
            print(f"Running the desktop app {sys_app}")
            subprocess.run([sys_app], shell=True)
            return True
        else:
            return False

    def checkWhetherAppOrFile(self, userRequest):
        fileExtensions = ["py", "txt", "o", "log", "c", "cpp", "pdf", "pptx"]
        if "." in userRequest:
            if userRequest.split(".")[1] in fileExtensions:
                return lambda file: self.__openFile(file)
        else:
            return lambda app: self.__openApplication(app)

    def __open(self, search):
        whatToOpen = self.checkWhetherAppOrFile(search)
        if whatToOpen(search):
            return True
        else:
            SpeakText("Sorry couldn't find the requested file or app")
            return False

    def __getUserFolder(self, user=""):
        return self.host_os.userFolder

    @staticmethod
    def __getSystemData(system=""):
        return get_sys_data()

    def __buildAction_dict(self):
        actions = [["open", self.__open], ["launch", self.__openApplication],
                   ["search", self.__SearchTheInternet], ["define", self.__SearchTheInternet],
                   ["userFolder", self.__getUserFolder], ["system", self.__getSystemData]]
        return {action[0]:action[1] for action in actions}

    def actions(self, user_command):
        operations = self.__buildAction_dict()
        action = user_command.split()[0].lower()

        if action in list(operations.keys()):
            cmd = " ".join(user_command.split()[1::])
            return operations.get(action)(cmd)
        else:
            print('Operation not supported')
            raise Exception("Command TO FOUND")
