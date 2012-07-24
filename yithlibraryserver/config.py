import logging
import os


log = logging.getLogger(__name__)


def read_setting_from_env(settings, key, default=None):
    env_variable = key.upper()
    if env_variable in os.environ:
        log.debug('Setting %s found in the environment: %s' %
                  (key, os.environ[env_variable]))
        return os.environ[env_variable]
    else:
        log.debug('Looking for setting %s in the selected .ini file: %s' %
                  (key, settings.get(key, default)))
        return settings.get(key, default)
