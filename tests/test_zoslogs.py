#!/usr/bin/env python

"""Tests for `zoslogs` class."""

import fileinput
import pytest

from src.zoslogs import zoslogs
from src.zoslogs.zosmessage import MessageException


def test_single_line_message():
    with open('tests/test_data/single_line_message.txt') as file:

        log = zoslogs.ZosLogs(file)

    assert len(log) == 1

    assert log[0].record_type == 'N'
    assert log[0].request_type == ' '
    assert log[0].routing_codes == '4000000'
    assert log[0].sysname == 'S5A'
    assert log[0].julian_date == '22039'
    assert log[0].time == '00:01:00.55'
    assert log[0].user_exit_mpf_flags == '00000211'

    assert log[0].message == '$HASP373 LOGRSVT  STARTED - INIT 15   - CLASS Q        - SYS S5A\n'
    # assert log[0].message_id == '$HASP373'
    # assert log[0].jobid == 'J0126429'


def test_single_line_command():
    with open('tests/test_data/single_line_command.txt') as file:
        log = zoslogs.ZosLogs(file)

    assert log[0].record_type == 'N'
    assert log[0].request_type == 'C'
    assert log[0].routing_codes == '0000000'
    assert log[0].sysname == 'S5A'
    assert log[0].julian_date == '22039'
    assert log[0].time == '07:00:34.88'
    assert log[0].user_exit_mpf_flags == '00000210'
    assert log[0].console_id == 'INTERNAL'

    assert log[0].message == 'CANCEL   LOGRSVTS,A=0064\n'
    # assert log[0].jobname == 'J0126429'


def test_single_line_internal():
    with open('tests/test_data/single_line_internal.txt') as file:
        log = zoslogs.ZosLogs(file)

    assert log[0].record_type == 'N'
    assert log[0].request_type == 'I'
    assert log[0].routing_codes == '0000000'
    assert log[0].sysname == 'S5A'
    assert log[0].julian_date == '22039'
    assert log[0].time == '07:00:34.88'
    assert log[0].user_exit_mpf_flags == '00000210'
    assert log[0].console_id is None
    assert log[0].job_id == 'J0130811'

    assert log[0].message == '$CJ0130811,PURGE\n'
    # assert log[0].jobname == 'J0126429'


def test_message_with_continuation():
    with open('tests/test_data/single_line_with_continuation.txt') as file:

        logs = zoslogs.ZosLogs(file)

    assert logs[0].record_type == 'N'
    assert logs[0].request_type == ' '
    assert logs[0].routing_codes == '0004000'
    assert logs[0].sysname == 'S5A'
    assert logs[0].julian_date == '22039'
    assert logs[0].time == '07:00:06.11'
    assert logs[0].user_exit_mpf_flags == '00000210'

    assert logs[0].message == '-LOGRSVTS ENDED.  NAME-                     ' \
                              'TOTAL CPU TIME=   .00  TOTAL ELAPSED TIME=    .0\n'
    # assert log[0].jobname == 'J0126429'


def test_multi_line_message():
    with open('tests/test_data/multi_line.txt') as file:
        logs = zoslogs.ZosLogs(file)

    assert logs[0].record_type == 'M'
    assert logs[0].request_type == ' '
    assert logs[0].routing_codes == '0040000'
    assert logs[0].sysname == 'S5A'
    assert logs[0].julian_date == '22039'
    assert logs[0].time == '03:54:38.76'
    assert logs[0].user_exit_mpf_flags == '00000210'
    assert logs[0].job_id == 'J0120104'

    assert logs[0].message == 'IXL030I CONNECTOR STATISTICS FOR LOCK STRUCTURE COACMELCKIMS_1,\n' \
                              'CONNECTOR COACMELC0B000019:\n' \
                              '      00071011 00000000 00000062 00F0000F 000A\n' \
                              '\n' \
                              '      00000000 00000000 00000001 00000000\n' \
                              '      00000000 00000000 00000000 00000005\n' \
                              '      00000000 00000000 00000000 00000000\n' \
                              '      00000000 00000000 00000000 00000000\n' \
                              '\n' \
                              '      00000001 00000000 00000001 00000000\n' \
                              '      00000000 00000000 00000000 0000009D\n' \
                              '      00000000 00000000 00000000 00000000\n' \
                              '      00000000 00000000 00000000 00000000\n' \
                              '\n' \
                              '      00000002 00000000 00000001 00000000\n' \
                              '      00000000 00000000 00000000 00000065\n' \
                              '      00000000 00000000 00000000 00000000\n' \
                              '      00000000 00000000 00000000 00000000\n' \
                              '\n' \
                              '      00000003 00000000 00000000 00000000\n' \
                              '      00000000 00000000 00000000 00000000\n' \
                              '      00000000 00000000 00000000 00000000\n' \
                              '      00000000 00000000 00000000 00000000\n'


def test_multi_line_message_with_missing_message_header():
    with open('tests/test_data/multi_line_with_no_message_header.txt') as file:
        logs = zoslogs.ZosLogs(file)

    assert len(logs) == 1

    assert logs[0].record_type == 'M'
    assert logs[0].request_type == ' '
    assert logs[0].routing_codes == '0040000'
    assert logs[0].sysname == 'S5A'
    assert logs[0].julian_date == '22039'
    assert logs[0].time == '03:54:38.76'
    assert logs[0].user_exit_mpf_flags == '00000210'
    assert logs[0].job_id == 'J0120104'

    assert logs[0].message == 'IXL030I CONNECTOR STATISTICS FOR LOCK STRUCTURE COACMELCKIMS_1,\n' \
                              'CONNECTOR COACMELC0B000019:\n' \
                              '      00071011 00000000 00000062 00F0000F 000A\n' \
                              '\n' \
                              '      00000000 00000000 00000001 00000000\n' \
                              '      00000000 00000000 00000000 00000005\n' \
                              '      00000000 00000000 00000000 00000000\n' \
                              '      00000000 00000000 00000000 00000000\n' \
                              '\n' \
                              '      00000001 00000000 00000001 00000000\n' \
                              '      00000000 00000000 00000000 0000009D\n' \
                              '      00000000 00000000 00000000 00000000\n' \
                              '      00000000 00000000 00000000 00000000\n' \
                              '\n' \
                              '      00000002 00000000 00000001 00000000\n' \
                              '      00000000 00000000 00000000 00000065\n' \
                              '      00000000 00000000 00000000 00000000\n' \
                              '      00000000 00000000 00000000 00000000\n' \
                              '\n' \
                              '      00000003 00000000 00000000 00000000\n' \
                              '      00000000 00000000 00000000 00000000\n' \
                              '      00000000 00000000 00000000 00000000\n' \
                              '      00000000 00000000 00000000 00000000\n'


def test_multi_line_message_with_missing_message_header_and_halt():
    with open('tests/test_data/multi_line_with_no_message_header.txt') as file:
        with pytest.raises(MessageException):
            zoslogs.ZosLogs(file, halt_on_errors=True)


def test_multi_line_message_with_continuation():
    with open('tests/test_data/multi_line_with_continuation.txt') as file:
        logs = zoslogs.ZosLogs(file)

    assert logs[0].record_type == 'M'
    assert logs[0].request_type == ' '
    assert logs[0].routing_codes == '0000000'
    assert logs[0].sysname == 'S5A'
    assert logs[0].julian_date == '22039'
    assert logs[0].time == '09:03:08.10'
    assert logs[0].user_exit_mpf_flags == '00000210'
    assert logs[0].job_id == 'S0119482'


def test_multiple_messages():
    with fileinput.input(('tests/test_data/multi_line.txt',
                          'tests/test_data/single_line_with_continuation.txt',
                          'tests/test_data/single_line_internal.txt',
                          'tests/test_data/single_line_command.txt',
                          'tests/test_data/multi_line_with_continuation.txt')) \
                          as files:
        log = zoslogs.ZosLogs(files)

    assert len(log) == 5


def test_new_syslog_page():
    with fileinput.input(('tests/test_data/new_syslog_page.txt',
                          'tests/test_data/syslog_initialization_message.txt')) \
                        as files:
        log = zoslogs.ZosLogs(files)

    assert len(log) == 2


def test_multiple_messages_with_filters():
    filter = {"message_ids_to_include": ['IEE043I']}

    with fileinput.input(('tests/test_data/multiple_messages.txt')) as file:
        log = zoslogs.ZosLogs(file, message_filters=filter)

    assert len(log) == 1


def test_multiple_messages_with_filters_and_exception():
    filter = {"message_ids_to_include": ['IEE043I']}

    with fileinput.input(('tests/test_data/multiple_messages.txt',
                          'tests/test_data/multi_line_with_no_message_header.txt')) as file:
        log = zoslogs.ZosLogs(file, message_filters=filter)

    assert len(log) == 1


def test_multiple_messages_with_filters_and_exception_and_halt():
    filter = {"message_ids_to_include": ['IEE043I']}

    with fileinput.input(('tests/test_data/multiple_messages.txt',
                          'tests/test_data/multi_line_with_no_message_header.txt')) as file:
        with pytest.raises(MessageException):
            zoslogs.ZosLogs(file, message_filters=filter, halt_on_errors=True)
