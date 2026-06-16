"""
تحديث قاعدة البيانات لإدارة أرصدة الإجازات المفصلة.

- إضافة إعدادات التجديد السنوي إلى system_settings
- إنشاء جدول leave_balance_sources
- تحويل الرصيد القديم في users.leave_balance إلى مصدر رصيد أساسي
"""
import os
import sqlite3
from datetime import date


DB_PATH = 'halaqat.db'


def get_columns(cursor, table_name):
    cursor.execute(f'PRAGMA table_info({table_name})')
    return [column[1] for column in cursor.fetchall()]


def add_column(cursor, table_name, column_name, column_type):
    columns = get_columns(cursor, table_name)
    if column_name not in columns:
        print(f'➕ إضافة عمود {column_name} إلى {table_name}')
        cursor.execute(f'ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}')
    else:
        print(f'✓ العمود {column_name} موجود مسبقاً')


def update_database():
    if not os.path.exists(DB_PATH):
        print('⚠️ قاعدة البيانات غير موجودة. شغّل التطبيق أولاً أو تأكد من المسار.')
        return False

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        print('=' * 60)
        print('جاري تحديث قاعدة بيانات أرصدة الإجازات...')
        print('=' * 60)

        add_column(cursor, 'system_settings', 'annual_leave_balance', 'INTEGER DEFAULT 21')
        add_column(cursor, 'system_settings', 'leave_renewal_month', 'INTEGER DEFAULT 1')
        add_column(cursor, 'system_settings', 'leave_renewal_day', 'INTEGER DEFAULT 1')
        add_column(cursor, 'system_settings', 'carryover_leave_balance', 'BOOLEAN DEFAULT 0')
        add_column(cursor, 'system_settings', 'last_leave_renewal_year', 'INTEGER')

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS leave_balance_sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL,
                name VARCHAR(150) NOT NULL,
                balance_type VARCHAR(30) DEFAULT 'extra',
                initial_days INTEGER NOT NULL DEFAULT 0,
                remaining_days INTEGER NOT NULL DEFAULT 0,
                year INTEGER,
                is_active BOOLEAN DEFAULT 1,
                notes TEXT,
                hidden_at DATETIME,
                created_by INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(employee_id) REFERENCES users (id),
                FOREIGN KEY(created_by) REFERENCES users (id)
            )
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS ix_leave_balance_sources_employee_id
            ON leave_balance_sources (employee_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS ix_leave_balance_sources_is_active
            ON leave_balance_sources (is_active)
        """)

        current_year = date.today().year

        cursor.execute("""
            UPDATE system_settings
            SET annual_leave_balance = COALESCE(annual_leave_balance, 21),
                leave_renewal_month = COALESCE(leave_renewal_month, 1),
                leave_renewal_day = COALESCE(leave_renewal_day, 1),
                carryover_leave_balance = COALESCE(carryover_leave_balance, 0),
                last_leave_renewal_year = COALESCE(last_leave_renewal_year, ?)
        """, (current_year,))

        cursor.execute("""
            SELECT id, COALESCE(leave_balance, 0)
            FROM users
            WHERE role = 'موظف'
              AND id NOT IN (
                  SELECT DISTINCT employee_id
                  FROM leave_balance_sources
              )
        """)
        employees = cursor.fetchall()

        for employee_id, leave_balance in employees:
            cursor.execute("""
                INSERT INTO leave_balance_sources
                    (employee_id, name, balance_type, initial_days, remaining_days, year, is_active, notes)
                VALUES (?, ?, 'annual', ?, ?, ?, 1, ?)
            """, (
                employee_id,
                f'الرصيد الأساسي {current_year}',
                leave_balance,
                leave_balance,
                current_year,
                'تم إنشاؤه من الرصيد القديم'
            ))

        conn.commit()

        print(f'✓ تم إنشاء جدول مصادر الرصيد وتحديث {len(employees)} معلم')
        print('✅ تم تحديث قاعدة البيانات بنجاح')
        return True
    except Exception as exc:
        conn.rollback()
        print(f'❌ حدث خطأ أثناء التحديث: {exc}')
        return False
    finally:
        conn.close()


if __name__ == '__main__':
    raise SystemExit(0 if update_database() else 1)
