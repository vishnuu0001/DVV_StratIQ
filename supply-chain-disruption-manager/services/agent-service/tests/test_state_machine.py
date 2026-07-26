# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Tests for the incident state machine — valid and invalid transitions.
# Date: 2026-04-20
# ---------------------------------------------------------------------------
"""Tests for the incident state machine — valid and invalid transitions."""
from __future__ import annotations

import pytest

from agents.store.models import IncidentState, validate_transition, VALID_TRANSITIONS


class TestValidTransitions:
    """Test all explicitly valid state transitions."""

    # Function: test_new_to_classified
    def test_new_to_classified(self):
        assert validate_transition(IncidentState.NEW, IncidentState.CLASSIFIED) is True

    # Function: test_new_to_failed
    def test_new_to_failed(self):
        assert validate_transition(IncidentState.NEW, IncidentState.FAILED) is True

    # Function: test_classified_to_dispatched
    def test_classified_to_dispatched(self):
        assert validate_transition(IncidentState.CLASSIFIED, IncidentState.DISPATCHED) is True

    # Function: test_classified_to_escalated
    def test_classified_to_escalated(self):
        assert validate_transition(IncidentState.CLASSIFIED, IncidentState.ESCALATED) is True

    # Function: test_classified_to_failed
    def test_classified_to_failed(self):
        assert validate_transition(IncidentState.CLASSIFIED, IncidentState.FAILED) is True

    # Function: test_dispatched_to_in_progress
    def test_dispatched_to_in_progress(self):
        assert validate_transition(IncidentState.DISPATCHED, IncidentState.IN_PROGRESS) is True

    # Function: test_dispatched_to_failed
    def test_dispatched_to_failed(self):
        assert validate_transition(IncidentState.DISPATCHED, IncidentState.FAILED) is True

    # Function: test_in_progress_to_awaiting_approval
    def test_in_progress_to_awaiting_approval(self):
        assert validate_transition(IncidentState.IN_PROGRESS, IncidentState.AWAITING_APPROVAL) is True

    # Function: test_in_progress_to_resolved
    def test_in_progress_to_resolved(self):
        assert validate_transition(IncidentState.IN_PROGRESS, IncidentState.RESOLVED) is True

    # Function: test_in_progress_to_blocked
    def test_in_progress_to_blocked(self):
        assert validate_transition(IncidentState.IN_PROGRESS, IncidentState.BLOCKED) is True

    # Function: test_in_progress_to_failed
    def test_in_progress_to_failed(self):
        assert validate_transition(IncidentState.IN_PROGRESS, IncidentState.FAILED) is True

    # Function: test_awaiting_approval_to_resolved
    def test_awaiting_approval_to_resolved(self):
        assert validate_transition(IncidentState.AWAITING_APPROVAL, IncidentState.RESOLVED) is True

    # Function: test_awaiting_approval_to_rejected
    def test_awaiting_approval_to_rejected(self):
        assert validate_transition(IncidentState.AWAITING_APPROVAL, IncidentState.REJECTED) is True

    # Function: test_awaiting_approval_to_failed
    def test_awaiting_approval_to_failed(self):
        assert validate_transition(IncidentState.AWAITING_APPROVAL, IncidentState.FAILED) is True

    # Function: test_rejected_to_classified
    def test_rejected_to_classified(self):
        # Re-plan after rejection
        assert validate_transition(IncidentState.REJECTED, IncidentState.CLASSIFIED) is True

    # Function: test_rejected_to_failed
    def test_rejected_to_failed(self):
        assert validate_transition(IncidentState.REJECTED, IncidentState.FAILED) is True


class TestInvalidTransitions:
    """Test that invalid transitions return False."""

    # Function: test_new_cannot_go_to_dispatched
    def test_new_cannot_go_to_dispatched(self):
        assert validate_transition(IncidentState.NEW, IncidentState.DISPATCHED) is False

    # Function: test_new_cannot_go_to_resolved
    def test_new_cannot_go_to_resolved(self):
        assert validate_transition(IncidentState.NEW, IncidentState.RESOLVED) is False

    # Function: test_classified_cannot_go_to_resolved_directly
    def test_classified_cannot_go_to_resolved_directly(self):
        assert validate_transition(IncidentState.CLASSIFIED, IncidentState.RESOLVED) is False

    # Function: test_classified_cannot_go_to_in_progress_directly
    def test_classified_cannot_go_to_in_progress_directly(self):
        assert validate_transition(IncidentState.CLASSIFIED, IncidentState.IN_PROGRESS) is False

    # Function: test_dispatched_cannot_go_to_resolved_directly
    def test_dispatched_cannot_go_to_resolved_directly(self):
        assert validate_transition(IncidentState.DISPATCHED, IncidentState.RESOLVED) is False

    # Function: test_dispatched_cannot_go_to_awaiting_approval_directly
    def test_dispatched_cannot_go_to_awaiting_approval_directly(self):
        assert validate_transition(IncidentState.DISPATCHED, IncidentState.AWAITING_APPROVAL) is False

    # Function: test_resolved_cannot_go_to_in_progress
    def test_resolved_cannot_go_to_in_progress(self):
        assert validate_transition(IncidentState.RESOLVED, IncidentState.IN_PROGRESS) is False

    # Function: test_resolved_cannot_go_to_classified
    def test_resolved_cannot_go_to_classified(self):
        assert validate_transition(IncidentState.RESOLVED, IncidentState.CLASSIFIED) is False

    # Function: test_failed_has_no_valid_transitions
    def test_failed_has_no_valid_transitions(self):
        for state in IncidentState:
            assert validate_transition(IncidentState.FAILED, state) is False

    # Function: test_awaiting_approval_cannot_go_to_in_progress
    def test_awaiting_approval_cannot_go_to_in_progress(self):
        assert validate_transition(IncidentState.AWAITING_APPROVAL, IncidentState.IN_PROGRESS) is False

    # Function: test_rejected_cannot_go_to_resolved_directly
    def test_rejected_cannot_go_to_resolved_directly(self):
        assert validate_transition(IncidentState.REJECTED, IncidentState.RESOLVED) is False

    # Function: test_blocked_to_in_progress_not_allowed
    def test_blocked_to_in_progress_not_allowed(self):
        assert validate_transition(IncidentState.BLOCKED, IncidentState.IN_PROGRESS) is False


class TestStateMachineCompleteness:
    """Ensure all states are covered in the transition map."""

    # Function: test_all_states_have_transition_entry
    def test_all_states_have_transition_entry(self):
        """Every IncidentState should appear as a key in VALID_TRANSITIONS."""
        for state in IncidentState:
            assert state in VALID_TRANSITIONS, f"State {state} missing from VALID_TRANSITIONS"

    # Function: test_failed_is_terminal
    def test_failed_is_terminal(self):
        assert VALID_TRANSITIONS[IncidentState.FAILED] == set()

    # Function: test_any_state_can_transition_to_failed
    def test_any_state_can_transition_to_failed(self):
        """All non-terminal states must allow transition to FAILED."""
        non_terminal = [s for s in IncidentState if s != IncidentState.FAILED]
        for state in non_terminal:
            assert IncidentState.FAILED in VALID_TRANSITIONS[state], (
                f"State {state} cannot transition to FAILED"
            )


class TestStateEnumValues:
    # Function: test_state_values_are_strings
    def test_state_values_are_strings(self):
        for state in IncidentState:
            assert isinstance(state.value, str)

    # Function: test_all_expected_states_exist
    def test_all_expected_states_exist(self):
        expected = {
            "NEW", "CLASSIFIED", "DISPATCHED", "IN_PROGRESS",
            "AWAITING_APPROVAL", "RESOLVED", "ESCALATED", "BLOCKED",
            "REJECTED", "FAILED",
        }
        actual = {s.value for s in IncidentState}
        assert expected == actual
