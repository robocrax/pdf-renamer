import os
import time
import sys
import json
import win32print
import win32api
from datetime import datetime

pdf_dir = "C:\\Users\\Tom\\Desktop\\Watching\\"
archive_dir = "C:\\Users\\Tom\\Desktop\\Donezos\\"
queue_file = "C:\\hotfolder_queue.json"
delay = 2*60   # in seconds * 60 (minutes...duh)
# force_printer = "Microsoft Print to PDF"

def fileList(x):
    files = []
    filesInFolder = sorted(os.listdir(x))
    for f in filesInFolder:
        if f[-4:] == ".pdf":
            files.append(f)
    return files

def checkForNewFiles(x):
    return not (queue() == fileList(x))

def getLogTime():
    now = datetime.now()
    t = now.strftime("%Y-%m-%d_%H%M%S")
    return t

def moveFile(source, dest):
    try:
        os.rename(source, dest)
    except Exception as e:
        print(e)
    return None

"""
scheduleAhead accepts x which is an array of files in the folder that will now be the queue.

Right now this ignores any extra files which were in the queue that no longer exist in the folder and just overrides queue with what's there currently, also without informing or logging

"""
def scheduleAhead(x):
    json_data = {"last_detect": 0, "force_printer": False, "queue": [], "watch_dir": False, "archive_dir": False}
    try:
        with open(queue_file, "r") as jsn:
            json_data = json.load(jsn)
        json_data["last_detect"] = time.time()
        json_data["queue"] = x
    except IOError:
        print("Generating schedule file...")
    except:
        raise SystemExit('Something is wrong with the schedule ahead JSON file, possibly the format. Script cannot run. \nHINT: You can delete the queue file and start a fresh.')
    with open(queue_file, 'w') as jsn:
        json.dump(json_data, jsn)

def jsonFileFix():
    try:
        sys.argv[1]
    except IndexError:   # Not sure if I should also catch NameError
        pass
    else:
        if sys.argv[1] == "reset":
            try:
                os.remove(queue_file)
                raise SystemExit('Schedule reset!')
            except FileNotFoundError:   # This can never be caught unless function called directly 
                raise SystemExit('No schedule file detected. No reset required.')
            #return True
        else:
            pass
    raise SystemExit('Damaged schedule JSON file, possibly the format. Script cannot run. \nHINT: You can run the following to start a fresh.\n\n          `'+sys.argv[0]+' reset`')

def queue():
    try:
        with open(queue_file, "r") as jsn:
            json_data = json.load(jsn)
        return json_data["queue"]
    except IOError:
        scheduleAhead([])
        return []
    except:
        print(jsonFileFix())

def canRunSchedule():
    try:
        with open(queue_file, "r") as jsn:
            json_data = json.load(jsn)
        if len(json_data["queue"])>0:    # 1-liners are boring so traditional if else
            return ( time.time() - json_data["last_detect"] ) > delay   # okay maybe not that boring
        else:
            return False
    except:
        print(jsonFileFix())

def dropFromQueue(x):
    try:
        with open(queue_file, "r") as jsn:
            json_data = json.load(jsn)
        json_data["queue"].remove(x)
        with open(queue_file, 'w') as jsn:
            json.dump(json_data, jsn)
    except:
        print(jsonFileFix())

def viewAllPrinters():
    printers = win32print.EnumPrinters(2)
    default_printer = win32print.GetDefaultPrinter()
    for printer in printers:
        if printer[2] == default_printer:
            print("==> " + printer[2] + " <== Default")
        else:
            print("    " + printer[2])
    exit()

def setPrinter(x):
    try:
        with open(queue_file, "r") as jsn:
            json_data = json.load(jsn)
    except IOError:
        main()
        setPrinter(x)
        exit() # Dont loop
    except:
        jsonFileFix()
    if x == "auto":
        json_data["force_printer"] = False
        print('Default printer controlled by Windows.')
    else:
        json_data["force_printer"] = x
        default_printer = win32print.GetDefaultPrinter()
        if x == default_printer:
            print('That is already your default printer')
        else:
            win32print.SetDefaultPrinter(x)
            print('Default printer changed to "'+sys.argv[2]+'" globally and for this script as well.')
    with open(queue_file, 'w') as jsn:
        json.dump(json_data, jsn)
    exit()

def chosenPrinter():
    try:
        with open(queue_file, "r") as jsn:
            json_data = json.load(jsn)
    except IOError:
        scheduleAhead([])
    except:
        jsonFileFix()
    return json_data["force_printer"]

def startPrinting(x):
    force_printer = chosenPrinter()
    if force_printer:
        try:
            if win32print.GetDefaultPrinter() != force_printer:
                win32print.SetDefaultPrinter(force_printer)
        except:
            print('Cannot set your printer "'+force_printer+'" as default. Please see list below and choose one.\n')
            viewAllPrinters()   # exits after showing options
    for file in x:
        # Archive first so that file is not in use when archiving (just in case printer is still spooling)
        archive_file = os.path.join(archive_dir,getLogTime()+"_"+file)
        moveFile(os.path.join(pdf_dir,file),archive_file)
        # Send print using Windows default action
        win32api.ShellExecute(0,"print", archive_file, None,  ".",  0)
        print('Processed '+archive_file)
        dropFromQueue(file)

def main():
    if checkForNewFiles(pdf_dir):
        scheduleAhead(fileList(pdf_dir))
    if canRunSchedule():
        startPrinting(queue())

if __name__ == "__main__":
    try:
        sys.argv[1]
    except IndexError:   # Not sure if I should also catch NameError
        pass
    else:
        if sys.argv[1] == "list_printers":
            viewAllPrinters()
        elif sys.argv[1] == "set_printer":
            setPrinter(sys.argv[2])
        if sys.argv[1] == "pick_folders":
            exit('You found hidden arg. Go home now, this is not ready')
        elif sys.argv[1] == "help" or sys.argv[1] == "?":
            exit('Available options: help, reset, list_printers, set_printer "Microsoft Print to PDF"')
        elif sys.argv[1] == "reset":
            print('This is an optional command and only resets if needed or else program will continue normally.')
        else:
            print('Unrecognized argument, use ? to view available commands. Running default...')
    print('Watching '+pdf_dir)
    while True:
        try:
            time.sleep(10)
            main()
        except KeyboardInterrupt:
            exit('\nNo longer watching... Adios!')
