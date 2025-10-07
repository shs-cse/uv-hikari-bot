import hikari
from bot_environment import state
from bot_environment.config import InfoKey, FacultyGuild, RoleName, ChannelName
from setup_validation.toml_inputs import update_info_key
from wrappers.utils import FormatText
from wrappers.discord import fetch_guild_from_id, get_channel_by_name
from wrappers.discord import update_guild_cache, fetch_invite_link


async def now(e: hikari.StartedEvent) -> None:
    print(FormatText.wait("Syncing initialization..."))
    # fetch course server
    this_guild_id = int(state.info[InfoKey.GUILD_ID])
    state.guild = await fetch_guild_from_id(e, this_guild_id)
    state.eee_guild = await fetch_guild_from_id(e, FacultyGuild.Id)
    # update cache of list of members, roles and channels
    await update_guild_cache()
    await update_guild_cache(state.eee_guild, True, False, False)
    # check if bot has @bot role
    bot_mem = state.guild.get_my_member()
    if bot_mem.get_top_role().name != RoleName.BOT:
        log = f"Bot was not assigned @{RoleName.BOT} role.\n  Please add"
        log += f" @{RoleName.BOT} role to {bot_mem} before proceeding."
        log = FormatText.error(log)
        raise hikari.HikariError(log)
    else:
        log = FormatText.bold(f"@{RoleName.BOT}")
        log = f"Bot Role: {log} has been added by admin."
        print(FormatText.status(log))
    # create invite link from welcome channel if not found
    if not state.info[InfoKey.INVITE_LINK]:
        welcome = get_channel_by_name(ChannelName.WELCOME)
        invite = await fetch_invite_link(welcome)
        update_info_key(InfoKey.INVITE_LINK, str(invite))
    log = FormatText.bold(state.info[InfoKey.INVITE_LINK])
    print(FormatText.status(f"Invite Link: {log}"))
    print(FormatText.success("Syncing initialization complete."))
