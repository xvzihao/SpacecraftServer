import subprocess
import sys
import time
from ssl import create_default_context
from threading import Thread
from urllib.request import urlopen, Request

from flask import Flask, json
from json import load as json_file
from psutil import Process

from locals import *


class APIServer:
    def __init__(self):
        self.api = Flask(
            import_name=""
        )
        self.running = False

        @self.api.route('/stop', methods=['GET'])
        def op_stop():
            self.stop()
            return "api server is stopped"

        @self.api.route('/mods/planned', methods=['GET'])
        def get_modes_planned():
            with open("./mods.json") as f:
                return json.dumps(json_file(f))

        @self.api.route("/mods/installed", methods=['GET'])
        def get_modes_installed():
            return json.dumps(
                listdir("./server/mods/")
            )

    def launch(self):
        self.running = True
        self.api.run(
            host='0.0.0.0',
            port=2005
        )

    def stop(self):
        self.running = False

        def _stop():
            time.sleep(0.5)
            Process(PID).terminate()

        Thread(target=_stop).start()


def install_server():
    link = "https://files.minecraftforge.net/maven/net/minecraftforge/forge/1.12.2-14.23.5.2854/forge-1.12.2-14.23.5" \
           ".2854-installer.jar "
    with urlopen(
            url=Request(
                url=link,
                headers={
                    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1",
                }
            ),
            context=create_default_context()
    ) as browser:
        size = 4602
        with open('./installer.jar', 'wb') as f:
            data = None
            i = 0
            while data != b'':
                i += 1
                percentage = round(i / size * 100)
                print(f"[{str(percentage).rjust(3)}%] Loading installer [{('=' * round(percentage // 5) + '>').ljust(20)}]", end='\r')
                data = browser.read(1024)
                f.write(data)
            percentage = 100
            print(f"[{str(percentage).rjust(3)}%] Loading installer [{('=' * round(percentage // 5)).ljust(20)}]")

        command = "java -jar ./installer.jar --installServer ./server/"
        print("Running Command:", command)
        subprocess.call(command)
        print('=' * 30)

        print("Removing Installer...")
        os.remove("installer.jar")
        os.remove('installer.jar.log')

        print("Modifying Settings...")
        with open("./server/eula.txt", 'w') as f:
            f.write("eula=true")

        try:
            with open("./server/server.properties", 'r') as f:
                content = f.read()
        except FileNotFoundError:
            content = ''

        with open('./server/server.properties', 'w') as f:
            if 'online-mode' in content:
                content = content.replace('online-mode=true', 'online-mode=false')
            else:
                content += "\nonline-mode=false\n"
            if 'enable-rcon' in content:
                content = content.replace('enable-rcon=false', 'enable-rcon=true')
            else:
                content += "\nenable-rcon=true\n"
            f.write(content)
        print("Done. ")


def fetch_mod(url, file):
    with urlopen(
            url=Request(
                url=url,
                headers={
                    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 ("
                                  "KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1",
                }
            ),
            context=create_default_context()
    ) as browser:
        name = file
        file = os.path.join("./server/mods/", file)
        size = int(browser.headers.get("Content-Length"))
        if getsize(file) != size:
            with open_file(file, 'wb') as f:
                count = 0
                while count != size:
                    data = browser.read(1024)
                    percentage = int(count / size * 100)
                    print(f"[{str(percentage).rjust(3)}%] Fetching Mod '{name}' [{ ('=' * (percentage // 5)).ljust(20) }]", end='\r')
                    count += len(data)
                    f.write(data)
                percentage = 100
                print(f"[{str(percentage).rjust(3)}%] Fetching Mod '{name}' [{('=' * (percentage // 5)).ljust(20)}]")


def update_mods():
    with open("./mods.json") as f:
        mod_list = json_file(f)
    for mod in mod_list:
        fetch_mod(mod_list[mod]['link'], mod)
    print("Done. ")


def clean_mods():
    with open("./mods.json") as f:
        mod_list = json_file(f)
    planned = []
    for mod in mod_list:
        planned.append(mod)

    def is_mod(name):
        return name.endswith('.jar') or name.endswith('.litemod')

    for mod in listdir("server/mods/"):
        if is_mod(mod) and mod not in planned:
            os.remove("server/mods/"+mod)
            print(f"Removed Mod '{mod}'")

    print("Done. ")


def update_server():
    install_server()
    print("=" * 30)
    print("Updating Modes...")
    update_mods()
    print('=' * 30)
    print("Check Non-Used Mods...")
    clean_mods()


def launch():
    os.chdir('./server')
    subprocess.call('java -jar -Xmx4096m forge-1.12.2-14.23.5.2854.jar nogui')


def show_help():
    pass


if __name__ == '__main__':
    if 'mods.json' not in os.listdir('.'):
        with open('mods.json', 'w') as f:
            f.write("{}")
    args = sys.argv[1:]
    if len(args) == 1:
        if args[0] == 'api':
            server = APIServer()
            server.launch()
            exit(0)
        elif args[0] == 'update':
            update_server()
            exit(0)
        elif args[0] == 'launch':
            launch()
            exit(0)

    elif len(args) == 2:
        if args[0] == 'mods':
            if args[1] == 'update':
                update_mods()
                exit(0)
            elif args[1] == 'clean':
                clean_mods()
                exit(0)
    show_help()