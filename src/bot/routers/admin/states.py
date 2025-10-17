from aiogram.fsm.state import State, StatesGroup


class ChangeStatusStates(StatesGroup):
    input_username = State()
    select_status = State()
