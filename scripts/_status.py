"""
Canonical status vocabulary and classification helpers, shared by
build_dashboard.py and verify_recalibration.py so status semantics can't
drift between the dashboard and the recalibration math the way the old
separate `outcome` field could (and once did — see TESTING.md).

docs/index.html's JS STATUS_ORDER array is the browser-side mirror of
ALL_STATUSES below. scripts/verify_consistency.py checks the two stay in
sync — this file is the single source of truth; the JS array is derived
from it by hand and verified, not generated.
"""

ACTIVE_STATUSES = ["scored", "applied", "awaiting_recruiter", "interviewing", "offer"]
CLOSED_STATUSES = [
    "rejected",
    "rejected_after_interview",
    "withdrawn",
    "withdrawn_after_interview",
    "assumed_rejected",
    "role_closed",
]
ALL_STATUSES = ACTIVE_STATUSES + CLOSED_STATUSES

# Reaching interview stage validates the scoring rubric's prediction
# (jd_fit/seniority/competition) regardless of what happens afterward —
# a rejection after interview is a different signal than never being
# interviewed at all, and must not be collapsed into the same bucket.
REACHED_INTERVIEW = {"interviewing", "offer", "rejected_after_interview", "withdrawn_after_interview"}
NO_INTERVIEW_NEGATIVE = {"rejected", "withdrawn", "assumed_rejected"}
# role_closed / scored / applied / awaiting_recruiter: excluded from
# recalibration — no verdict on candidate fit, or not yet resolved.


# Score-locking is a distinct concept from the active/closed dashboard
# grouping: `offer` stays in the *active* group (exciting, sorts to the top,
# not buried with rejections) but the score should still lock there — this
# tool doesn't track what happens after an offer (accepted/declined/
# negotiated is out of scope), so offer is effectively terminal for the
# purpose of "was the prediction right," even though it isn't for sorting.
LOCKS_SCORE = set(CLOSED_STATUSES) | {"offer"}


def is_closed(status):
    return status in CLOSED_STATUSES


def should_lock(status):
    return status in LOCKS_SCORE


def recalibration_signal(status):
    """'positive' | 'negative' | None (excluded from the recalibration comparison)."""
    if status in REACHED_INTERVIEW:
        return "positive"
    if status in NO_INTERVIEW_NEGATIVE:
        return "negative"
    return None
