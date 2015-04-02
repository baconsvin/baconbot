import asyncio
import irc3
from irc3.plugins.command import command


@irc3.plugin
class AlarmPlugin:
    def __init__(self, bot):
        self.bot = bot

    @command
    def alarm(self, mask, target, args):
        """Alarm command
        %%alarm [TIME]
        """
        time = float(args['TIME'] or 5.0)
        self.bot.loop.create_task(self.initiate_alarm(target, time))

    @asyncio.coroutine
    def initiate_alarm(self, target, time):
        self.bot.privmsg(target, 'ALARM INITIATED!')
        yield from asyncio.sleep(time)
        self.bot.privmsg(target, 'ALARM OFF!')


BOT = irc3.IrcBot(
    nick='baconbot',
    autojoins=['#baconbot'],
    host='irc.0x90.dk',
    port=6697,
    ssl=True,
    includes=[
        'irc3.plugins.core',
        'irc3.plugins.command',
        'irc3.plugins.human',
        __name__,
    ],
)

if __name__ == '__main__':
    BOT.run()
