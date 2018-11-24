import subprocess
import sys

def install_libraries(libs):
    subprocess.call([sys.executable, "-m", "pip", "install", "--upgrade", *libs])

if __name__ == '__main__':
    libs = ['requests', 'python-telegram-bot']
    install_libraries(libs)

    files = [
        'user_dict.db',
        'notif_dict.db'
    ]

    for file in files:
        open(file, 'a').close()