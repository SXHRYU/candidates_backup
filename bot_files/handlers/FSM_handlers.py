from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from authorization import auth
from create_users.db_operations import remember_username_password
from db import db_conn
from bot_files import keyboards as kb
from create_users.to_handlers import (
    get_all_candidates,
    get_user_credentials,
)
from tasks_metrics.to_handlers import (
    send_HR_metrics,
    task_complete,
    get_candidate_results,
    get_candidate_formatted_results,
    update_times_attempted,
)
from tasks_generator.to_handlers import (
    task_generated,
)
from tasks_new.to_handlers import (
    new_task_generated,
)


class FSM_NewCandidate(StatesGroup):
    confirm = State()

    async def new_candidate_command(message: types.Message):
        await FSM_NewCandidate.confirm.set()
        await message.reply(
            ("Зарегистрироваться для прохождения тестового задания? 📄\n"
                + "❗️<b>Предупреждение:</b> после подтверждения будет записана дата начала выполнения.\n\n"
                + "Если вы уже зарегистрированы и хотите сообщить о выполненном задании, "
                + "вернитесь в главное меню и нажмите '<code>Тестовое задание выполнено☑️</code>'."),
            parse_mode="HTML",
            reply_markup=kb.confirm_kb,
        )

    async def new_candidate_confirm(message: types.Message, state: FSMContext):
        if message.text == "Отмена":
            await message.reply(
            "Меню",
            reply_markup=kb.menu_kb,
        )
        elif message.text == "Да":
            if message.from_user.username in get_all_candidates(conn=db_conn):
                credentials = remember_username_password(message.from_user.username, conn=db_conn)
                username = credentials["username"]
                password = credentials["password"]
                await message.reply(
                    ("❗️Вы уже зарегистрировались на "
                    + "<a href='candidates.trainingdata.solutions'>candidates.trainingdata.solutions</a>.\n"
                    + "Ваши данные для входа:\n"
                    + f"Логин: <code>{username}</code>\n"
                    + f"Пароль: <code>{password}</code>\n"
                    + "Если произошла ошибка, свяжитесь с HR."),
                    parse_mode="HTML",
                    reply_markup=kb.menu_kb,
                )
            else:
                credentials = get_user_credentials(message.from_user.username)
                username = credentials["username"]
                password = credentials["password1"]
                await message.reply(
                    ("<a href='candidates.trainingdata.solutions'>candidates.trainingdata.solutions</a>\n"
                        + "Ваши данные для входа:\n"
                        + f"Логин: <code>{username}</code>\n"
                        + f"Пароль: <code>{password}</code>\n"
                        + "Описание задания: ЗДЕСЬ ДОЛЖНА БЫТЬ ССЫЛКА НА НОУШЕН\n" # TODO: ССЫЛКА НА НОУШЕН
                        + "После успешного выполнения тестового задания, необходимо перейти в главное меню, "
                        + "нажать кнопку  '<code>Тестовое задание выполнено☑️</code>' и подтвердить выполнение. Удачи!"),
                    parse_mode="HTML",
                    reply_markup=kb.menu_kb,
                )
                if not task_generated(message.from_user.username):
                    await message.reply(
                        "Произошла ошибка при создании задания. Обратитесь к HR.",
                        reply_markup=kb.menu_kb,
                    )
        else:
            await message.reply(
            "Ошибка! Попробуйте ещё раз.",
            reply_markup=kb.menu_kb,
        )
        await state.finish()

class FSM_ExistingCandidate(StatesGroup):
    confirm = State()

    async def existing_candidate_command(message: types.Message):
        await FSM_ExistingCandidate.confirm.set()
        await message.reply(
            "Задание выполнено?",
            reply_markup=kb.confirm_kb,
        )

    async def existing_candidate_confirm(message: types.Message, state: FSMContext):
        if message.text == "Отмена":
            await message.reply(
            "Меню",
            reply_markup=kb.menu_kb,
        )
        elif message.text == "Да":
            if message.from_user.username not in get_all_candidates(conn=db_conn):
                await message.reply(
                    "❗️Вы ещё не зарегистрировались. Если произошла ошибка, свяжитесь с HR.",
                    reply_markup=kb.menu_kb,
                )
            else:
                await message.answer("Проверяем...\nПодождите, пожалуйста.")
                task_status = task_complete(message.from_user.username)
                if task_status == True:
                    send_HR_metrics(message.from_user.username)
                    await message.reply(
                        "Выполнено! Можете связаться с HR по результатам работы.",
                        reply_markup=kb.menu_kb,
                    )
                else:
                    await message.reply(
                        task_status,
                        reply_markup=kb.menu_kb,
                    )
        else:
            await message.reply(
            "Ошибка! Попробуйте ещё раз.",
            reply_markup=kb.menu_kb,
        )
        await state.finish()

class FSM_RepeatTestAssignment(StatesGroup):
    confirm = State()

    async def repeat_test_assignment_command(message: types.Message):
        if message.from_user.username not in get_all_candidates(conn=db_conn):
            await message.reply(
                ("Вы ещё не зарегистрировались. Нажмите '<code>Получить тестовое задание📄</code>'.\n"
                    + "Если произошла ошибка, свяжитесь с HR."),
                parse_mode="HTML",
                reply_markup=kb.menu_kb,
            )
        else:
            await FSM_RepeatTestAssignment.confirm.set()
            await message.reply(
                "Вы уверены, что хотите попробовать пройти тестовое задание заново?",
                reply_markup=kb.confirm_kb,
            )
    
    async def repeat_test_assignment_confirm(message: types.Message, state: FSMContext):
        if message.text == "Отмена":
            await message.reply(
            "Меню",
            reply_markup=kb.menu_kb,
        )
        elif message.text == "Да":
            user_results: dict[str, str] = get_candidate_results(message.from_user.username)
            if user_results["times_attempted"] == 2:
                await message.answer(
                    "Пройти тестовое задание можно максимум 2 раза. Если произошла ошибка, свяжитесь с HR.",
                    reply_markup=kb.menu_kb,
                )
            else:
                await message.answer("Проверяем...\nПодождите, пожалуйста.")
                task_status = task_complete(message.from_user.username)
                if task_status == True:
                    if not new_task_generated(message.from_user.username):
                        await message.reply(
                            "Произошла ошибка при создании задания. Свяжитесь с HR.",
                            reply_markup=kb.menu_kb,
                        )
                    else:
                        update_times_attempted(message.from_user.username,
                                               conn=db_conn, times_attempted=2)
                        await message.reply(
                            "Готово. Можете приступить к решению.",
                            reply=kb.menu_kb,
                        )
                else:
                    await message.answer(
                        ("Для получения нового тестового задания необходимо <b>полностью</b> пройти первое.\n"
                            + f"Состояние вашего задания:\n{task_status}\n"
                            + "Закончите первое задание и попробуйте ещё раз."),
                        parse_mode="HTML",
                        reply_markup=kb.menu_kb,
                    )
        else:
            await message.reply(
            "Ошибка! Попробуйте ещё раз.",
            reply_markup=kb.menu_kb,
        )
        await state.finish()

class FSM_HRCandidateResults(StatesGroup):
    username = State()

    @auth
    async def hr_candidate_results_command(message: types.Message):
        await FSM_HRCandidateResults.username.set()
        await message.reply(
            "Введите логин (Telegram) кандидата.",
        )

    async def hr_candidate_results_username(message: types.Message, state: FSMContext):
        if message.text not in get_all_candidates(conn=db_conn):
            await message.reply(
                "Такого пользователя не существует. Попробуйте ещё раз.",
                reply_markup=kb.hr_kb,
            )
        else:
            await message.reply(
            get_candidate_formatted_results(message.text),
            reply_markup=kb.hr_kb,
        )
        await state.finish()

class FSM_HRNewTask(StatesGroup):
    username = State()
    
    @auth
    async def hr_new_task_command(message: types.Message):
        await FSM_HRNewTask.username.set()
        await message.reply(
            "Введите логин (Telegram) кандидата.",
        )

    async def hr_new_task_username(message: types.Message, state: FSMContext):
        if message.text not in get_all_candidates(conn=db_conn):
            await message.reply(
                "Такого пользователя не существует. Попробуйте ещё раз.",
                reply_markup=kb.hr_kb,
            )
        else:
            if not new_task_generated(message.text):
                await message.reply(
                    "Произошла ошибка при создании задания. Обратитесь к разработчикам.",
                    reply_markup=kb.hr_kb,
                )
            else:
                await message.reply(
                    "Готово. Можете сообщить пользователю об этом.",
                    reply=kb.hr_kb,
                )
        await state.finish()
        

def register_FSM_handlers(dp: Dispatcher):
    # Регистрируем нового кандидата.
    dp.register_message_handler(
        FSM_NewCandidate.new_candidate_command, text="Получить тестовое задание📄", state=None)
    dp.register_message_handler(
        FSM_NewCandidate.new_candidate_confirm, state=FSM_NewCandidate.confirm)

    # Проверяем тестовое задание существующего кандидата.
    dp.register_message_handler(
        FSM_ExistingCandidate.existing_candidate_command, text="Тестовое задание выполнено☑️", state=None)
    dp.register_message_handler(
        FSM_ExistingCandidate.existing_candidate_confirm, state=FSM_ExistingCandidate.confirm)

    # Кандидат запрашивает новое задание.
    dp.register_message_handler(
        FSM_RepeatTestAssignment.repeat_test_assignment_command, text="Повторить тестовое задание", state=None)
    dp.register_message_handler(
        FSM_RepeatTestAssignment.repeat_test_assignment_confirm, state=FSM_RepeatTestAssignment.confirm)

    # Узнаём индивидуальные результаты кандидата.
    dp.register_message_handler(
        FSM_HRCandidateResults.hr_candidate_results_command, text="Посмотреть результаты кандидата", state=None)
    dp.register_message_handler(
        FSM_HRCandidateResults.hr_candidate_results_username, state=FSM_HRCandidateResults.username)

    # Выдаём кандидату повторное задание.
    dp.register_message_handler(
        FSM_HRNewTask.hr_new_task_command, text="Повторное задание кандидату", state=None)
    dp.register_message_handler(
        FSM_HRNewTask.hr_new_task_username, state=FSM_HRNewTask.username)
