# os libraury
import os
# ask usr for input and save it to choice variable
choice=input("Want to ShutDown ? (y or n):-")

if(choice=='y' or choice=='Y'):
    #/t shutdown after 100 sec
    #/s for shut down /r restart and /l log off
    os.system("shutdown /s /t 100")
else:
    print("Doing Nothing")

