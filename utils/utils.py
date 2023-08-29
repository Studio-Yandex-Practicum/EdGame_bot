from db.models import Achievement


def process_next_achievements(tasks: list[Achievement], count: int = 0,
                              previous_final_item: int = 0, page_size: int = 5
                              ) -> tuple:
    '''
    Обрабатывает список доступных ачивок и выдает кортеж с текстом для
    сообщения, словарем id ачивок, информацию для пагинатора,
    если ачивок много, и номер последнего элемента для клавиатуры.
    '''
    task_list = []
    task_ids = {}
    # Устанавливаем номер последнего элемента
    new_final_item = previous_final_item + page_size
    # Размер страницы
    final_item = (
        len(tasks) if len(tasks) < (new_final_item + 1) else new_final_item)
    for i in range(previous_final_item, final_item):
        count += 1
        task_list.append(f'{count}: {tasks[i].name}.')
        task_ids[count] = tasks[i].id
    text = '\n\n'.join(task_list)
    task_info = {'count': count, 'final_item': final_item, 'tasks': tasks}
    return (text, task_ids, task_info)


def process_previous_achievements(tasks: list[Achievement], count: int = 0,
                                  previous_final_item: int = 0,
                                  page_size: int = 5) -> tuple:
    '''
    Обрабатывает список доступных ачивок и выдает кортеж с текстом для
    сообщения, словарем id ачивок, информацию для пагинатора,
    если ачивок много, и номер последнего элемента для клавиатуры.
    '''
    task_list = []
    task_ids = {}
    # Счетчик id
    count = count - page_size * 2 if count > page_size * 2 else 0
    # Устанавливаем номер последнего элемента
    new_final_item = previous_final_item - page_size
    # Устанавливаем номер первого элемента
    first_item = (
        previous_final_item - page_size * 2
        if previous_final_item > page_size * 2 else 0)
    # Размер страницы
    final_item = (
        len(tasks) if len(tasks) < (new_final_item + 1) else new_final_item)
    for i in range(first_item, final_item):
        count += 1
        task_list.append(f'{count}: {tasks[i].name}.')
        task_ids[count] = tasks[i].id
    text = '\n\n'.join(task_list)
    task_info = {
        'count': count,
        'first_item': first_item,
        'final_item': final_item,
        'tasks': tasks
    }
    return (text, task_ids, task_info)
