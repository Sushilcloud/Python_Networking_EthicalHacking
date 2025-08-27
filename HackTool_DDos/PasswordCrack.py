#Python Super Powerfull Easy to use Libraury
#AI
#Network Libraury
# 3 way Handshake

import hashlib #hashlib
pass_hash=input("Enter md5 hash:  ")
wordlist=input("File name:  ")
try:
    pass_file=open(wordlist,"r")
except:
    print("No file found")
    quit()
# typing the logic
for word in pass_file:
    enc_wrd=word.encode('utf-8')
    #hexdigest inbuild funtion
    digest=hashlib.md5(enc_wrd.strip()).hexdigest()

    if digest==pass_hash:
        print("Password found")
        print("password is "+word)
        flag=1
        break
# when password is not in the list
if flag==0:
    print("password/passphrase is not in the list")
