from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton


# Menu Keyboard.
menu_new_candidate_button = KeyboardButton("Получить тестовое задание📄")
menu_existing_candidate_button = KeyboardButton("Тестовое задание выполнено☑️")
menu_second_chance = KeyboardButton("Повторить тестовое задание")
# menu_hr_button = KeyboardButton("HR")
menu_help_button = KeyboardButton("Помощь")

menu_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
(menu_kb
    .add(menu_new_candidate_button)
    .insert(menu_existing_candidate_button)
    .add(menu_second_chance)
    # .add(menu_hr_button)
    .add(menu_help_button)
)

# Confirm Keyboard.
confirm_button_yes = KeyboardButton("Да")
confirm_button_no = KeyboardButton("Отмена")

confirm_kb = ReplyKeyboardMarkup(resize_keyboard=True)
confirm_kb.row(confirm_button_no, confirm_button_yes)

# HR Keyboard.
hr_results_button = KeyboardButton("Посмотреть результаты кандидата")
hr_all_results_button = KeyboardButton("Посмотреть метрики всех пользователей")
hr_retry_button = KeyboardButton("Повторное задание кандидату")
hr_help_button = KeyboardButton("Помощь по меню HR")
hr_menu_button = KeyboardButton("Меню")

hr_kb = ReplyKeyboardMarkup(resize_keyboard=True)
(hr_kb
    .add(hr_results_button)
    .add(hr_all_results_button)
    .add(hr_retry_button)
    .add(hr_menu_button)
    .insert(hr_help_button)
)
