# coding: utf-8
import re
from datetime import datetime
import logging
import asyncio
import irc3
from irc3.plugins.command import command

logging.basicConfig(filename='bot.log',level=logging.DEBUG)


@irc3.plugin
class SwitchControllerPlugin:

    """
    Plugin to control RF sockets.
    """

    def __init__(self, bot):
        self.bot = bot
        self.switches = self.bot.db.get('switches', None)
        if not self.switches:
            self.bot.db['switches'] = {}
            self.switches = self.bot.db['switches']

    @irc3.event((r':(?P<mask>\S+) PRIVMSG (?P<target>\S+) '
                 r':{re_cmd}(?P<cmd>\w+)(\s(?P<data>\S.*)|$)'))
    def on_command(self, cmd, mask=None, target=None, client=None, **kwargs):
        if cmd in self.switches:
            switch_args = self.switches[cmd]
            signal = int(switch_args.get('signal'))
            value = switch_args.get('value', None)

            if value:
                self.bot.loop.create_task(
                    self.send_signal(target, signal, value)
                )
            else:
                arg = kwargs.get('data', None)
                self.bot.loop.create_task(
                    self.process_maybe_timed_command(target, signal, arg)
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

    @command
    def switches(self, mask, target, args):
        """Switches command

        %%switches
        """
        self.bot.notice(target, '{:<15}| {:15}| {:<15}'.format(
            'Command', 'Signal', 'Value'
        ))
        for switch_name, switch_args in self.switches.items():
            signal = switch_args.get('signal', None)
            value = switch_args.get('value', None)
            if value:
                message = '{switch_name:<15}| {signal:<15}| {value:<15}'.format(
                    switch_name=switch_name,
                    signal=signal,
                    value=value
                )
            else:
                message = '{switch_name:<15}| {signal:<15}|'.format(
                    switch_name=switch_name,
                    signal=signal,
                )

            self.bot.notice(target, message)

    @command
    def setswitch(self, mask, target, args):
        """ Setswitch command

        %%setswitch <switch_name> <signal> [<value>]
        """
        switch_name = re.sub(r'\W+', '', args['<switch_name>'])
        signal = int(args['<signal>'])
        value = args['<value>'] if args['<value>'] in ['t', 'f'] else None

        if switch_name and signal:
            self.switches[switch_name] = {
                'signal': signal
            }
            if value:
                self.switches[switch_name]['value'] = value

    @command
    def delswitch(self, mask, target, args):
        """ Delswitch command

        %%delswitch <switch_name>
        """
        switch_name = args['<switch_name>']
        del self.switches[switch_name]
