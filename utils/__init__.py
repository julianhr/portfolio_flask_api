def sanitize_param_num(request, key: str, default: int, min_num: int, max_num: int):
    try:
        args_num = int(request.args.get(key, default))
        return max(min(args_num, max_num), min_num)
    except Exception as error:
        return default
