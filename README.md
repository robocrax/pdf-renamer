# Bulk save PDF's from Gmail and rename
Using Google Apps Script (free quota) for any incoming mails with matching params and PDF attachment, saves it and optionally renames it by converting PDF to text using OCR and using content in it.

Email is marked as read after script downloads the email to notify user/you. Can also add a label once done if you prefer

## For printing

Additionally to automatically print the attachments, I'm using [benjamin-kromer](https://github.com/benjamin-kromer)'s [printHotfolder](https://github.com/benjamin-kromer/printHotfolder) python script idea but using Python 3

Since PDFs are received in random order, and synced using Google Backup and Sync in random order as well, I've added a delay to confirm all files are received then start printing them (not prematurely). Delay of 1-2 minutes should easily be enough unless you are on 2G satellite connection

## Requirements

- Assuming you're a dev (not necessarily Python or Javascript)
- You have a 3rd party application (like Adobe Reader for PDFs) for print support.
  - Right-click a document and make sure you see a Print option
  * Hint: make sure your 3rd party app is the default and not some other app like Microsoft Edge if you don't see Print option in context menu. If you see the option, you're golden
  
## Compile using Pyinstaller

> pyinstaller PrintFolderAndArchive.py -i printer.ico --onefile --hiddenimport pywintypes
