"""
On this page is a single App Config which is to be used by all environments.

There are no separate configs for each environment (local, staging, prod,
etc). This is to remove the potential bug where config meant for one environment
(say prod) is accidentally used in a different environment (say local dev) due
to a typo or other human error.

Instead, the rules for providing config are simple:

1. Any values which are expected to change between deployment envs must not live
in the code base and are passed through environment variables only. Such as DB
connection strings and API keys.
2. Any values which are expected to be consistent throughout the deployment envs
can be defaulted if desired. These can be still provided through environment
variables, but the idea is that nothing bad will happen if somebody makes a typo
and the defaulted value is picked up by mistake.
"""
from __future__ import annotations

from pydantic_settings import BaseSettings


class AppConfig(BaseSettings):
    """
    The behaviour of pydantic's BaseSettings is that environment variables are
    checked for any keys not provided when instantiating the class. If no env var
    exists for a key then the default is used if provided.
    """

    # Must be provided by env vars
    SQLALCHEMY_DATABASE_URI: str
    SECRET_KEY: str

    # Expect same value for all envs so can be defaulted
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
