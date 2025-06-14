import subprocess
import os

commands = [
    "adb -s 127.0.0.1:16384 shell am start-foreground-service --user 0 -a jp.co.cyberagent.stf.ACTION_START -n jp.co.cyberagent.stf/.Service && adb -s 127.0.0.1:16384 forward tcp:1100 localabstract:stfservice && nc64 localhost 1100",
    "adb -s 127.0.0.1:16384 forward tcp:1090 localabstract:stfagent && adb -s 127.0.0.1:16384 shell pm path jp.co.cyberagent.stf && adb -s 127.0.0.1:16384 shell export CLASSPATH=\"package:/data/app/~~Jr-GxeGnZxBjP1TWUJA3rw==/jp.co.cyberagent.stf-yTMn6Do7T6PDkxk1PiTaBg==/base.apk\";exec app_process /system/bin jp.co.cyberagent.stf.Agent",
    "adb -s 127.0.0.1:16384 shell /data/local/tmp/minitouch",
    "adb -s 127.0.0.1:16384 forward tcp:1090 localabstract:minitouch && nc localhost 1090"
]

# Define the CREATE_NO_WINDOW flag
CREATE_NO_WINDOW = 0x08000000

for command in commands:
    subprocess.Popen(command, creationflags=CREATE_NO_WINDOW, shell=True)


