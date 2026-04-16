

try:
    f = open("demofile.text", "r")
    f.write("Hello! Welcome to demofile.txt This file is for testing purposes. Good Luck!")
except:
    print("file does not exist")
finally:
    print("Process ended")