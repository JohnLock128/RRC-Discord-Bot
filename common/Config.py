from dataclasses import dataclass


# TODO Use `configparser` to create config from .ini or etc.
@dataclass(frozen=True)
class Config:
    """
    Class containing the Discord bot's configuration information.

    This class stores various configuration settings required to run the bot,
    including the Discord bot token, server-specific details, mod-mail settings,
    external integration tokens, and feature flags.
    """

    discord_token: str
    discord_guild_id: int
    modmail_role_id: int
    modmail_channel_id: int
    sendgrid_token: str
    sheet_name: str
    sheet_index: int
    enable_test_features: bool
