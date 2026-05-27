from app.db.db_connection import execute_query


def save_user(telegram_id: int, tg_nick: str | None, full_name: str = ''):
    execute_query(
        """
        INSERT INTO members (telegram_id, tg_nick, full_name)
        VALUES (%s, %s, %s)
        ON CONFLICT (telegram_id)
        DO UPDATE SET
            tg_nick = EXCLUDED.tg_nick,
            full_name = EXCLUDED.full_name,
            updated_at = NOW();
        """,
        (telegram_id, tg_nick, full_name)
    )


def get_member_id_by_telegram_id(telegram_id: int):
    member = execute_query(
        """
        SELECT id
        FROM members
        WHERE telegram_id = %s;
        """,
        (telegram_id,),
        fetchone=True
    )

    if not member:
        return None

    return member['id']


def get_user_role(telegram_id: int):
    user = execute_query(
        """
        SELECT role::TEXT AS role
        FROM members
        WHERE telegram_id = %s;
        """,
        (telegram_id,),
        fetchone=True
    )

    if not user:
        return None

    return user['role']


def set_user_role_by_id(telegram_id: int, role: str):
    execute_query(
        """
        UPDATE members
        SET role = %s::user_role,
            updated_at = NOW()
        WHERE telegram_id = %s;
        """,
        (role, telegram_id)
    )


def set_user_role_by_nick(tg_nick: str, role: str):
    user = execute_query(
        """
        UPDATE members
        SET role = %s::user_role,
            updated_at = NOW()
        WHERE LOWER(tg_nick) = LOWER(%s)
        RETURNING id;
        """,
        (role, tg_nick),
        fetchone=True
    )

    return user is not None


def get_users():
    return execute_query(
        """
        SELECT id, telegram_id, tg_nick, full_name, role::TEXT AS role, created_at
        FROM members
        ORDER BY created_at DESC;
        """,
        fetchall=True
    )


def create_material(
    title: str,
    body: str | None,
    teacher_telegram_id: int,
    file_id: str | None = None,
    file_type: str = 'text'
):
    teacher_member_id = get_member_id_by_telegram_id(teacher_telegram_id)

    if teacher_member_id is None:
        return None

    material = execute_query(
        """
        INSERT INTO materials (title, body, teacher_id, file_id, file_type)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id;
        """,
        (title, body, teacher_member_id, file_id, file_type),
        fetchone=True
    )

    return material['id']


def get_materials():
    return execute_query(
        """
        SELECT id, title, created_at
        FROM materials
        ORDER BY created_at DESC;
        """,
        fetchall=True
    )


def get_material_by_id(material_id: int):
    return execute_query(
        """
        SELECT id, title, body, file_id, file_type, created_at
        FROM materials
        WHERE id = %s;
        """,
        (material_id,),
        fetchone=True
    )


def get_student_ids():
    students = execute_query(
        """
        SELECT telegram_id
        FROM members
        WHERE role = 'student'
          AND telegram_id IS NOT NULL;
        """,
        fetchall=True
    )

    return [student['telegram_id'] for student in students]