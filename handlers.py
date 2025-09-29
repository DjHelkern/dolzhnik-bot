import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import db

HELP_TEXT = """
*Список доступных команд:*
/add `фамилия` `что взял` - Добавить новый долг.
_Пример: `/add иванов дрель`_

/show `фамилия` - Показать долги конкретного человека и кнопки для удаления.
_Пример: `/show иванов`_

/show - Показать общий список всех должников.

/del `фамилия` `что вернул` - Удалить конкретный долг по названию.
_Пример: `/del иванов дрель`_

/help - Показать это сообщение.
"""


def register_handlers(bot: telebot.TeleBot):
    """Регистрирует все обработчики для бота."""

    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        bot.send_message(message.chat.id, HELP_TEXT, parse_mode='Markdown')

    @bot.message_handler(commands=['add'])
    def add_handler(message):
        try:
            _, name, *item_parts = message.text.split()
            item = " ".join(item_parts)
            db.add_debt(name, item)
            bot.reply_to(
                message, f"✅ Записал: {name.capitalize()} взял(а) '{item}'.")
        except ValueError:
            bot.reply_to(
                message, "❌ Неверный формат. Используйте: `/add фамилия что_взял`")

    @bot.message_handler(commands=['show'])
    def show_handler(message):
        args = message.text.split(maxsplit=1)
        if len(args) > 1:
            # Показываем долги конкретного человека
            name = args[1]
            debts = db.get_debts_by_name(name)
            if not debts:
                bot.send_message(
                    message.chat.id, f"🤷‍♂️ У '{name.capitalize()}' нет долгов.")
                return

            markup = InlineKeyboardMarkup()
            response_text = f"*{name.capitalize()}* должен(на):\n\n"
            for debt_id, item in debts:
                response_text += f"– {item}\n"
                button = InlineKeyboardButton(
                    f"❌ Вернул(а) '{item}'", callback_data=f"del_{debt_id}")
                markup.add(button)

            bot.send_message(message.chat.id, response_text,
                             reply_markup=markup, parse_mode='Markdown')

        else:
            # Показываем общий список
            all_debts = db.get_all_debts()
            if not all_debts:
                bot.send_message(message.chat.id, "🎉 Список должников пуст!")
                return

            response_text = "*Общий список должников:*\n\n"
            for name, items in all_debts.items():
                response_text += f"*{name.capitalize()}:*\n"
                for item in items:
                    response_text += f"  – {item}\n"
                response_text += "\n"

            bot.send_message(message.chat.id, response_text,
                             parse_mode='Markdown')

    @bot.message_handler(commands=['del'])
    def delete_command(message):
        try:
            _, name, *item_parts = message.text.split()
            item = " ".join(item_parts)

            debts = db.get_debts_by_name(name)
            for debt_id, debt_item in debts:
                if debt_item.lower() == item.lower():
                    db.delete_debt_by_id(debt_id)
                    bot.reply_to(
                        message, f"✅ Долг '{item}' у {name.capitalize()} удалён.")
                    return

            bot.reply_to(
                message, f"❌ Не найден долг '{item}' у {name.capitalize()}.")
        except ValueError:
            bot.reply_to(
                message, "❌ Неверный формат. Используйте: `/del фамилия что_вернул`")

    @bot.callback_query_handler(func=lambda call: call.data.startswith('del_'))
    def delete_callback(call):
        try:
            debt_id = int(call.data.split('_')[1])
            if db.delete_debt_by_id(debt_id):
                bot.answer_callback_query(call.id, "✅ Долг удален!")
                # Обновляем сообщение, убирая из него клавиатуру и добавляя пометку
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=f"{call.message.text}\n\n_(Один из долгов погашен)_",
                    reply_markup=None,
                    parse_mode='Markdown'
                )
            else:
                bot.answer_callback_query(
                    call.id, "❌ Ошибка: долг уже удален.")
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=f"{call.message.text}\n\n_(Этот долг уже был удален ранее)_",
                    reply_markup=None,
                    parse_mode='Markdown'
                )
        except Exception as e:
            print(f"Error in delete_callback: {e}")
            bot.answer_callback_query(call.id, "❌ Произошла ошибка.")
