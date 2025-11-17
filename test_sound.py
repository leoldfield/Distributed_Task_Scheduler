import time
from playsound import playsound

print("Scheduling sound in 3 seconds...")
time.sleep(3)
print("Playing sound now!")
playsound('notification.mp3')
print("Done.")
