import hikari
from bot_environment import state
from bot_environment.config import ClassType
from wrappers.discord import get_sec_role, get_sec_role_name
from wrappers.discord import DiscordClassTypeTemplate, get_sec_category, get_sec_category_name
from wrappers.utils import FormatText


# check if all sections' roles and channels are in server
async def check_or_create_discord_sec(event: hikari.StartedEvent) -> None:
    # iterate over available theory & lab sections
    for class_type in ClassType.ALL:
        for sec in state.available_secs:
            role = get_sec_role(sec, class_type)
            if sec not in state.sec_roles:
                state.sec_roles[sec] = {}
            state.sec_roles[sec][class_type] = role
            if role is None:
                role = await create_sec_role(event, sec, class_type)
            category = get_sec_category(sec, class_type)
            if category is None:
                category = await create_sec_category(sec, class_type, role)


async def create_sec_role(
    event: hikari.StartedEvent, section: int, class_type: ClassType
) -> hikari.Role:
    template_role = get_sec_role(0, class_type)
    role_name = get_sec_role_name(section, class_type)
    new_role = await create_role_from_template(event, role_name, template_role)
    return new_role


# clone role with new name
async def create_role_from_template(
    event: hikari.StartedEvent, role_name: str, template_role: hikari.Role
) -> hikari.Role:
    log = FormatText.bold("@" + role_name)
    print(FormatText.warning(f"Creating {log} role..."))
    new_role = await event.app.rest.create_role(
        state.guild,
        name=role_name,
        permissions=template_role.permissions,
        color=template_role.color,
    )
    print(FormatText.success(f"Created {log} role successfully."))
    return new_role


async def create_sec_category(
    section: int, class_type: ClassType, new_role: hikari.Role
) -> hikari.PermissibleGuildChannel:
    # fetch template from section 0 if not cached
    if class_type not in state.sec_template:
        load_sec_template(class_type)
    # clone category with permissions
    category_name = get_sec_category_name(section, class_type)
    new_category = await create_channel_from_template(
        category_name,
        new_role,
        state.sec_template[class_type].category,
        state.sec_template[class_type].role,
    )
    # clone channels under template category
    for template_channel in state.sec_template[class_type].channels:
        await create_channel_from_template(
            template_channel.name,
            new_role,
            template_channel,
            state.sec_template[class_type].role,
            new_category,
        )
    return new_category


def load_sec_template(class_type: ClassType) -> None:
    template_role = get_sec_role(0, class_type)
    template_category = get_sec_category(0, class_type)
    # update state variable
    state.sec_template[class_type] = DiscordClassTypeTemplate(
        role=template_role,
        category=template_category,
        channels=[
            channel
            # for _, channel in state.guild.get_channels().items()
            for channel in state.guild.get_channels().values()
            if channel.parent_id == template_category.id
        ],
    )


# clone category with new name
async def create_channel_from_template(
    new_channel_name: str,
    new_role: hikari.Role,
    template_channel: hikari.PermissibleGuildChannel,
    template_role: hikari.Role,
    parent_category: hikari.GuildCategory = None,
) -> hikari.PermissibleGuildChannel:
    log = FormatText.bold("#" + new_channel_name)
    if template_channel.type == hikari.ChannelType.GUILD_CATEGORY:
        log += " category"
        print(FormatText.warning(f"Creating {log}..."))
    else:
        log += " channel"
        print(FormatText.status(f"Creating {log}..."))

    # create channel function to use
    create_channel_func_dict = {
        hikari.ChannelType.GUILD_CATEGORY: state.guild.create_category,
        hikari.ChannelType.GUILD_VOICE: state.guild.create_voice_channel,
        hikari.ChannelType.GUILD_TEXT: state.guild.create_text_channel,
    }
    create_channel_func = create_channel_func_dict[template_channel.type]
    new_channel: hikari.PermissibleGuildChannel = await create_channel_func(
        name=new_channel_name, permission_overwrites=template_channel.permission_overwrites.values()
    )
    await new_channel.edit(parent_category=parent_category)

    # copy permission overwrite from template to new role
    permission_overwrite = new_channel.permission_overwrites[template_role.id]
    await new_channel.remove_overwrite(template_role.id)
    await new_channel.edit_overwrite(
        new_role, allow=permission_overwrite.allow, deny=permission_overwrite.deny
    )
    if template_channel.type == hikari.ChannelType.GUILD_CATEGORY:
        print(FormatText.success(f"Created {log} successfully."))
    return new_channel
