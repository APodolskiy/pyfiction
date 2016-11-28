import os
import time
from subprocess import *

from games.supported_games import GameType
from simulator.nbstreamreader import NonBlockingStreamReader


class Simulator:


    def __init__(self, game):
        self.__game = game
        self.__game_type = None
        self.__path = None
        self.__interpreter_path = None
        self.__nbsr = None
        self.simulator = None

    def start_game(self, interpreter_path = None, game_path = None):



        self.simulator = Popen([self.__game.interpreter.path, self.__game.path], stdin=PIPE, stdout=PIPE, stderr=STDOUT,
                               bufsize=1, universal_newlines=False)
        print('Running interpreter ', self.__game.interpreter.path, ' on game ', self.__game.path)

        # using cmd for testing purposes instead of an IF interpreter.py + game
        # terminal = "ls"
        # if os.name != "posix":
        #     terminal = "cmd"
        # self.game = Popen([terminal], stdin=PIPE, stdout=PIPE, stderr=STDOUT,
        #                   bufsize=1, universal_newlines=True)

        self.__nbsr = NonBlockingStreamReader(self.simulator.stdout)
        print('Game started')

    def startup_actions(self):
        for action in self.__game.startup_actions:
            time.sleep(1)
            self.write(action)
            print(self.read(1))

    def write(self, text):
        print('writing ', text)
        self.simulator.stdin.flush()
        self.simulator.stdin.write(text.encode('utf-8'))
        print('write end')

    # TODO: add a regexp 'timeout' (e.g. read until '\n >' is read)
    def read(self, timeout=0.001):
        print('read start')
        lines = []
        while True:
            line = self.__nbsr.readline(timeout)
            if line is not None:
                lines.append(line)
                # print(output)
                self.simulator.stdout.flush()
            else:
                # print('[No more data]')
                break
                # print(output)

        print('read end')
        return lines