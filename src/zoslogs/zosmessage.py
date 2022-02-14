import logging
import datetime


class ZosMessage():

    def __init__(self, text_to_parse: list, message_filters: dict = None):
        """

        :param text_to_parse: a list of one or more lines to parse
        :param message_filters:  messages to filter on; if filters are
        specified, and the message doesn't meet the filter requirements,
        raise a MessageFilter exception
        :param loglevel: the log level
        """

        log = logging.getLogger(__name__)

        self.record_type: str = None
        self.request_type: str = None
        self.routing_codes: str = None
        self.julian_date: int = None
        self.time: str = None
        self.date_time: datetime = None
        self.sysname: str = None
        self.console_id: str = None
        self.job_id: str = None
        self.user_exit_mpf_flags: str = None

        self.message: str = None
        self.message_id: str = None

        if isinstance(text_to_parse, str):
            first_line = text_to_parse
            rest_of_message = None
        elif isinstance(text_to_parse, list):
            first_line = text_to_parse[0]
            rest_of_message = text_to_parse[1:]

        self.record_type = first_line[0]
        self.request_type = first_line[1]

        self.routing_codes = first_line[2:9]
        self.sysname = first_line[10:18].rstrip()

        self.julian_date = first_line[19:24]
        self.time = first_line[25:36]

        self.user_exit_mpf_flags = first_line[46:54]

        self.message = first_line[56:]

        # Single Line Command Issued by operator
        if self.record_type == "N" and self.request_type == "C":
            self.console_id = first_line[37:45].rstrip()

        # Single Line Internal Message
        if self.record_type == "N" and (self.request_type == "I" or self.request_type == ' ')\
           or self.record_type == "X":
            self.job_id = first_line[37:45].rstrip()

            try:
                self.message_id = self.message.split()[0]
            except IndexError as e:
                log.error("Problem determining message id for line " + text_to_parse)
                raise MessageException("Problem determining message id for line " +
                                       text_to_parse) from e

        if self.record_type == "M" and (self.request_type == " "):
            self.job_id = first_line[37:45]
            try:
                self.message_id = self.message.split()[0]
            except IndexError as e:
                log.error("Problem determining message id for line " + str(text_to_parse))
                raise MessageException("Problem determining message id for line " +
                                       str(text_to_parse)) from e

            message_num = first_line.split()[-1]

            try:
                assert message_num.isnumeric()
            except AssertionError as e:
                raise MessageException("Error parsing " + str(text_to_parse) +
                                       "Missing message number") from e

            self.message = self.message.rpartition(message_num)[0].rstrip() + "\n"

        if message_filters is not None:
            if 'message_ids_to_include' in message_filters:
                if self.message_id not in message_filters['message_ids_to_include']:
                    raise FilterException

        if rest_of_message:
            for line in rest_of_message:

                if len(line) > 56:
                    self.message += line[56:]
                else:
                    self.message += '\n'

        if message_filters is not None:
            if 'message_contains' in message_filters:
                if any(filter_item in self.message for filter_item in
                       message_filters["message_contains"]):
                    pass
                else:
                    raise FilterException

    def __str__(self):
        return ' '.join((self.julian_date, self.time, self.sysname.ljust(8),
                         self.message)).rstrip()


class FilterException(Exception):
    pass


class MessageException(Exception):
    pass
