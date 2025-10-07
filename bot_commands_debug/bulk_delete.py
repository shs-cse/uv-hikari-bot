import hikari, crescent, re
from bot_environment import state
from bot_environment.config import RolePermissions, ChannelName, ClassType
from wrappers.utils import FormatText

plugin = crescent.Plugin[hikari.GatewayBot, None]()
# admin ang higher level access only
delete_group = crescent.Group("delete", default_member_permissions=RolePermissions.ADMIN)
# bulk subgroup
bulk_subgroup = delete_group.sub_group("bulk")


@plugin.include
@delete_group.child
@crescent.command(name="role")
class DeleteRole:
    role = crescent.option(hikari.Role)

    async def callback(self, ctx: crescent.Context) -> None:
        await ctx.defer(ephemeral=True)
        await delete_section_role(self.role)
        await ctx.respond("Check print log.", ephemeral=True)


async def delete_section_role(role: hikari.Role) -> None:
    if role not in state.all_sec_roles:
        print(FormatText.dim(f"Bulk Delete: {role.mention} is not a section role."))
        return
    print(FormatText.warning(f"Bulk Delete: deleting {role.mention} {role}..."))
    await plugin.app.rest.delete_role(state.guild, role)


@plugin.include
@delete_group.child
@crescent.command(name="category")
class DeleteCategory:
    category = crescent.option(hikari.GuildCategory)

    async def callback(self, ctx: crescent.Context) -> None:
        await ctx.defer(ephemeral=True)
        await delete_sec_category(self.category)
        await ctx.respond("Check print log.", ephemeral=True)


async def delete_sec_category(category: hikari.GuildCategory) -> None:
    if category.type != hikari.ChannelType.GUILD_CATEGORY:
        print(FormatText.dim(f"Bulk Delete: {category.name} is not a category."))
        return

    sec_category_names = [
        ChannelName.SECTION_CATEGORY[class_type].format(sec)
        for class_type in ClassType.ALL
        for sec in state.available_secs
    ]
    if category.name not in sec_category_names:
        print(FormatText.dim(f"Bulk Delete: {category.name} is not a section category."))
        return

    for _, channel in state.guild.get_channels().items():
        if channel.parent_id == category.id:
            print(FormatText.warning(f"Bulk Delete: deleting {channel.mention} {channel}..."))
            await channel.delete()
    print(FormatText.warning(f"Bulk Delete: deleting {category.mention} {category}..."))
    await category.delete()


@plugin.include
@bulk_subgroup.child
@crescent.command(name="roles", description="Bulk delete all section roles.")
class DeleteBulkRoles:
    BULK_DELETE_PROMPT = "yes"  # "Confirm bulk deletion!"
    confirm = crescent.option(str, f"Type in `{BULK_DELETE_PROMPT}` exactly to confirm.")

    async def callback(self, ctx: crescent.Context) -> None:
        await ctx.defer(ephemeral=True)
        if self.confirm == self.BULK_DELETE_PROMPT:
            for _, role in state.guild.get_roles().items():
                await delete_section_role(role)
            await ctx.respond("Check print log.", ephemeral=True)
        else:
            msg = "Confimation text did not match prompt:\n"
            msg += f"```diff\n+ {self.BULK_DELETE_PROMPT}\n"
            msg += f"- {self.confirm}\n```"
            await ctx.respond(msg, ephemeral=True)


@plugin.include
@bulk_subgroup.child
@crescent.command(name="categories", description="Bulk delete all section channels.")
class DeleteBulkCategories:
    BULK_DELETE_PROMPT = "yes"  # "Confirm bulk deletion!"
    confirm = crescent.option(str, f"Type in `{BULK_DELETE_PROMPT}` exactly to confirm.")

    async def callback(self, ctx: crescent.Context) -> None:
        await ctx.defer(ephemeral=True)
        if self.confirm == self.BULK_DELETE_PROMPT:
            for _, channel in state.guild.get_channels().items():
                await delete_sec_category(channel)
            await ctx.respond("Check print log.", ephemeral=True)
        else:
            msg = "Confimation text did not match prompt:\n"
            msg += f"```diff\n+ {self.BULK_DELETE_PROMPT}\n"
            msg += f"- {self.confirm}\n```"
            await ctx.respond(msg, ephemeral=True)
