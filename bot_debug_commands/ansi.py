import hikari, crescent
import urllib.parse
from bot_environment.config import RolePermissions
from wrappers.utils import FormatText

# https://gist.github.com/kkrypt0nn/a02506f3712ff2d1c8ca7c9e0aed7c06

plugin = crescent.Plugin[hikari.GatewayBot, None]()

ansi_group = crescent.Group("ansi", default_member_permissions=RolePermissions.ADMIN)


@plugin.include
@ansi_group.child
@crescent.command(name="color")
async def test_ansi_color(ctx: crescent.Context) -> None:
    log = "```ansi\n"
    log += "\u001b[1;30mExample\u001b[0;0m \u001b[1;31mExample\u001b[0;0m \u001b[1;32mExample\u001b[0;0m \u001b[1;33mExample\u001b[0;0m \u001b[1;34mExample\u001b[0;0m \u001b[1;35mExample\u001b[0;0m \u001b[1;36mExample\u001b[0;0m \u001b[1;37mExample\u001b[0;0m"
    log += "\n```"
    await ctx.respond(log)


@plugin.include
@ansi_group.child
@crescent.command(name="test")
async def test(ctx: crescent.Context) -> None:
    log = f"{ctx.member.mention} Here is a breakdown of your marks."
    link = f"https://discord.com/channels/{ctx.guild.id}/{ctx.channel.id}"
    embed = hikari.Embed(
        description=f"## Final\n## \u200b\u2001[**10**]({link})\u2001*out of*\u200150",
    )
    embed.add_field(
        name="Breakdown 1", value=f"\u200b\u2001\u2001[**2**]({link})\u2001*out of*\u200120"
    )
    embed.add_field(
        name="Breakdown 2", value=f"\u200b\u2001\u2001[**8**]({link})\u2001*out of*\u200130"
    )
    embed.set_footer(text="2145345\u2001Name Abcd", icon=hikari.UnicodeEmoji("#️⃣"))
    embed.color = 0xFF051A
    await ctx.respond(log, embed=embed, ephemeral=True)


@plugin.include
@crescent.message_command(name="Show Embed Url", default_member_permissions=RolePermissions.ADMIN)
async def show_embed_url(ctx: crescent.Context, message: hikari.Message) -> None:
    embed = message.embeds[0]
    col = urllib.parse.unquote(embed.url)
    col = col[len("https://dummy.url/") :]
    await ctx.respond(col, ephemeral=True)
