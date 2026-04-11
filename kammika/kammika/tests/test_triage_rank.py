from kammika.commands.triage import Candidate, rank


def make(number: int, labels: list[str], age_days: int = 0) -> Candidate:
    return Candidate(number=number, title=f"Issue {number}", body="", labels=labels, age_days=age_days)


def test_p0_beats_p1():
    p0 = make(1, ["P0"])
    p1 = make(2, ["P1"])
    assert rank([p1, p0])[0].number == 1


def test_bug_beats_feature_within_same_priority():
    bug = make(1, ["P2", "bug"])
    feature = make(2, ["P2", "enhancement"])
    assert rank([feature, bug])[0].number == 1


def test_older_beats_newer_when_tied():
    old = make(1, ["P3"], age_days=30)
    new = make(2, ["P3"], age_days=5)
    assert rank([new, old])[0].number == 1


def test_no_priority_label_sorts_last():
    no_prio = make(1, [])
    p4 = make(2, ["P4"])
    assert rank([no_prio, p4])[0].number == 2


def test_empty_list():
    assert rank([]) == []


def test_single_item():
    c = make(42, ["P1", "bug"])
    assert rank([c]) == [c]


def test_full_ordering():
    c1 = make(1, ["P0", "bug"], age_days=10)
    c2 = make(2, ["P0"], age_days=10)
    c3 = make(3, ["P1", "bug"], age_days=5)
    c4 = make(4, [], age_days=100)
    result = rank([c4, c3, c2, c1])
    assert [c.number for c in result] == [1, 2, 3, 4]
