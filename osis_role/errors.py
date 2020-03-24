from functools import wraps


def clear_cached_error_perms(user_obj, perm):
    if hasattr(user_obj, '_cached_error_perms'):
        user_obj._cached_error_perms[perm] = None


def get_permission_errors(user_obj, perm):
    if hasattr(user_obj, '_cached_error_perms') and perm in user_obj._cached_error_perms:
        return user_obj._cached_error_perms[perm]
    return None


def set_permission_error(user_obj, perm, error):
    if not hasattr(user_obj, '_cached_error_perms'):
        setattr(user_obj, '_cached_error_perms', {})
    user_obj._cached_error_perms[perm] = error


def predicate_failed_msg(message=None):
    def predicate_decorator(func):
        @wraps(func)
        def wrapped_function(*args, **kwargs):
            result = func(*args, **kwargs)
            if not result:
                perm_name = args[0].context['perm_name']
                user_obj = args[1]
                set_permission_error(user_obj, perm_name, message)
            return result
        return wrapped_function
    return predicate_decorator
