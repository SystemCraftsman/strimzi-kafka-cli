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
