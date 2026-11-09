from pathlib import Path
from decimal import Decimal
import pytest
from pydantic import ValidationError
from app.schemas.employees import EmployeeInput,SalaryInput
from app.db.academic_queries import AcademicQuery,adapt_query_to_current_schema

ROOT=Path(__file__).resolve().parents[2]


def test_schema_and_seed_have_separate_responsibilities():
    schema=(ROOT/'sql/data/01_create_database.sql').read_text(encoding='utf-8')
    seed=(ROOT/'sql/data/02_seed_data.sql').read_text(encoding='utf-8')
    assert 'CREATE DATABASE IF NOT EXISTS' in schema
    assert 'CREATE TABLE IF NOT EXISTS' in schema
    assert 'INSERT INTO' not in schema
    assert not any(word in '\n'.join(line for line in seed.splitlines() if not line.startswith('--')).upper() for word in ('CREATE TABLE','ALTER TABLE','PASSWORD','NV000'))
    assert '-- @system' in seed and '-- @demo' in seed
    assert sorted(path.name for path in (ROOT/'sql/data').glob('*.sql'))==['01_create_database.sql','02_seed_data.sql']


def test_personnel_input_cannot_implicitly_assign_a_role():
    payload=dict(employee_id='E',name='Name',phone='0900000201',email='e@example.test',store_id='S',position_id='sales',salary='100.50')
    assert EmployeeInput(**payload).salary==Decimal('100.50')
    with pytest.raises(ValidationError):
        EmployeeInput(**payload,role='system_admin')
    with pytest.raises(ValidationError):
        SalaryInput(salary=0)


def test_academic_queries_preserve_saved_prices():
    query=AcademicQuery('M04_Q01','Saved prices','SELECT SUM(so_luong*don_gia_ban-giam_gia) FROM chi_tiet_don_hang;')
    assert adapt_query_to_current_schema(query)==(query.sql,None)
