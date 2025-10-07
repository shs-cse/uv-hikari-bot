import hikari, crescent, miru
import hikari.errors
from bot_environment import state
from bot_environment.config import InfoKey, FilePath, PluginFileName
import warnings
from setup_validation.toml_inputs import check_and_load_info
from wrappers.utils import FormatText


def main() -> None:
    # ignore pygsheets warnings in normal mode
    if __debug__:
        print(FormatText.warning("Code is running in debug mode."))
    else:
        warnings.simplefilter("ignore")
    # validate and update state.info
    check_and_load_info()
    # hikari + crescent -> create bot and client
    bot = hikari.GatewayBot(
        state.info[InfoKey.BOT_TOKEN],
        intents=hikari.Intents.ALL,
        logs="INFO" if __debug__ else "WARNING",
    )
    this_guild_id = int(state.info[InfoKey.GUILD_ID])
    client = crescent.Client(bot, default_guild=this_guild_id)
    client.plugins.load_folder(PluginFileName.EVENTS_FOLDER)
    client.plugins.load_folder(PluginFileName.COMMANDS_FOLDER)
    if __debug__:
        client.plugins.load_folder(PluginFileName.DEBUG_COMMANDS_FOLDER)
    # initialize miru for managing buttons and forms
    state.miru_client = miru.Client(bot)
    # run the bot
    try:
        bot.run(
            # enable asyncio debug to detect blocking and slow code.
            asyncio_debug=__debug__,
            # enable coroutine tracking, makes some asyncio errors clearer.
            coroutine_tracking_depth=20 if __debug__ else None,
            # initial discord status of the bot
            status=hikari.Status.IDLE,
        )
    except hikari.errors.UnauthorizedError as autherror:
        log = FormatText.error(
            "Bot authorization failed. Please check "
            + f"{FilePath.INFO_TOML} > '{InfoKey.BOT_TOKEN}'"
        )
        raise Exception(log) from autherror


if __name__ == "__main__":
    main()
