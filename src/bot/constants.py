from aiogram import types
from aiogram.utils.i18n import lazy_gettext as __

from src.config import bot_settings

instructions_url = "https://innohassle.ru/music-room/instructions"
how_to_get_url = "https://www.youtube.com/watch?v=mGfdun8ah3g"
tg_chat_url = "https://t.me/joinchat/DjhyZkBN-FmZStxTB40qwQ"
bot_name = "Music Room Bot" if bot_settings.environment == "production" else "[dev] Music Room Bot"
bot_description = "Book a music room in the Innopolis Sport Complex. Made by @one_zero_eight"
bot_short_description = "Book a music room in the Innopolis Sport Complex. Made by @one_zero_eight"
bot_commands = [
    types.BotCommand(command="/start", description="Start the bot (register)"),
    types.BotCommand(command="/menu", description="Open the menu"),
    types.BotCommand(command="/help", description="Get help"),
    types.BotCommand(command="/create_booking", description="Create a booking"),
    types.BotCommand(command="/my_bookings", description="Show your bookings"),
    types.BotCommand(command="/image_schedule", description="Show the image with bookings"),
]
admin_commands = [
    types.BotCommand(command="/admin", description="Enable admin mode"),
    types.BotCommand(command="/export_users", description="Export users in docx format"),
    types.BotCommand(command="/change_status", description="Change status of a user"),
]

rules_message = __(
    "After you have crossed the threshold of the room, you must follow the rules described below. In case of "
    "non-compliance, you would be permanently banned from the music room and all corresponding resources.\n\n"
    "🚫 Do not remove property from the room.\n"
    "🚫 Do not bring any food and/or drinks into the room. In case you really need to eat or drink, you can do it "
    "outside the room.\n"
    "🚫 Don't leave trash in the room. There is no trash bin in the room, the nearest one is located right at the "
    "entrance of the sports complex.\n"
    "🚫 Do not fix instruments if they are broken (including broken strings on guitars). It's better to report this "
    "in the chat so that the technician can repair them in the future.\n"
    "⚠️ If you don't know how to tune the instrument, don't do it yourself. Find someone who knows and ask him/her "
    "to teach or help you with it.\n"
    "⚠️ Unnecessarily, do not move the equipment.\n"
)
rules_confirmation_message = __("I agree to and will abide by the stated rules.")

ban_message = __(
    "You are banned and can't book the music room. In case you believe it's a mistake, please contact: @Leon_Parepko"
)

create_booking_message = __("Create a booking")
create_booking_message_en = "Create a booking"
my_bookings_message = __("My bookings")
my_bookings_message_en = "My bookings"
image_schedule_message = __("Show the image with bookings")
image_schedule_message_en = "Show the image with bookings"

DIALOG_I18N_FORMAT_KEY = "dialog_i18n_format"
