import functools

from utils import db_commands


def task_params(queryset):
    @functools.wraps(queryset)
    def wrapper(*args, **kwargs):
        all_tasks = queryset(*args, **kwargs)
        tasks = []

        for task in all_tasks:
            user = db_commands.select_user(task.user_id)
            achievement = db_commands.get_achievement(task.achievement_id)
            category = db_commands.get_category(task.achievement.category_id)
            tasks.append((task, user, achievement, category))

        return tasks
    return wrapper
