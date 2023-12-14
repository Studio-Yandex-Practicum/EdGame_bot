import os
import zipfile

import xlwt
from aiogram import types
from sqlalchemy.orm import Session


from db.models import (
    Achievement,
    AchievementStatus,
    Category,
    Password,
    Season,
    Team,
    User,
)


def get_user_name(session: Session, user_id: int) -> str:
    user = session.query(User).filter(User.id == user_id).first()
    return user.name


def get_all_children(session: Session):
    return session.query(User).filter(User.role == "kid").all()


def get_all_children_from_group(session: Session, group_id: int):
    return (
        session.query(User)
        .filter(User.group == group_id, User.role == "kid")
        .all()
    )


def get_all_child_achievements(session: Session, child_id):
    return (
        session.query(AchievementStatus)
        .filter(
            AchievementStatus.user_id == child_id,
            AchievementStatus.status == "pending",
        )
        .all()
    )


def get_child_by_name_and_group(session: Session, name, group):
    return (
        session.query(User)
        .filter(User.name == name, User.group == group, User.role == "kid")
        .first()
    )


def get_achievement_name(session: Session, achievement_id: int) -> str:
    achievement = (
        session.query(Achievement)
        .filter(Achievement.id == achievement_id)
        .first()
    )
    return achievement.name


def get_achievement_description(session: Session, achievement_id: int) -> str:
    achievement = (
        session.query(Achievement)
        .filter(Achievement.id == achievement_id)
        .first()
    )
    return achievement.description


def get_achievement_instruction(session: Session, achievement_id: int) -> str:
    achievement = (
        session.query(Achievement)
        .filter(Achievement.id == achievement_id)
        .first()
    )
    return achievement.instruction


def get_achievement_file_id(session: Session, achievement_id: int) -> bytes:
    achievement = (
        session.query(AchievementStatus)
        .filter(AchievementStatus.achievement_id == achievement_id)
        .first()
    )
    return achievement.files_id


def get_achievement_file_type(session: Session, achievement_id: int) -> bytes:
    achievement = (
        session.query(Achievement)
        .filter(Achievement.id == achievement_id)
        .first()
    )

    return achievement.artifact_type


def get_message_text(session: Session, id: int):
    achievement_status = (
        session.query(AchievementStatus)
        .filter(AchievementStatus.id == id)
        .first()
    )
    return achievement_status.message_text


def get_achievements_by_name(session: Session, achievement_name: str):
    """Возвращает все запросы на проверку одного задания."""
    achievements = (
        session.query(Achievement)
        .join(AchievementStatus)
        .filter(
            Achievement.name == achievement_name,
            AchievementStatus.status == "pending",
        )
        .first()
    )
    return achievements.id


def get_achievement_status_by_id(session: Session, achievement_id):
    return (
        session.query(AchievementStatus)
        .filter(AchievementStatus.achievement_id == achievement_id)
        .all()
    )


def get_achievement_status(session: Session, achievement_id: int):
    return (
        session.query(AchievementStatus)
        .filter_by(achievement_id=achievement_id)
        .all()
    )


def change_achievement_status_by_id(
    session: Session, id: int, new_status: str
) -> bool:
    """Получает AchievementStatus по его id и изменяет статус задания."""
    if achievement_status := (
        session.query(AchievementStatus)
        .filter(AchievementStatus.id == id)
        .first()
    ):
        achievement_status.status = new_status
        session.commit()
        return True
    return False


def save_rejection_reason_in_db(id: int, message_text: str):
    """Сохраняет причину отказа принять задание."""
    user_achievement = (
        session.query(AchievementStatus)
        .filter(AchievementStatus.id == id)
        .first()
    )
    user_achievement.rejection_reason = message_text
    session.commit()
    return True


async def send_task(
    message: types.Message,
    file_type,
    file_id,
    caption,
    message_text,
    inline_keyboard,
):
    if file_type == "image":
        await message.answer_photo(
            photo=file_id[0], caption=caption, reply_markup=inline_keyboard
        )
    elif file_type == "video":
        await message.answer_video(
            video=file_id[0], caption=caption, reply_markup=inline_keyboard
        )
    elif file_type == "text":
        await message.answer(
            f"{caption}\n\n{message_text}", reply_markup=inline_keyboard
        )
    else:
        await message.answer("Не удалось получить файл по id")


def get_all_group(session: Session):
    return (
        session.query(User.group).filter(User.role == "kid").distinct().all()
    )


def get_all_categories(session: Session):
    return session.query(Category).all()


def get_achievement_by_category_id(session: Session, category_id):
    achievement_by_category = (
        session.query(Achievement)
        .filter(Achievement.category_id == category_id)
        .all()
    )
    available_achievements_list = []
    for available_achievement in achievement_by_category:
        available_achievements_list.append((available_achievement))
    return available_achievements_list


def get_user_statistics(session: Session):
    a = session.query(
        User.id, User.name, User.role, User.score, User.group
    ).all()
    return a


def get_achievement_statistics(session: Session):
    return (
        session.query(
            Achievement.id,
            Achievement.name,
            Achievement.description,
            Achievement.instruction,
            Achievement.artifact_type,
            Achievement.score,
            Achievement.price,
            AchievementStatus.user_id,
            AchievementStatus.status,
            AchievementStatus.message_text,
            AchievementStatus.rejection_reason,
        )
        .join(
            AchievementStatus,
            Achievement.id == AchievementStatus.achievement_id,
        )
        .all()
    )


def get_text_user(session: Session, user_id):
    """Получение из БД ответов пользователей при выполнении задания"""
    return (
        session.query(AchievementStatus.message_text)
        .filter(AchievementStatus.user_id == user_id)
        .first()
    )


def get_foto_id_user(session: Session, user_id):
    """Получение из БД foto_id при выполнении задания."""
    return (
        session.query(AchievementStatus.files_id)
        .filter(AchievementStatus.user_id == user_id)
        .first()
    )


def export_xls(a, column_names, name_file):
    """Запись информации в эксель файл."""
    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet("contacts")
    header_font = xlwt.Font()
    header_font.name = "Arial"
    header_font.bold = True
    header_style = xlwt.XFStyle()
    header_style.font = header_font
    for i, name in enumerate(column_names):
        sheet.write(0, i, name)
    for i, t in enumerate(a, start=1):
        for j in range(len(column_names)):
            sheet.write(i, j, f"{t[j]}")
    workbook.save(name_file)


def delete_bd(session: Session):
    """Удаление БД при закрытии сезона."""
    session.query(User).delete()
    session.query(Achievement).delete()
    session.query(AchievementStatus).delete()
    session.query(Team).delete()
    session.query(Category).delete()
    session.query(Password).delete()
    session.query(Season).delete()
    session.commit()
    session.close()


def statistics(session):
    """Создание файлов эксель файлов со 
    статистическими данными пользователей и авичек."""
    os.makedirs("statictica")
    user = get_user_statistics(session)
    column_user = [
        "Номер пользователя",
        "Имя, фамилия",
        "Роль",
        "Очки",
        "Группа",
    ]
    user_file = ".//statictica//user_statistics.xls"
    export_xls(user, column_user, user_file)
    achievement = get_achievement_statistics(session)
    column_achievement = [
        "Номер ачивки",
        "Имя",
        "Описание",
        "Инструкция",
        "Тип артефакта",
        "Начальный балл",
        "Цена",
        "Номер Пользователя",
        "Статус ачивки",
        "Ответ",
        "Причина отклонения",
    ]
    achievement_file = ".//statictica//achievement_statistic.xls"
    export_xls(achievement, column_achievement, achievement_file)



def text_files(session):
    """Создание текстовых файлов с информацией с 
    информацией, прислонной от студентов при 
    выполнении задания."""
    users = session.query(User.name, User.id).all()
    for user in users:
        user_name = user[0]
        if get_text_user(session, user.id):
            test_user = get_text_user(session, user.id)
            os.makedirs(f".//statictica//{user_name}")
            with open(
                f".//statictica//{user_name}//{user_name}.txt", "w"
            ) as file:  
                file.write(test_user[0])


def foto_user_id(session):
    """Создание словаря с ключом - Имя студента, 
    значение - foto_user."""
    files = {}
    users = session.query(User.name, User.id).all()
    for user in users:
        user_name = user[0]
        if get_foto_id_user(session, user.id):
            foto_user = get_foto_id_user(session, user.id)
            files.setdefault(user_name, foto_user[0])
    return files


def zip_files():
    z = zipfile.ZipFile("statictica.zip", "w")  # Создание нового архива
    for root, dirs, files in os.walk(
        "statictica"
    ):  # Список всех файлов и папок в директории folder
        for file in files:
            z.write(
                os.path.join(root, file)
            )  # Создание относительных путей и запись файлов в архив
    z.close()
    