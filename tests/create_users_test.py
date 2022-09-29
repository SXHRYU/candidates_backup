import pytest
from create_users.db_operations import get_all_candidates

@pytest.fixture
def fake_db():
    a = []
    a.append(1)
    a.append(2)
    a.append(3)
    yield a
    print(a)
    a.pop()
    a.pop()
    print(a)

@pytest.fixture
def fake_transaction():
    b = "lolka"
    yield b
    print(b)
    b = "success"
    print(b)

def test_get_all_candidates(fake_db, fake_transaction):
    assert fake_db == [1, 2, 3]
    print('something done')
    assert fake_transaction == "lolka"
    