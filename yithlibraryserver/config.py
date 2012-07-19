import os


def read_setting_from_env(settings, key, default=None):
    if key in settings and settings:
        return settings.get(key, default)
    else:
        env_variable = key.upper()
        return os.environ.get(env_variable, default)
