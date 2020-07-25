from settings import *
import os
import pathlib


PID = os.getpid()


def open_file(filename, mode='r'):
    path = pathlib.Path(filename)
    parent = str(path.parent).replace('\\', '/').split('/')
    current = ''
    while parent:
        current += parent.pop(0) + '/'
        if not pathlib.Path(current).exists():
            try:
                pathlib.Path(current).mkdir()
            except FileExistsError:
                pass
    return open(filename, mode)


def listdir(path):
    try:
        return os.listdir(path)
    except FileNotFoundError:
        return []


def getsize(path):
    try:
        return os.path.getsize(path)
    except FileNotFoundError:
        return 0