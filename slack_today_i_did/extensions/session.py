import datetime
from typing import List
import json
import re
from collections import defaultdict
import importlib
import types

from slack_today_i_did.reports import Report
from slack_today_i_did.generic_bot import BotExtension, ChannelMessage, ChannelMessages
from slack_today_i_did.reports import Sessions
from slack_today_i_did.known_names import KnownNames
from slack_today_i_did.notify import Notification
import slack_today_i_did.parser as parser
import slack_today_i_did.text_tools as text_tools


class SessionExtensions(BotExtension):
    def _setup_sessions(self) -> None:
        self.sessions = Sessions()
        self.sessions.load_from_file(self.session_file)

    def start_session(self, channel: str) -> ChannelMessages:
        """ starts a session for a user """
        person = self._last_sender
        self.sessions.start_session(person, channel)
        self.sessions.save_to_file(self.session_file)

        message = """
Started a session for you. Send a DMs to me with what you're working on throughout the day.
Tell me `end-session` to finish the session and post it here!
"""
        return ChannelMessage(channel, message.strip())

    def end_session(self, channel: str) -> ChannelMessages:
        """ ends a session for a user """

        person = self._last_sender
        if not self.sessions.has_running_session(person):
            return ChannelMessage(channel, 'No session running.')

        self.sessions.end_session(person)
        self.sessions.save_to_file(self.session_file)

        entry = self.sessions.get_entry(person)

        message = f'Ended a session for the user <@{person}>. They said the following:\n'
        message += '\n'.join(entry['messages'])
        return ChannelMessage(entry['channel'], message)