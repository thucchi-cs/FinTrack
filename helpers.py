def format_usd(num):
    if ((type(num) != int) and (type(num) != float)):
        return num
    return f'$%0.2f' % float(num)
