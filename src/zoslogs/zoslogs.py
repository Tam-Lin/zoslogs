"""Main module."""

import logging

from tqdm import tqdm

from src.zoslogs.zosmessage import ZosMessage, MessageException, \
    FilterException


class ZosLogs():

    def __init__(self, text_stream, message_filters=None, halt_on_errors=False, disable_tqdm=None):
        """

        :param text_stream:  A text stream to break into messages
        :param message_filters:  A dictionary of filters
        :param halt_on_errors:  By default, the library will do its best to
                                parse the logs, and ignore anything it can't
                                understand.  If this is True, the library will
                                raise an exception if it has problems parsing
                                something, instead parsing what it does
                                understand
        :param disable_tqdm:  By default, the library will use tqdm to display
                              parsing progress when running interactively.  If
                              this is set to True, it won't display parsing
                              progress.
        """

        logger = logging.getLogger(__name__)

        self.message_list = list()

        messages = dict()

        # Going to loop through twice for now, to reduce complexity.
        # Thinking of a better way to handle this.

        cleaned_text_stream = list()

        logger.info("Cleaning text")

        for line in tqdm(text_stream, disable=disable_tqdm, desc="Cleaning text", leave=False):

            # Syslog starts with a leading space; Operlog doesn't.  So, we'll drop leading spaces.

            logger.debug(line)

            # Try to discard any characters I don't know what to do with
            # (Problem if using an older version of operlog dump program)
            line = line.encode("ascii", errors="ignore").decode().lstrip()

            if len(line) == 0:
                continue

            # Can happen when a virtual page is created by syslog
            if line[0].isdigit():
                line = line[1:]

            # Next page
            if line[0] == "+":
                continue

            # Continuation of prior line
            if line[0] == "S":
                try:
                    cleaned_text_stream[-1] = cleaned_text_stream[-1].rstrip() + " " + \
                                              line[1:].lstrip()
                except IndexError:
                    error = "Trying to add message to prior message, but there is no prior " \
                            "message\n" + line
                    if halt_on_errors:
                        raise MessageException(error)
                    else:
                        logger.error(error)

                continue

            cleaned_text_stream.append(line)

        logger.info("Processing cleaned lines")

        for line in tqdm(cleaned_text_stream, disable=disable_tqdm,
                         desc="Processing messages", leave=False):

            new_message = None

            # Single Line message or Syslog initialization message
            if line[0] == "N" or line[0] == "X":

                try:
                    new_message = ZosMessage(line, message_filters=message_filters)
                except FilterException:
                    continue
                except MessageException as e:
                    if halt_on_errors:
                        raise e
                    else:
                        logger.exception(e)

            # Multiline message Start
            elif line[0] == "M":

                multiline_id = line.split()[-1]

                try:
                    assert multiline_id.isnumeric()
                except AssertionError as e:
                    logger.warning("Got multiline id of " + str(multiline_id))
                    logger.warning(line)
                    if halt_on_errors:
                        raise e

                messages[multiline_id] = [line]

            # Multiline data or list
            elif line[0] == "D" or line[0] == "L":

                multiline_id = line[42:45]

                try:
                    messages[multiline_id].append(line)
                except KeyError as e:
                    error_message = ("Trying to append data to multiline message " + multiline_id +
                                     " with no such message header")
                    logger.warning(error_message)
                    if halt_on_errors:
                        raise MessageException(error_message) from e

            # Multiline end
            elif line[0] == "E":

                multiline_id = line[42:45]

                try:
                    messages[multiline_id].append(line)
                except KeyError as e:
                    logger.warning("Trying to append data to multiline message " + multiline_id +
                                   " with no such message header")
                    if halt_on_errors:
                        raise e

                try:
                    new_message = ZosMessage(messages[multiline_id],
                                             message_filters=message_filters)
                    messages.pop(multiline_id)
                except FilterException:
                    continue
                except MessageException as e:
                    logger.warning("Error parsing " + str(messages[multiline_id]))
                    if halt_on_errors:
                        raise e
                except KeyError as e:
                    logger.warning("Got a multiline ending " + multiline_id +
                                   " with no header")
                    if halt_on_errors:
                        raise e

            else:
                logger.warning("I don't know what to do with message record "
                               "type " + line[0] + "\n" + line)
                logger.warning("Skipping")

            if new_message:
                self.message_list.append(new_message)

        if len(messages) > 0:
            logger.warning("Have multiline messages I never saw an ending for")

        for message_id in messages:

            logger.warning(messages[message_id])

            try:
                new_message = ZosMessage(messages[message_id], message_filters=message_filters)
            except FilterException:
                continue
            except MessageException as e:
                logger.warning("Error parsing " + str(messages[message_id]))
                if halt_on_errors:
                    raise e
                else:
                    continue

            if new_message is not None:
                self.message_list.append(new_message)

    def __len__(self):
        return len(self.message_list)

    def __yield__(self):
        return self

    def __next__(self):
        return (self.message_list.pop())

    def __getitem__(self, item):
        return (self.message_list[item])
