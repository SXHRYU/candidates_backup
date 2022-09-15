from aiogram import Dispatcher, types

from authorization import auth
from bot_files import keyboards as kb
from tasks_metrics.to_handlers import generate_excel

# Handlers that don't use Finite State Machine (FSM),
# meaning these commands can be called independent of previous commands
# given that the caller has required rights and not in a FSM command.
async def show_menu_commands(message: types.Message):
    """Displays menu interface to the user.
    
    This can be invoked by typing either of "Меню" or "Menu".

    Returns
    -------
    Message : Awaitable
        Replies to user with the following message (<text>) and
        keyboard (<button>):
        <text>Меню
            <button>"Я новенький"
            <button>"Я уже разметчик"
            <button>"Помощь"

    Notes
    -----
    Everyone who has access to this bot can use any of these buttons.
    No checks are made which means bot is basically public.
    """
    await message.answer(
        "Меню",
        reply_markup=kb.menu_kb,
    )

async def get_help(message: types.Message):
    """Displays help message to the user.

    This can be invoked by typing either of the following:.
    "Help", "Помощь", "/start", "/help"

    Notes
    -----
    Everyone who has access to this bot can see this message.
    No checks are made which means bot is basically public.
    Catches all uncaught handlers.
    """
    await message.answer(
        # from `help.html`
        ("🤖<b>Бот для кандидатов-разметчиков в TrainingData.\n\n</b>"
            
            + "<u>Команды бота:</u>\n"
            + "➖<code>Меню</code>/<code>Menu</code> - команда для перехода в главное меню.\n\n"
            + "➖<code>Получить тестовое задание📄</code> - команда для тех, кто хочет зарегистрироваться для прохождения тестового задания.\n\n"
            + "➖<code>Тестовое задание выполнено☑️</code> - команда для тех, кто уже зарегистрировался и хочет отправить результаты.\n\n"
            + "➖<code>Повторить тестовое задание</code> - команда для тех, кто <b>уже выполнил</b> тестовое задание, но по какой-либо причине решил пройти его заново. "
                + "<b>Предупреждение:</b> запросить новое тестовое задание можно только один раз, и результаты выполнения будут смотреться по новому решению.\n\n"
            # + "💼<code>HR</code> - команда для HR.\n\n"
            + "❓<code>Помощь</code>/<code>Help</code> - команда для вывода данного сообщения.\n\n"

            + "<u>Тестовое задание</u>📄\n"
            + "Для понимания предстоящей работы и оценки своих сил Вам предлагается пройти небольшое тестовое задание по разметке данных, \
которое представляет из себя то, чем регулярно занимаются разметчики TrainingData. Проверяться будут точность и скорость, \
с которыми Вы справитесь с этим заданием. Если у Вас возникнут трудности или Вы захотите заново его пройти, \
не стесняйтесь написать HR. <b>Удачи!</b>"),
        parse_mode="HTML",
        reply_markup=kb.menu_kb,
    )

@auth
async def show_hr_commands(message: types.Message):
    """Displays HR menu interface to the HR.
    
    This can be invoked by "HR".

    Returns
    -------
    Message : Awaitable
        Replies to user with the following message (<text>) and
        keyboard (<button>):
        <text>Меню HR
            <button>"Посмотреть результаты кандидата"
            <button>"Посмотреть метрики всех пользователей"
            <button>"Повторное задание кандидату"
            <button>"Помощь по меню HR"
            <button>"Меню"

    Notes
    -----
    Only HR can access this menu.
    """
    await message.answer(
        "Меню HR",
        reply_markup=kb.hr_kb
    )

@auth
async def get_hr_help(message: types.Message):
    """Displays help message to the HR.

    Notes
    -----
    Only HR can access this menu.
    """
    await message.answer(
        # from `help hr.html`
        ("💼<b>Меню HR</b>\n\n"
            
            + "<u>Возможные команды:</u>\n"
            + "➖ <code>Посмотреть результаты кандидата</code> - выводит результаты тестового задания кандидата. "
                + "Потребуется ввести его логин (чувствителен к регистру).\n"
            + "➖ <code>Посмотреть метрики всех пользователей</code> - выводит все метрики из базы данных.\n"
            + "➖ <code>Повторное задание кандидату</code> - позволяет кандидату повторно пройти тестовое задание "
                + "(все повторные тестовые задания такие же, как самое первое).\n"
            + "❓ <code>Помощь по меню HR</code> - выводит данное сообщение.\n"
            + "⬅️ <code>Меню</code> - возвращает в оригинальное меню.\n"),
        parse_mode="HTML",
        reply_markup=kb.hr_kb,
    )

@auth
async def get_all_candidates_results(message: types.Message):
    """Sends all candidates' results and metrics in excel (xlsx) format.

                    xlsx has following columns:

| candidate_username | car_iou | plate_iou | plate_accuracy | task_started        | task_ended          | task_completed | times_attempted |
|--------------------|---------|-----------|----------------|---------------------|---------------------|----------------|-----------------|
| SXRu1              | 0.57    | 0.95      | 0.19           | 2022-01-08 04:05:06 | 2022-01-08 10:00:00 | 05:54:54       | 1               |
| roman_kucev        |         |           |                | 2022-09-20 12:12:12 |                     |                | 1               |
|                    |         |           |                |                     |                     |                |                 |

    Notes
    -----
    There is a limit of 50 Mb on file uploads via a bot.
    Only HR can access this menu.
    """
    excel_file_name, excel_output_name = generate_excel()
    with open(excel_file_name, "rb") as all_results:
        await message.answer_document(
            all_results,
            caption=excel_output_name,
            reply_markup=kb.hr_kb,
        )

def register_general_handlers(dp: Dispatcher):
    dp.register_message_handler(show_menu_commands, text=["Меню", "Menu"])
    dp.register_message_handler(get_help, commands=["start", "help"])
    dp.register_message_handler(get_help, text=["Помощь", "Help"])
    dp.register_message_handler(get_hr_help, text=["Помощь по меню HR"])
    dp.register_message_handler(get_all_candidates_results, text=["Посмотреть метрики всех пользователей"])
    dp.register_message_handler(show_hr_commands)
