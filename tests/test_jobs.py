import threading
from datetime import datetime

import pytest

from vsi import news
from vsi.jobs import JobStore, Refused, run_lock

VN = news.VN_TZ


def at(day, hh=10, mm=0):
    return datetime(2026, 11, day, hh, mm, tzinfo=VN)


@pytest.fixture
def store(tmp_path):
    return JobStore(tmp_path / "bot.sqlite")


def test_enqueue_and_position(store):
    a, pos_a = store.enqueue(1, "VNM", "2026-11-23", 10, at(25))
    b, pos_b = store.enqueue(1, "FPT", "2026-11-23", 10, at(25))
    assert (pos_a, pos_b) == (1, 2)
    assert store.next_queued().id == a.id
    assert a.status == "queued" and a.ticker == "VNM" and a.chat_id == 1


def test_duplicate_refused(store):
    job, _ = store.enqueue(1, "VNM", "2026-11-23", 10, at(25))
    with pytest.raises(Refused, match="VNM"):
        store.enqueue(1, "VNM", "2026-11-23", 10, at(25))
    store.start(job.id, at(25))
    with pytest.raises(Refused):
        store.enqueue(1, "VNM", "2026-11-23", 10, at(25))
    store.finish(job.id, "done", at(25))
    store.enqueue(1, "VNM", "2026-11-23", 10, at(25))  # allowed again


def test_cap_refuses_run_n_plus_1(store):
    old, _ = store.enqueue(1, "AAA", "2026-11-23", 2, at(24, 23, 59))
    store.start(old.id, at(24, 23, 59))  # yesterday, Vietnam time
    store.finish(old.id, "done", at(25, 0, 5))
    a, _ = store.enqueue(1, "VNM", "2026-11-23", 2, at(25))
    store.start(a.id, at(25))
    store.enqueue(1, "FPT", "2026-11-23", 2, at(25))  # queued counts
    assert store.runs_today(at(25)) == 2
    with pytest.raises(Refused, match="2"):
        store.enqueue(1, "HPG", "2026-11-23", 2, at(25))


def test_recover_marks_running_failed(store):
    job, _ = store.enqueue(1, "VNM", "2026-11-23", 10, at(25))
    store.start(job.id, at(25))
    recovered = store.recover(at(25, 11))
    assert [j.id for j in recovered] == [job.id]
    again = store.get(job.id)
    assert again.status == "failed" and again.error == "bot restarted during the run"
    assert store.active() == []


def test_unsent_and_finish_fields(store):
    job, _ = store.enqueue(1, "VNM", "2026-11-23", 10, at(25))
    store.start(job.id, at(25))
    store.finish(job.id, "done_unsent", at(25), report_path="/r/x.html", rating="Hold", summary="text")
    [u] = store.unsent()
    assert (u.report_path, u.rating, u.summary) == ("/r/x.html", "Hold", "text")


def test_state_roundtrip(store, tmp_path):
    assert store.get_state("offset") is None
    store.set_state("offset", "42")
    assert JobStore(tmp_path / "bot.sqlite").get_state("offset") == "42"


def test_run_lock_is_exclusive(tmp_path):
    lock = tmp_path / "run.lock"
    inside, release, second_in = threading.Event(), threading.Event(), threading.Event()

    def first():
        with run_lock(lock):
            inside.set()
            release.wait(5)

    def second():
        inside.wait(5)
        with run_lock(lock):
            second_in.set()

    t1, t2 = threading.Thread(target=first), threading.Thread(target=second)
    t1.start(), t2.start()
    inside.wait(5)
    assert not second_in.wait(0.3)  # blocked while the first holds the lock
    release.set()
    t1.join(5), t2.join(5)
    assert second_in.is_set()


def test_vsi_home(monkeypatch, tmp_path):
    monkeypatch.setenv("VSI_HOME", str(tmp_path))
    assert news.vsi_home() == tmp_path


def test_claim_only_once(store):
    job, _ = store.enqueue(1, "VNM", "2026-11-23", 10, at(25))
    assert store.claim(job.id, at(25)) is True
    assert store.claim(job.id, at(25)) is False  # a second worker must not start it again
    assert store.get(job.id).status == "running"


def test_instance_lock_refuses_second(tmp_path):
    from vsi.jobs import instance_lock
    first = instance_lock(tmp_path / "bot.lock")
    assert first is not None
    assert instance_lock(tmp_path / "bot.lock") is None
    first.close()
    assert instance_lock(tmp_path / "bot.lock") is not None
