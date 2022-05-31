from wish_functions import *
from gia_functions import *

# обрабатывает коллбэки от инлайн-кнопок
def callback_func(update, context):
    query = update.callback_query['data']
    if query.split('||')[-1] == 'sbcb':
        choose_catalog(update, context)
    if query.split('||')[-1] == 'cccb':
        get_task(update, context)
    if query.split('||')[-1] == 'gtcb':
        task(update, context)
