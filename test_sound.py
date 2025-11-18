import time
import simpleaudio as sa

print("Scheduling sound in 3 seconds...")
time.sleep(3)
print("Playing sound now!")

wave_obj = sa.WaveObject.from_wave_file("notification.wav")
play_obj = wave_obj.play()
play_obj.wait_done()

print("Done.")
