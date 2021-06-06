import re


def convert_string_to_type(str_val):
    str_val = str(str_val)
    if str_val.isdigit():
        return int(str_val)
    elif is_number(str_val):
        return float(str_val)
    elif is_bool(str_val):
        return convert_string_to_boolean(str_val)
    else:
        return str_val


def is_number(str_val):
    try:
        float(str_val)
    except ValueError:
        return False
    return True


def is_bool(str_val):
    if str_val == 'true' or str_val == 'false':
        return True
    else:
        return False


def convert_string_to_boolean(str_val):
    if str_val == 'true':
        return True
    else:
        return False


def snake_to_camel_case(snake_str):
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def get_list_by_split_string(str_val, split_char):
    # TODO: exception here
    return str_val.split(split_char)


def is_valid_url(url):
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    return re.match(regex, url) is not None

