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

        current_line = next(text_stream)

        for next_line in tqdm(text_stream, disable=disable_tqdm,
                         desc="Processing messages", leave=False):

            logger.debug(current_line)
            logger.debug(next_line)

            # Syslog starts with a leading space; Operlog doesn't.  So, we'll drop leading spaces.
            # Try to discard any characters I don't know what to do with
            # (Problem if using an older version of operlog dump program)

            current_line = current_line.encode("ascii", errors="ignore").decode().lstrip()

            if len(current_line) == 0:
                current_line = next_line
                continue

            # Can happen when a virtual page is created by syslog
            try:
                if current_line[0].isdigit():
                    current_line = current_line[1:]

                # Next page
                elif current_line[0] == "+":
                    current_line = next_line
                    continue

                # Continuation of a prior line
                elif current_line[0] == "S":
                    current_line = next_line
                    continue

            except IndexError:
                current_line = next_line
                continue


            next_line = next_line.encode("ascii", errors="ignore").decode().lstrip()

            try:
                if next_line[0].isdigit():
                    next_line = next_line[1:]

                # nextline is a continuation of current current_line
                if next_line[0] == "S":
                    current_line = current_line.rstrip() + " " + next_line[1:].lstrip()
            except IndexError:
                pass

            new_message = None

            # Single Line message or Syslog initialization message
            if current_line[0] == "N" or current_line[0] == "X":

                try:
                    new_message = ZosMessage(current_line, message_filters=message_filters)
                except FilterException:
                    current_line = next_line
                    continue
                except MessageException as e:
                    if halt_on_errors:
                        raise e
                    else:
                        logger.exception(e)

            # Multiline message Start
            elif current_line[0] == "M":

                multiline_id = current_line.split()[-1]

                try:
                    assert multiline_id.isnumeric()
                except AssertionError as e:
                    logger.warning("Got multiline id of " + str(multiline_id))
                    logger.warning(current_line)
                    if halt_on_errors:
                        raise e

                messages[multiline_id] = [current_line]

            # Multiline data or list
            elif current_line[0] == "D" or current_line[0] == "L":

                multiline_id = current_line[42:45]

                try:
                    messages[multiline_id].append(current_line)
                except KeyError as e:
                    error_message = ("Trying to append data to multiline message " + multiline_id +
                                     " with no such message header")
                    logger.warning(error_message)
                    if halt_on_errors:
                        raise MessageException(error_message) from e

            # Multiline end
            elif current_line[0] == "E":

                multiline_id = current_line[42:45]

                try:
                    messages[multiline_id].append(current_line)
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
                    current_line = next_line
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
                               "type " + current_line[0] + "\n" + current_line)
                logger.warning("Skipping")

            if new_message:
                self.message_list.append(new_message)

            current_line = next_line

        else:

            logger.debug(current_line)

            new_message = None

            # Syslog starts with a leading space; Operlog doesn't.  So, we'll drop leading spaces.
            # Try to discard any characters I don't know what to do with
            # (Problem if using an older version of operlog dump program)

            current_line = current_line.encode("ascii", errors="ignore").decode().lstrip()


            if len(current_line) == 0:
                pass
            else:
                # Can happen when a virtual page is created by syslog
                if current_line[0].isdigit():
                    current_line = current_line[1:]

                # Next page
                if current_line[0] == "+":
                    pass

                elif current_line[0] == "S":
                  pass

                else:

                    # Single Line message or Syslog initialization message
                    if current_line[0] == "N" or current_line[0] == "X":

                        try:
                            new_message = ZosMessage(current_line, message_filters=message_filters)
                        except FilterException:
                            pass
                        except MessageException as e:
                            if halt_on_errors:
                                raise e
                            else:
                                logger.exception(e)

                    # Multiline message Start
                    elif current_line[0] == "M":

                        multiline_id = current_line.split()[-1]

                        try:
                            assert multiline_id.isnumeric()
                        except AssertionError as e:
                            logger.warning("Got multiline id of " + str(multiline_id))
                            logger.warning(current_line)
                            if halt_on_errors:
                                raise e

                        messages[multiline_id] = [current_line]

                    # Multiline data or list
                    elif current_line[0] == "D" or current_line[0] == "L":

                        multiline_id = current_line[42:45]

                        try:
                            messages[multiline_id].append(current_line)
                        except KeyError as e:
                            error_message = ("Trying to append data to multiline message " + multiline_id +
                                             " with no such message header")
                            logger.warning(error_message)
                            if halt_on_errors:
                                raise MessageException(error_message) from e

                    # Multiline end
                    elif current_line[0] == "E":

                        multiline_id = current_line[42:45]

                        try:
                            messages[multiline_id].append(current_line)
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
                            pass
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
                                       "type " + current_line[0] + "\n" + current_line)
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

    def __process_current(self, current_line):
        pass

    def __len__(self):
        return len(self.message_list)

    def __yield__(self):
        return self

    def __next__(self):
        return (self.message_list.pop())

    def __getitem__(self, item):
        return (self.message_list[item])
