# coding: utf-8
from datetime import datetime
import logging
import asyncio
import irc3
from irc3.plugins.command import command

codes = {
    'A_ON': "282 846 282 846 282 846 846 282 282 846 282 846 282 846 846 282 282 846 282 846 282 846 282 846 282 846 846 282 282 846 846 282 282 846 846 282 282 846 846 282 282 846 282 846 282 846 846 282 282 9588",
    'A_OFF': "280 840 280 840 280 1120 840 280 280 1120 280 840 280 840 840 280 280 840 280 840 280 1120 280 840 280 840 840 280 280 840 840 280 280 840 840 280 280 840 840 280 280 840 840 280 280 840 280 840 280 9520",
    'B_ON': "282 846 282 846 282 846 846 282 282 846 282 846 282 846 846 282 282 1128 282 846 282 846 846 282 282 846 282 846 282 846 846 282 282 846 846 282 282 846 846 282 282 846 282 1128 282 846 846 282 282 9588",
    'B_OFF': "281 843 281 843 281 843 843 281 281 843 281 843 281 843 843 281 281 843 281 1124 281 843 843 281 281 843 281 843 281 843 843 281 281 843 843 281 281 843 843 281 281 843 843 281 281 1124 281 843 281 9554",
    'C_ON': "282 846 282 846 282 846 846 282 282 846 282 846 282 846 846 282 282 1128 282 846 282 846 1128 282 282 1128 846 282 282 846 282 846 282 846 846 282 282 846 846 282 282 846 282 1128 282 846 846 282 282 9588",
    'C_OFF': "282 846 282 846 282 846 846 282 282 846 282 846 282 1128 846 282 282 846 282 1128 282 846 846 282 282 846 846 282 282 846 282 846 282 846 846 282 282 846 846 282 282 846 846 282 282 846 282 846 282 9588",
    'D_ON': "282 846 282 846 282 846 846 282 282 846 282 846 282 846 846 282 282 846 282 846 282 846 846 282 282 846 846 282 282 846 846 282 282 846 282 846 282 846 846 282 282 846 282 846 282 846 846 282 282 9588",
    'D_OFF': "281 843 281 843 281 843 843 281 281 843 281 843 281 843 843 281 281 843 281 843 281 843 843 281 281 843 843 281 281 843 843 281 281 843 281 843 281 843 843 281 281 843 843 281 281 843 281 843 281 9554",
}

logging.basicConfig(filename='bot.log',level=logging.DEBUG)

@irc3.plugin
class AlarmPlugin:
    def __init__(self, bot):
        self.bot = bot

    @command
    def love(self, mask, target, args):
        """Love command
        %%love [TIME]
        """
        time = min(float(args['TIME'] or 5), 3600)
        logging.info('Starting love for {} seconds'.format(time))
        self.bot.privmsg(target, 'Så er der kærlighed i {} sekunder!'.format(time))
        self.bot.loop.create_task(self.process_love(target, time))

    @asyncio.coroutine
    def process_love(self, target, time):
        self.bot.loop.create_task(self.send_signal(target, 'C_ON'))
        yield from asyncio.sleep(time)
        for _ in range(50):
            self.bot.loop.create_task(self.send_signal(target, 'C_OFF'))

    @command
    def alarm(self, mask, target, args):
        """Alarm command
        %%alarm [TIME]
        """
        time = min(float(args['TIME'] or 5), 3600)
        logging.info('Starting alarm for {} seconds'.format(time))
        self.bot.privmsg(target, 'ALARM ALARM ALARM I {} SEKUNDER!'.format(time))
        self.bot.loop.create_task(self.process_alarm(target, time))

    @asyncio.coroutine
    def process_alarm(self, target, time):
        for _ in range(50):
            self.bot.loop.create_task(self.send_signal(target, 'A_ON'))
        yield from asyncio.sleep(time, loop=self.bot.loop)
        for _ in range(50):
            self.bot.loop.create_task(self.send_signal(target, 'A_OFF'))

    @command
    def illuminate(self, mask, target, args):
        """Illuminate command
        %%illuminate
        """
        self.bot.privmsg(target, 'Illuminate!')
        logging.info('Illuminate')
        for _ in range(50):
            self.bot.loop.create_task(self.send_signal(target, 'D_ON'))

    @command
    def deluminate(self, mask, target, args):
        """Deluminate command
        %%deluminate
        """
        self.bot.privmsg(target, 'Deluminate!')
        logging.info('Deluminate')
        for _ in range(50):
            self.bot.loop.create_task(self.send_signal(target, 'D_OFF'))

    @asyncio.coroutine
    def send_signal(self, target, code_id):
        base_command = 'sudo pilight-send -p raw -c "{}"'
        command = base_command.format(codes[code_id])
        logging.debug('{}: {}: {}'.format(datetime.now(), code_id, command))
        yield from asyncio.create_subprocess_shell(command, loop=self.bot.loop)
