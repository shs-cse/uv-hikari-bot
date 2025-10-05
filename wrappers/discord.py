import hikari
from bot_environment import state
from bot_environment.config import ClassType, RoleName, ChannelName, FacultyGuild
from wrappers.utils import FormatText

class DiscordClassTypeTemplate:
    def __init__(self, role: hikari.Role, 
                 category:hikari.GuildCategory, 
                 channels:list[hikari.PermissibleGuildChannel]) -> None:
        self.role = role
        self.category = category
        self.channels = channels
    


async def fetch_invite_link(event: hikari.StartedEvent,
                            channel: hikari.GuildTextChannel) -> str:
    invites = await event.app.rest.fetch_channel_invites(channel)
    for invite in invites:
        # infinite useage and infinite timelimit
        if invite.max_age is None and invite.max_uses is None:
            return str(invite)
    new_invite = await event.app.rest.create_invite(channel, max_age=0, max_uses=0)
    return str(new_invite)


def get_sec_role_name(section: int, class_type: ClassType) -> str:
    return RoleName.SECTION[class_type].format(section)


def get_sec_role(section: int, class_type: ClassType) -> hikari.Role:
    name = get_sec_role_name(section, class_type)
    role = get_role_by_name(name)
    ...  # TODO: sec template
    if section == 0 and not role:
        log = FormatText.bold("@" + name)
        log = FormatText.error(f"Template role {log} was not found.")
        raise Exception(log)
    return role


def get_sec_category_name(section: int, class_type: ClassType) -> str:
    return ChannelName.SECTION_CATEGORY[class_type].format(section)


def get_sec_category(section: int, class_type: ClassType) -> hikari.GuildCategory:
    name = get_sec_category_name(section, class_type)
    category = get_channel_by_name(name)
    ...  # TODO: sec template and check catergory dtype
    if section == 0 and not category:
        log = FormatText.bold("#" + name)
        log = FormatText.error(f"Template category {log} was not found.")
        raise Exception(log)
    if category is not None and not isinstance(category, hikari.GuildCategory):
        log = FormatText.bold("#" + name)
        log = FormatText.error(f"Category {log} is not a GuildCategory object.")
        raise Exception(log)
    return category


async def fetch_guild_from_id(event: hikari.StartedEvent,
                              guild_id: hikari.Snowflakeish) -> hikari.Guild | None:
    guild_hint = "ECT-BC" if guild_id == FacultyGuild.Id else "Course"
    try:
        guild = await event.app.rest.fetch_guild(guild_id)
        log = f"{guild_hint} Server: {FormatText.BOLD}{guild}{FormatText.RESET}"
        print(FormatText.status(log))
        return guild
    except hikari.NotFoundError as error:
        bot_acc = await event.app.rest.fetch_my_user()
        log = f"Could not reach the {guild_hint} server. \n  Have you added this bot"
        log += f" ({bot_acc} {bot_acc.mention}) in the {guild_hint} server?"
        log = FormatText.error(log)
        raise hikari.HikariError(log) from error


# cache get methods by using fetch methods occasionally
async def update_guild_cache(
    event: hikari.StartedEvent,
    guild: hikari.Guild | None = None,
    members: bool = True,
    roles: bool = True,
    channels: bool = True,
) -> None:
    if not guild:
        guild = state.guild
    print(FormatText.wait("Updating guild data cache..."))
    if members:
        await event.app.rest.fetch_members(guild)
    if roles:
        await event.app.rest.fetch_roles(guild)
    if channels:
        await event.app.rest.fetch_guild_channels(guild)
    print(FormatText.success(f"Cache Updated: {FormatText.bold(guild)} guild's data"))


# search in list of guild channels by name
def get_channel_by_name(name: str) -> hikari.PermissibleGuildChannel | None:
    for _, channel in state.guild.get_channels().items():
        if channel.name.lower() == name.lower():
            log = FormatText.bold("#" + name)
            print(FormatText.status(f"Fetched Channel: {log}"))
            return channel


# search in list of guild roles by name
def get_role_by_name(name: str) -> hikari.Role | None:
    for _, role in state.guild.get_roles().items():
        if role.name.lower() == name.lower():
            log = FormatText.bold("@" + name)
            print(FormatText.status(f"Fetched Role: {log}"))
            return role


# async def fetch_member_by_id(guild: hikari.Guild, id_or_user: hikari.Snowflakeish):
#     await event.app.rest.fetch_member(guild, id_or_user)
