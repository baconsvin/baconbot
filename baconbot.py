# coding: utf-8
from datetime import datetime
import logging
import asyncio
import irc3
from irc3.plugins.command import command


logging.basicConfig(filename='bot.log',level=logging.DEBUG)

@irc3.plugin
class AlarmPlugin:
    def __init__(self, bot):
        self.bot = bot

    @command
    def alarm(self, mask, target, args):
        """Alarm command
        %%alarm [ARG]
        """
        arg = args.get('ARG', None)
        if arg:
            logging.info('Starting alarm for {} seconds'.format(arg))
            # self.bot.notice(mask.nick, 'ALARM ALARM ALARM I {} SEKUNDER!'.format(arg))
        self.bot.loop.create_task(
            self.process_maybe_timed_command(
                target, 1, arg
            )
        )

    @command
    def disco(self, mask, target, args):
        """Disco command
        %%disco [ARG]
        """
        arg = args.get('ARG', None)
        if arg:
            logging.info('Starting disco for {} seconds'.format(arg))
            # self.bot.notice(mask.nick, 'DiScO dAsCo I {} SEKUNDER!'.format(arg))
        self.bot.loop.create_task(
            self.process_maybe_timed_command(
                target, 2, arg
            )
        )

    @command
    def love(self, mask, target, args):
        """Love command
        %%love [ARG]
        """
        arg = args.get('ARG', None)
        if arg:
            logging.info('Starting love for {} seconds'.format(arg))
            # self.bot.notice(mask.nick, 'Så er der kærlighed i {} sekunder!'.format(arg))
        self.bot.loop.create_task(
            self.process_maybe_timed_command(
                target, 4, arg
            )
        )

    @command
    def illuminate(self, mask, target, args):
        """Illuminate command
        %%illuminate
        """
        self.bot.notice(mask.nick, 'Illuminate!')
        logging.info('Illuminate')
        self.bot.loop.create_task(self.send_signal(target, 8, 't'))

    @command
    def deluminate(self, mask, target, args):
        """Deluminate command
        %%deluminate
        """
        self.bot.notice(mask.nick, 'Deluminate!')
        logging.info('Deluminate')
        self.bot.loop.create_task(self.send_signal(target, 8, 'f'))

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
        base_command = 'sudo pilight-send -p elro_800_switch -s 21 -u {} -{}'
        command = base_command.format(code_id, state)
        logging.debug('{}: {}: {}'.format(datetime.now(), code_id, command))
        yield from asyncio.create_subprocess_shell(command, loop=self.bot.loop)
