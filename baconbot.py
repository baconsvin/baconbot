# coding: utf-8
from datetime import datetime
import logging
import asyncio
import irc3


logging.basicConfig(filename='bot.log',level=logging.DEBUG)


@irc3.plugin
class SwitchControllerPlugin:

    """
    Plugin to control RF sockets.
    """

    def __init__(self, bot):
        self.bot = bot
        module = self.__class__.__module__
        self.config = bot.config.get(module, {})
        self.commands = {}
        for command in self.config['commands']:
            args = command.split(' ')
            self.commands[args[0]] = {'id': args[1]}
            if len(args) == 3:
                self.commands[args[0]]['value'] = args[2]

    @irc3.event((r':(?P<mask>\S+) PRIVMSG (?P<target>\S+) '
                 r':{re_cmd}(?P<cmd>\w+)(\s(?P<data>\S.*)|$)'))
    def on_command(self, cmd, mask=None, target=None, client=None, **kwargs):
        if cmd in self.commands:
            command_args = self.commands[cmd]
            command_id = int(command_args.get('id'))
            value = command_args.get('value', None)

            if value:
                self.bot.loop.create_task(
                    self.send_signal(target, command_id, value)
                )
            else:
                arg = kwargs.get('data', None)
                self.bot.loop.create_task(
                    self.process_maybe_timed_command(target, command_id, arg)
                )

    @asyncio.coroutine
    def process_maybe_timed_command(self, target, unit, arg=None):
        OFF_WORDS = ['off', 'false', 'f']
        timed = False

        if not arg or arg not in OFF_WORDS:
            self.bot.loop.create_task(self.send_signal(target, unit, 't'))

        try:
            if int(arg) > 0:
                yield from asyncio.sleep(min(int(arg), 3600), loop=self.bot.loop)
                timed = True
        except ValueError:
            pass
        except TypeError:
            pass

        if arg in OFF_WORDS or timed:
            self.bot.loop.create_task(self.send_signal(target, unit, 'f'))

    @asyncio.coroutine
    def send_signal(self, target, code_id, state):
        switch_command = (
            'sudo pilight-send -p elro_800_switch -s 21 -u {} -{}'.format(
                code_id, state
            )
        )

        logging.debug(
            '{}: {}: {}'.format(datetime.now(), code_id, switch_command)
        )

        yield from asyncio.create_subprocess_shell(
            switch_command,
            loop=self.bot.loop
        )
