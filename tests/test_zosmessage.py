#!/usr/bin/env python

"""Tests for `zoslogs` zosmessage class."""

import pytest

from src.zoslogs import zosmessage


def test_single_line_message():
    with open('tests/test_data/single_line_message.txt') as file:
        line = file.readline()

        message = zosmessage.ZosMessage(line)

    assert message.record_type == 'N'
    assert message.request_type == ' '
    assert message.routing_codes == '4000000'
    assert message.sysname == 'S5A'
    assert message.julian_date == '22039'
    assert message.time == '00:01:00.55'
    assert message.user_exit_mpf_flags == '00000211'

    assert message.message == '$HASP373 LOGRSVT  STARTED - INIT 15   - CLASS Q        - SYS S5A\n'
    assert message.message_id == '$HASP373'
    # assert message.jobname == 'J0126429'


def test_single_line_command():
    with open('tests/test_data/single_line_command.txt') as file:
        line = file.readline()

        message = zosmessage.ZosMessage(line)

    assert message.record_type == 'N'
    assert message.request_type == 'C'
    assert message.routing_codes == '0000000'
    assert message.sysname == 'S5A'
    assert message.julian_date == '22039'
    assert message.time == '07:00:34.88'
    assert message.user_exit_mpf_flags == '00000210'
    assert message.console_id == 'INTERNAL'

    assert message.message == 'CANCEL   LOGRSVTS,A=0064\n'
    # assert message.jobname == 'J0126429'


def test_single_line_internal():
    with open('tests/test_data/single_line_internal.txt') as file:
        line = file.readline()

        message = zosmessage.ZosMessage(line)

    assert message.record_type == 'N'
    assert message.request_type == 'I'
    assert message.routing_codes == '0000000'
    assert message.sysname == 'S5A'
    assert message.julian_date == '22039'
    assert message.time == '07:00:34.88'
    assert message.user_exit_mpf_flags == '00000210'
    assert message.console_id is None
    assert message.job_id == 'J0130811'

    assert message.message == '$CJ0130811,PURGE\n'
    # assert message.jobname == 'J0126429'


def test_syslog_initilization():
    with open('tests/test_data/syslog_initialization_message.txt') as file:
        line = file.readline()

        message = zosmessage.ZosMessage(line)

    assert message.record_type == 'X'
    assert message.routing_codes == '0000000'
    assert message.sysname == 'S5A'
    assert message.julian_date == '21310'
    assert message.time == '00:00:01.81'
    assert message.user_exit_mpf_flags == '00000000'
    assert message.console_id is None
    assert message.job_id == 'SYSLOG'
    assert message.message_id == 'IEE042I'

    assert message.message == 'IEE042I SYSTEM LOG DATA SET INITIALIZED\n'


def test_multi_line_message():
    with open('tests/test_data/multi_line.txt') as file:
        lines = file.readlines()
        message = zosmessage.ZosMessage(lines)

    assert message.record_type == 'M'
    assert message.request_type == ' '
    assert message.routing_codes == '0040000'
    assert message.sysname == 'S5A'
    assert message.julian_date == '22039'
    assert message.time == '03:54:38.76'
    assert message.user_exit_mpf_flags == '00000210'
    assert message.job_id == 'J0120104'
    assert message.message_id == "IXL030I"

    assert message.message == 'IXL030I CONNECTOR STATISTICS FOR LOCK STRUCTURE COACMELCKIMS_1,\n' \
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


def test_empty_line():
    with open('tests/test_data/empty_line.txt') as file:
        line = file.readline()
        with pytest.raises(zosmessage.MessageException):
            zosmessage.ZosMessage(line)


def test_empty_multi_line():
    with open('tests/test_data/empty_multi_line.txt') as file:
        line = file.readline()
        with pytest.raises(zosmessage.MessageException):
            zosmessage.ZosMessage(line)


def test_single_line_messageid_filter_match():
    with open('tests/test_data/single_line_message.txt') as file:
        line = file.readline()

        filter = {"message_ids_to_include": ['$HASP373']}

        message = zosmessage.ZosMessage(line, message_filters=filter)

    assert message.record_type == 'N'
    assert message.request_type == ' '
    assert message.routing_codes == '4000000'
    assert message.sysname == 'S5A'
    assert message.julian_date == '22039'
    assert message.time == '00:01:00.55'
    assert message.user_exit_mpf_flags == '00000211'

    assert message.message == '$HASP373 LOGRSVT  STARTED - INIT 15   - CLASS Q        - SYS S5A\n'
    assert message.message_id == '$HASP373'


def test_single_line_message_contains_filter_match():
    with open('tests/test_data/single_line_message.txt') as file:
        line = file.readline()

        filter = {"message_contains": ['INIT 15']}

        message = zosmessage.ZosMessage(line, message_filters=filter)

    assert message.record_type == 'N'
    assert message.request_type == ' '
    assert message.routing_codes == '4000000'
    assert message.sysname == 'S5A'
    assert message.julian_date == '22039'
    assert message.time == '00:01:00.55'
    assert message.user_exit_mpf_flags == '00000211'

    assert message.message == '$HASP373 LOGRSVT  STARTED - INIT 15   - CLASS Q        - SYS S5A\n'
    assert message.message_id == '$HASP373'


def test_single_line_message_contains_message_id_and_message_filter_match():
    with open('tests/test_data/single_line_message.txt') as file:
        line = file.readline()

        filter = {"message_contains": ['INIT 15'],
                  "message_ids_to_include": ['$HASP373']}

        message = zosmessage.ZosMessage(line, message_filters=filter)

    assert message.record_type == 'N'
    assert message.request_type == ' '
    assert message.routing_codes == '4000000'
    assert message.sysname == 'S5A'
    assert message.julian_date == '22039'
    assert message.time == '00:01:00.55'
    assert message.user_exit_mpf_flags == '00000211'

    assert message.message == '$HASP373 LOGRSVT  STARTED - INIT 15   - CLASS Q        - SYS S5A\n'
    assert message.message_id == '$HASP373'


def test_single_line_messageid_filter_no_match():
    with open('tests/test_data/single_line_message.txt') as file:
        line = file.readline()

        filter = {"message_ids_to_include": ['$HASP374']}

        with pytest.raises(zosmessage.FilterException):
            zosmessage.ZosMessage(line, message_filters=filter)


def test_single_line_message_contains_filter_no_match():
    with open('tests/test_data/single_line_message.txt') as file:
        line = file.readline()

        filter = {"message_contains": ['INIT 16']}

        with pytest.raises(zosmessage.FilterException):
            zosmessage.ZosMessage(line, message_filters=filter)


def test_multi_line_message_no_messagenum():
    with open('tests/test_data/multi_line_no_messagenum.txt') as file:
        lines = file.readlines()
        with pytest.raises(zosmessage.MessageException):
            zosmessage.ZosMessage(lines)


def test_str():
    with open('tests/test_data/single_line_internal.txt') as file:
        line = file.readline()

        message = zosmessage.ZosMessage(line)

        assert str(message) == "22039 07:00:34.88 S5A      $CJ0130811,PURGE"
