import os
import time
import sys
#import shutil      # File copy and move stuff.. not yet ready
import json
from datetime import datetime

#all_printers = win32print.EnumPrinters(2)

pdf_dir = "C:\\Users\\Tom\\Desktop\\drive-download-20201231T010209Z-001"
archive_dir = "C:\\HOTFOLDER_DRUCK\\ARCHIV\\"
problem = "C:\\HOTFOLDER_DRUCK\\PROBLEMJOBS\\"
schedule_file = "C:\\hotfolder_schedule.json"
delay = 2*60   # in seconds * 60 (minutes...duh)

def fileList(x):
    files = []
    filesInFolder = sorted(os.listdir(x))
    for f in filesInFolder:
        if f[-4:] == ".pdf":
            files.append(f)
    return files

def checkForNewFiles(x):
    queue = readQueue()     # Have to rasterize these as variables or else they calculated x ( x = no. of files ) times
    newList = fileList(x)    # in the function below (Exponentially for no reason)
    return not all(item in queue for item in newList)    # https://www.techbeamers.com/program-python-list-contains-elements/#all-method

def getLogTime():
    now = datetime.now()
    t = now.strftime("%Y-%m-%d_%H%M")
    return t

def moveFile(f):
    while f in os.listdir(x):
        try:              
            time.sleep(3)
            print(getLogTime() + " REMOVING "+f+" FROM INPUT FOLDER!")
            os.remove(os.path.join(pdf_dir,f))
        except Exception as e:
            print(e)
            time.sleep(5)
    return None

"""
scheduleAhead accepts x which is an array of files in the folder that will now be the queue.

Right now this ignores any extra files which were in the queue that no longer exist in the folder and just overrides queue with what's there currently, also without informing or logging

"""
def scheduleAhead(x):
    json_data = {"last_detect": 0, "queue": []}
    try:
        with open(schedule_file, "r") as jsn:
            json_data = json.load(jsn)
        json_data["last_detect"] = time.time()
        json_data["queue"] = x
    except IOError:
        print("Generating schedule file...")
    except:
        raise SystemExit('Something is wrong with the schedule ahead JSON file, possibly the format. Script cannot run. \nHINT: You can delete the queue file and start a fresh.')
    with open(schedule_file, 'w') as jsn:
        json.dump(json_data, jsn)

def jsonFileFix():
    try:
        sys.argv[1]
    except IndexError:   # Not sure if I should also catch NameError
        pass
    else:
        if sys.argv[1] == "reset":
            try:
                os.remove(schedule_file)
                raise SystemExit('Schedule reset!')
            except FileNotFoundError:   # This can never be caught unless function called directly 
                raise SystemExit('No schedule file detected. No reset required.')
            #return True
        else:
            pass
    raise SystemExit('Damaged schedule JSON file, possibly the format. Script cannot run. \nHINT: You can run the following to start a fresh.\n\n          `'+sys.argv[0]+' reset`')
    return False

def readQueue():
    try:
        with open(schedule_file, "r") as jsn:
            json_data = json.load(jsn)
        return json_data["queue"]
    except IOError:
        scheduleAhead([])
        return []
    except:
        print(jsonFileFix())
        return []

def checkScheduleCanRun():
    try:
        with open(schedule_file, "r") as jsn:
            json_data = json.load(jsn)
        if len(json_data["queue"])>0:    # 1-liners are boring so traditional if else
            return ( time.time() - json_data["last_detect"] ) > delay   # okay maybe not that boring
        else:
            return False
    except:
        print(jsonFileFix())

def startPrinting():
    print("start printing.. not ready yet")

def main():
    if checkForNewFiles(pdf_dir):
        scheduleAhead(fileList(pdf_dir))
    if checkScheduleCanRun():
        startPrinting()

if __name__ == "__main__":
    main()
    print('Watching '+pdf_dir)
    while True:
        try:
            time.sleep(10)
            main()
        except KeyboardInterrupt:
            exit('\nNo longer watching... Adios!')


# while False:
#     time.sleep(10) # 10 sec intervals... not needed but 
#     files = checkForNewFiles()
#     time.time()
#     if len(files) > 0:
#         time.sleep(6) # WARTEN BIS SWITCH DEN PREFIX ENTFERNT HAT 
#         files = checkForNewFiles() # ANSCHLIESSEND ORDNER NEU EINLESEN
#         for f in files:
#             pattern = re.compile('\_([a-zA-Z0-9\s\-]+)\.pdf')
#             match = pattern.search(f)
#             try:
#                 printer = match.group(1)
#                 defaultPrinter = win32print.GetDefaultPrinter()
#                 if defaultPrinter != printer:
#                     win32print.SetDefaultPrinter(printer)
#                 print getActualTime()+" PRINTING FILE "+ f +" on "+printer
#                 win32api.ShellExecute(0,"print", os.path.join(pdf_dir,f), None,  ".",  0)
#                 print getActualTime()+" COPY "+f+" to ARCHIVE!"
#                 shutil.copy(os.path.join(pdf_dir,f),os.path.join(archive_dir,f))
#                 deleteFile(f)
#                 print getActualTime()+" FILE "+f+" SUCCESSFULLY PRINTED!"
#             except Exception as e:
#                 print e
#                 shutil.copy(os.path.join(pdf_dir,f),os.path.join(problem,f))
#                 deleteFile(f)
