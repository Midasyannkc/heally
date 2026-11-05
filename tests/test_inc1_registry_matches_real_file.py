"""The first load of the real Hospital General Information file must not report added columns: the registry has to describe the real file."""
from heally import sync
from tests.conftest import HOSP


def test_first_load_of_the_real_hospital_file_reports_no_added_columns(db):
    res = sync.sync(db, "hospital_info", HOSP)
    assert res["added_columns"] == []
