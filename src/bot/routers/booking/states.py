from aiogram.fsm.state import State, StatesGroup


class CreateBookingStates(StatesGroup):
    choose_date = State()
    choose_time = State()
