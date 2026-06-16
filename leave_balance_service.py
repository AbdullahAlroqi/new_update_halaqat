from calendar import monthrange
from datetime import date, datetime

from sqlalchemy import case

from models import db, User, Role, SystemSettings, LeaveBalanceSource


DEFAULT_ANNUAL_LEAVE_BALANCE = 21


def get_leave_settings():
    settings = SystemSettings.query.first()
    if not settings:
        settings = SystemSettings()
        db.session.add(settings)
        db.session.flush()

    changed = False
    defaults = {
        'annual_leave_balance': DEFAULT_ANNUAL_LEAVE_BALANCE,
        'leave_renewal_month': 1,
        'leave_renewal_day': 1,
        'carryover_leave_balance': False,
    }
    for field, value in defaults.items():
        if getattr(settings, field, None) is None:
            setattr(settings, field, value)
            changed = True

    if changed:
        db.session.flush()

    return settings


def get_renewal_date(settings, year=None):
    year = year or date.today().year
    month = settings.leave_renewal_month or 1
    day = settings.leave_renewal_day or 1
    day = min(day, monthrange(year, month)[1])
    return date(year, month, day)


def sync_employee_leave_balance(employee):
    active_sources = LeaveBalanceSource.query.filter_by(
        employee_id=employee.id,
        is_active=True
    ).all()

    if active_sources:
        employee.leave_balance = sum(source.remaining_days or 0 for source in active_sources)

    return employee.leave_balance or 0


def ensure_employee_leave_sources(employee, settings=None):
    if employee.role != Role.EMPLOYEE:
        return

    source_exists = LeaveBalanceSource.query.filter_by(employee_id=employee.id).first()
    if source_exists:
        sync_employee_leave_balance(employee)
        return

    settings = settings or get_leave_settings()
    legacy_balance = employee.leave_balance or 0
    current_year = date.today().year
    source = LeaveBalanceSource(
        employee_id=employee.id,
        name=f'الرصيد الأساسي {current_year}',
        balance_type='annual',
        initial_days=legacy_balance,
        remaining_days=legacy_balance,
        year=current_year,
        is_active=True,
        notes='تم إنشاؤه من الرصيد القديم'
    )
    db.session.add(source)
    employee.leave_balance = legacy_balance


def ensure_all_employee_leave_sources():
    settings = get_leave_settings()
    employees = User.query.filter_by(role=Role.EMPLOYEE).all()
    for employee in employees:
        ensure_employee_leave_sources(employee, settings)
    db.session.flush()


def get_active_sources(employee_id):
    return LeaveBalanceSource.query.filter_by(
        employee_id=employee_id,
        is_active=True
    ).order_by(
        case(
            (LeaveBalanceSource.balance_type == 'carryover', 0),
            (LeaveBalanceSource.balance_type == 'extra', 1),
            (LeaveBalanceSource.balance_type == 'annual', 2),
            else_=3
        ),
        LeaveBalanceSource.created_at.asc()
    ).all()


def get_or_create_active_annual_source(employee, year=None, created_by=None):
    year = year or date.today().year
    annual_source = LeaveBalanceSource.query.filter_by(
        employee_id=employee.id,
        balance_type='annual',
        year=year,
        is_active=True
    ).first()

    if annual_source:
        return annual_source

    annual_source = LeaveBalanceSource(
        employee_id=employee.id,
        name=f'الرصيد الأساسي {year}',
        balance_type='annual',
        initial_days=0,
        remaining_days=0,
        year=year,
        is_active=True,
        created_by=created_by
    )
    db.session.add(annual_source)
    db.session.flush()
    return annual_source


def set_employee_annual_balance(employee, days, created_by=None):
    ensure_employee_leave_sources(employee)
    annual_source = get_or_create_active_annual_source(employee, created_by=created_by)
    old_balance = annual_source.remaining_days or 0
    annual_source.initial_days = days
    annual_source.remaining_days = days
    annual_source.created_by = annual_source.created_by or created_by
    sync_employee_leave_balance(employee)
    return old_balance, employee.leave_balance or 0


def add_extra_balance(employee, name, days, created_by=None):
    ensure_employee_leave_sources(employee)
    source = LeaveBalanceSource(
        employee_id=employee.id,
        name=name.strip(),
        balance_type='extra',
        initial_days=days,
        remaining_days=days,
        year=date.today().year,
        is_active=True,
        created_by=created_by
    )
    db.session.add(source)
    db.session.flush()
    sync_employee_leave_balance(employee)
    return source


def hide_balance_source(source):
    source.is_active = False
    source.hidden_at = datetime.utcnow()
    sync_employee_leave_balance(source.employee)
    return source.employee.leave_balance or 0


def deduct_leave_balance(employee, days):
    ensure_employee_leave_sources(employee)
    remaining_to_deduct = days
    sources = get_active_sources(employee.id)

    for source in sources:
        if remaining_to_deduct <= 0:
            break

        available = source.remaining_days or 0
        if source.balance_type == 'annual':
            source.remaining_days = available - remaining_to_deduct
            remaining_to_deduct = 0
            break

        deduction = min(available, remaining_to_deduct)
        source.remaining_days = available - deduction
        remaining_to_deduct -= deduction

    if remaining_to_deduct > 0:
        annual_source = get_or_create_active_annual_source(employee)
        annual_source.remaining_days = (annual_source.remaining_days or 0) - remaining_to_deduct

    sync_employee_leave_balance(employee)
    return employee.leave_balance or 0


def process_due_leave_renewal(today=None):
    today = today or date.today()
    settings = get_leave_settings()
    renewal_date = get_renewal_date(settings, today.year)

    if today < renewal_date or settings.last_leave_renewal_year == today.year:
        return False

    ensure_all_employee_leave_sources()
    annual_days = settings.annual_leave_balance or DEFAULT_ANNUAL_LEAVE_BALANCE
    employees = User.query.filter_by(role=Role.EMPLOYEE).all()

    for employee in employees:
        previous_balance = sync_employee_leave_balance(employee)
        active_sources = LeaveBalanceSource.query.filter_by(
            employee_id=employee.id,
            is_active=True
        ).all()

        for source in active_sources:
            source.is_active = False
            source.hidden_at = datetime.utcnow()

        annual_source = LeaveBalanceSource(
            employee_id=employee.id,
            name=f'الرصيد الأساسي {today.year}',
            balance_type='annual',
            initial_days=annual_days,
            remaining_days=annual_days,
            year=today.year,
            is_active=True
        )
        db.session.add(annual_source)

        if settings.carryover_leave_balance and previous_balance > 0:
            carryover_source = LeaveBalanceSource(
                employee_id=employee.id,
                name=f'مرحل من سنة {today.year - 1}',
                balance_type='carryover',
                initial_days=previous_balance,
                remaining_days=previous_balance,
                year=today.year,
                is_active=True
            )
            db.session.add(carryover_source)

        db.session.flush()
        sync_employee_leave_balance(employee)

    settings.last_leave_renewal_year = today.year
    db.session.flush()
    return True
