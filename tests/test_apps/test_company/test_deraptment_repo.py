import pytest

from server.apps.company.infra.repository import DepartmentRepo
from server.apps.company.models import Department
from server.di import resolve
from tests.plugins.department_factory import DepartmentBatchFactory


@pytest.mark.django_db
def test_get_all(department_batch: DepartmentBatchFactory) -> None:
    """Test the `get_all()` method of DepartmentRepo."""
    batch_size = 2
    department_batch(batch_size)

    repo = resolve(DepartmentRepo)
    all_departments = repo.get_all()

    assert all_departments.count() == batch_size


@pytest.mark.django_db
def test_get_by_pk(department: Department) -> None:
    """Test the `get_by_pk()` method of DepartmentRepo."""
    repo = resolve(DepartmentRepo)
    department_obj = repo.get_by_pk(pk=department.id)

    assert department_obj == department


@pytest.mark.django_db
def test_get_by_pk_none() -> None:
    """get_by_pk raises Department.DoesNotExist if object is missing."""
    repo = resolve(DepartmentRepo)
    with pytest.raises(Department.DoesNotExist):
        repo.get_by_pk(pk=1)


@pytest.mark.django_db
def test_update_department(department: Department) -> None:
    """Test DepartmentRepo update_department method changes department name."""
    repo = resolve(DepartmentRepo)
    original_name = department.name
    upd_department_obj = repo.update_department(
        department=department, name='UpdDEP'
    )
    assert upd_department_obj.name == 'UpdDEP'
    assert upd_department_obj.name != original_name
