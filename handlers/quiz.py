import random
import json
from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from data.questions import quiz_data
from database.db import get_state, save_state, delete_state, save_result

def build_options_keyboard(options, q_index):
    builder = InlineKeyboardBuilder()
    for opt_idx, opt_text in enumerate(options):
        # callback кодируем рандом индекса ответа 
        builder.add(types.InlineKeyboardButton(text=opt_text, callback_data=f"answer:{q_index}:{opt_idx}"))
    builder.adjust(1)
    return builder.as_markup()

async def start_quiz(message: types.Message):
    user_id = message.from_user.id
    
    q_indices = list(range(len(quiz_data)))
    random.shuffle(q_indices)
    # Задаём порядок ответов для каждого вопроса
    options_order = {}
    for qi in q_indices:
        opts = list(range(len(quiz_data[qi]['options'])))
        random.shuffle(opts)
        options_order[str(qi)] = opts
    # Исходное состояние
    await save_state(user_id, 0, q_indices, options_order, 0)
    # Отправить первый вопрос
    await send_question(message, user_id)

async def send_question(message_or_callback, user_id):
    state = await get_state(user_id)
    if not state:
        await message_or_callback.answer("Ошибка: состояние не найдено. Запустите /quiz.")
        return
    q_index_in_shuffled = state['question_index']
    q_order = state['question_order']
    if q_index_in_shuffled >= len(q_order):
        await message_or_callback.answer("Квиз окончен.")
        return
    real_q_idx = q_order[q_index_in_shuffled]
    q = quiz_data[real_q_idx]
    # Получить варианты в перемешанном порядке, сохраненные в состоянии
    opts_order = state['options_order'].get(str(real_q_idx))
    opts = [q['options'][i] for i in opts_order]
    kb = build_options_keyboard(opts, q_index_in_shuffled)
    await message_or_callback.answer(q['question'], reply_markup=kb)

async def handle_answer(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    # Анализ ответа на данные обратного вызова:{q_index_in_shuffled}:{opt_idx_in_shown}
    parts = callback.data.split(":")
    if len(parts) != 3:
        await callback.answer()
        return
    _, q_index_in_shuffled_s, opt_idx_shown_s = parts
    q_index_in_shuffled = int(q_index_in_shuffled_s)
    opt_idx_shown = int(opt_idx_shown_s)

    state = await get_state(user_id)
    if not state:
        await callback.message.answer("Состояние игры не найдено. Запустите /quiz.")
        return
    # Убедитесь, что обратный вызов соответствует текущему вопросу (avoid stale callbacks)
    if q_index_in_shuffled != state['question_index']:
        await callback.answer("Этот вопрос уже обработан.", show_alert=True)
        return

    q_order = state['question_order']
    real_q_idx = q_order[q_index_in_shuffled]
    q = quiz_data[real_q_idx]
    opts_order = state['options_order'].get(str(real_q_idx))
    # Какой исходный индекс варианта соответствует показанному option index:
    chosen_original_opt = opts_order[opt_idx_shown]
    correct_original = q['correct_option']

    # Удалить встроенную клавиатуру
    try:
        await callback.bot.edit_message_reply_markup(chat_id=callback.from_user.id, message_id=callback.message.message_id, reply_markup=None)
    except Exception:
        pass

    chosen_text = q['options'][chosen_original_opt]
    if chosen_original_opt == correct_original:
        await callback.message.answer(f"Вы выбрали: {chosen_text}\n Верно!")
        state['score'] += 1
    else:
        correct_text = q['options'][correct_original]
        await callback.message.answer(f"Вы выбрали: {chosen_text}\n Неправильно. Правильный ответ: {correct_text}")
    # Следующий вопрос
    state['question_index'] += 1
    await save_state(user_id, state['question_index'], state['question_order'], state['options_order'], state['score'])

    # Дальше или закончили
    if state['question_index'] < len(state['question_order']):
        await send_question(callback.message, user_id)
    else:
        # Конец
        final_score = state['score']
        await callback.message.answer(f"Квиз завершен! Ваш результат: {final_score} из {len(state['question_order'])} правильных.")
        await save_result(user_id, final_score)
        await delete_state(user_id)
