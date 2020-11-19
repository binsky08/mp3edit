import os
import subprocess


def escapeForBash(text):
    text = text.replace(" ", "\\ ")
    text = text.replace("(", "\\(")
    text = text.replace(")", "\\)")
    text = text.replace("'", "\\'")
    return text


scanDirectory = os.getcwd()
print("Welcome to mp3edit")

dirInput = input("Scan folder (enter . for %s): " % scanDirectory)
if dirInput != ".":
    scanDirectory = dirInput

print("What do you want to edit?")
print("t (title)")
print("c (comment)")
print("a (artist)")
print("l (album)")

editMode = ""
editModeText = ""
while True:
    editMode = input("Please type t/c/a/l: ")
    if editMode in ("t", "c", "a", "b"):
        if editMode == "t":
            editModeText = "title"
        if editMode == "c":
            editModeText = "comment"
        if editMode == "a":
            editModeText = "artist"
        if editMode == "l":
            editModeText = "album"
        break

print("\nAvailable files:\n")
directories = os.scandir(scanDirectory)
files = []
for entry in directories:
    if entry.name.endswith(".mp3"):
        if os.path.isfile("%s/%s" % (scanDirectory, entry.name)):
            files.append(entry.name)
            print(entry.name)

if len(files) <= 0:
    print("No mp3 files found!")
    exit(0)

singleMode = False
print("Do you want to edit all files in once (a) (default) or every file manually (m)?")
while True:
    singleModeInput = input("Please type a/m: ")
    if singleModeInput == "a":
        singleMode = False
        break
    if singleModeInput == "m":
        singleMode = True
        break

replaceMode = None
print("Do you want to replace (r) the complete information or use the pattern editor (e)")
while True:
    singleModeInput = input("Please type r/e: ")
    if singleModeInput == "r":
        replaceMode = True
        break
    if singleModeInput == "e":
        replaceMode = False
        break

if replaceMode:
    if singleMode:
        for file in files:
            while True:
                newText = input("Enter the new text: ")
                print("%s - %s => %s" % (file, editModeText, newText))

                print("Do you want to apply these changes? (y/n)")
                apply = None
                while True:
                    singleModeInput = input("Please type y/n: ")
                    if singleModeInput == "y":
                        apply = True
                        break
                    if singleModeInput == "n":
                        apply = False
                        break
                if apply:
                    command = "mp3info -%s \"%s\" %s" % (editMode, newText, "%s/%s" % (escapeForBash(scanDirectory), escapeForBash(file)))
                    print(command)
                    os.system(command)
                    break
    else:
        while True:
            newText = input("Enter the new text: ")
            for file in files:
                print("%s - %s => %s" % (file, editModeText, newText))

            print("Do you want to apply these changes? (y/n)")
            apply = None
            while True:
                singleModeInput = input("Please type y/n: ")
                if singleModeInput == "y":
                    apply = True
                    break
                if singleModeInput == "n":
                    apply = False
                    break
            if apply:
                for file in files:
                    command = "mp3info -%s \"%s\" %s" % (editMode, newText, "%s/%s" % (escapeForBash(scanDirectory), escapeForBash(file)))
                    print(command)
                    os.system(command)
                break

else:
    print("Use one of the following options to generate the new %s text" % editModeText)
    print("(Options can not be combined except its also done in the example)\n")
    print("$ (use the original text, no changes)")
    print("\"xd\" (place new text in double high quotes like \"xd\" for 'xd' or $\"xd\" for '{original text}xd or \"xd\"$')")
    print("e-3 (use e-{number} to remove {number} characters from the end of the original text)")
    print("b-3 (use b-{number} to remove {number} characters from the beginning of the original text)")

    pattern = None
    if not singleMode:
        while True:
            pattern = input("Enter the edit option: ")
            if pattern == "$" or pattern.startswith("e-") or pattern.startswith("b-") \
                    or pattern.startswith("\"") or pattern.startswith("$"):
                break

    for file in files:
        originalText = None

        try:
            originalText = subprocess.check_output(
                ['mp3info', "%s/%s" % (scanDirectory, file), "-p %s" % "%" + editMode]) \
                .decode(encoding="UTF-8")
        except subprocess.CalledProcessError as err:
            print(err)
            continue

        if singleMode:
            print("Selected file: %s - %s: %s" % (file, editModeText, originalText))
            while True:
                pattern = input("Enter the edit option: ")
                if pattern == "$" or pattern.startswith("e-") or pattern.startswith("b-") \
                        or pattern.startswith("\"") or pattern.startswith("$"):
                    break

        if originalText is None:
            continue

        newText = None
        if pattern == "$":
            newText = originalText
        elif pattern.startswith("e-"):
            removeNumber = int(pattern.replace("e-", ""))
            if removeNumber > 0:
                newText = originalText[0:len(originalText) - removeNumber]
        elif pattern.startswith("b-"):
            removeNumber = int(pattern.replace("b-", ""))
            if removeNumber > 0:
                newText = originalText[removeNumber:len(originalText)]
        elif pattern.startswith("\"") or pattern.startswith("$"):
            newText = pattern.replace("\"", "").replace("$", originalText)

        command = "mp3info -%s \"%s\" %s" % (editMode, newText.strip(), "%s/%s" % (escapeForBash(scanDirectory), escapeForBash(file)))
        print(command)
        os.system(command)

print("Done!")
