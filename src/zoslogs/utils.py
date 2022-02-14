import datetime


def julian_to_datetime(input_string: str):
    """

    :param: input_string String to be converted
    :rtype: datetime object
    """
    if len(input_string) == 5:

        date = datetime.datetime.strptime(input_string, '%y%j')

    elif len(input_string) == 7:

        date = datetime.datetime.strptime(input_string, '%Y%j')
    else:
        raise UtilityException("Incorrect parameter length passed to "
                               "julian_to_datetime")

    return date


class UtilityException(Exception):
    pass
