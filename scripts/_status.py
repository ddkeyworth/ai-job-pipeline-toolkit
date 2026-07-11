"""
Canonical status vocabulary and classification helpers, shared by
build_dashboard.py and verify_recalibration.py so status semantics can't
drift between the dashboard and the recalibration math the way the old
separate `outcome` field could (and once did – see TESTING.md).

docs/index.html's JS STATUS_ORDER array is the browser-side mirror of
ALL_STATUSES below. scripts/verify_consistency.py checks the two stay in
sync – this file is the single source of truth; the JS array is derived
from it by hand and verified, not generated.

The state machine is deliberately exhaustive and small – every status has
exactly one place it's reached from:
  scored       -> applied | didnt_apply
  applied      -> rejected | assumed_rejected | interviewing
  interviewing -> offer | rejected_after_interview | withdrew_after_interview

Two earlier statuses (awaiting_recruiter, role_closed) were tried and
dropped as too messy to track in practice / not useful signal – removed
rather than kept around unused.
"""

# Display/filter order – a logical read of the state machine (each status
# sits right after wherever it's reached from), not "active statuses then
# closed statuses." offer is deliberately last: it's the one status that
# feels wrong buried mid-list even though structurally it's just one of
# interviewing's three exits.
ALL_STATUSES = [
    "scored",
    "didnt_apply",
    "applied",
    "rejected",
    "assumed_rejected",
    "interviewing",
    "rejected_after_interview",
    "withdrew_after_interview",
    "offer",
]

# Classification groups – membership only, order isn't load-bearing here
# the way it is for ALL_STATUSES above.
ACTIVE_STATUSES = ["scored", "applied", "interviewing", "offer"]
CLOSED_STATUSES = [
    "didnt_apply",
    "rejected",
    "assumed_rejected",
    "rejected_after_interview",
    "withdrew_after_interview",
]

# Reaching interview stage validates the scoring rubric's prediction
# (jd_fit/seniority/competition) regardless of what happens afterward –
# a rejection after interview is a different signal than never being
# interviewed at all, and must not be collapsed into the same bucket.
REACHED_INTERVIEW = {"interviewing", "offer", "rejected_after_interview", "withdrew_after_interview"}
NO_INTERVIEW_NEGATIVE = {"rejected", "assumed_rejected"}
# didnt_apply / scored / applied: excluded from recalibration – a
# deliberate pass or an unresolved application says nothing about whether
# the scoring rubric's prediction was right.


# Score-locking is a distinct concept from the active/closed dashboard
# grouping: `offer` stays in the *active* group (exciting, sorts to the top,
# not buried with rejections) but the score should still lock there – this
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
