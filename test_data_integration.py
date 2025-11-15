#!/usr/bin/env python3
"""
Test script to verify data integration with Context Matcher

Creates mock events and tests both heuristic and data-driven matching.
"""

import json
from datetime import date
from pathlib import Path

from news_alerts.models import DetectedEvent
from news_alerts.event_storage import EventStorage
from news_alerts.context_matcher import ContextMatcher


def create_test_events():
    """Create test events for evaluation"""

    events = [
        DetectedEvent(
            event_type="health_emergency",
            title="Norovirus Outbreak in Dublin",
            description="Health officials report a significant increase in norovirus cases across Dublin. Hospitals seeing surge in patients with gastrointestinal symptoms. Public advised to maintain strict hygiene practices.",
            severity="high",
            urgency="immediate",
            location="Dublin, Ireland",
            confidence="high",
            event_date="2024-11-15",
            published_at="2024-11-15T10:30:00Z",
            source_url="https://test.example.com/norovirus",
            key_facts=[
                "Cases up 300% in past week",
                "Primarily affecting Dublin city centre",
                "Peak season for norovirus",
                "Hospitals urging prevention measures"
            ],
            potential_relevance="High demand expected for OTC gastrointestinal medications, hand sanitizers, and hygiene products"
        ),
        DetectedEvent(
            event_type="major_event",
            title="Major Concert at 3Arena Dublin",
            description="Sold-out concert this weekend at 3Arena with 15,000 attendees expected. Event runs Friday and Saturday nights.",
            severity="medium",
            urgency="within_week",
            location="3Arena, Dublin",
            confidence="high",
            event_date="2024-11-16",
            published_at="2024-11-15T08:00:00Z",
            expected_attendance=15000,
            source_url="https://test.example.com/concert",
            key_facts=[
                "15,000 attendees per night",
                "Located near O'Connell Street",
                "Weekend event",
                "High foot traffic expected"
            ],
            potential_relevance="Increased demand for pain relievers, first aid supplies, and convenience items near venue"
        )
    ]

    return events


def test_heuristic_matching():
    """Test heuristic-based matching"""
    print("=" * 80)
    print("TEST 1: HEURISTIC-BASED MATCHING")
    print("=" * 80)
    print()

    matcher = ContextMatcher(use_real_data=False, enhance_with_llm=False)

    events = create_test_events()

    for i, event in enumerate(events, 1):
        print(f"\nEvaluating Event {i}: {event.title}")
        print("-" * 80)

        alert = matcher.evaluate_single_event(event)

        if alert:
            print(f"✅ ALERT GENERATED")
            print(f"   Severity: {alert.severity}")
            print(f"   Confidence: {alert.decision.confidence:.2f}")
            print(f"   Affected Categories: {', '.join(alert.affected_categories) if alert.affected_categories else 'None'}")
            print(f"\n   Decision Reasoning:")
            for reason in alert.decision.reasoning:
                print(f"     • {reason}")
        else:
            print("❌ No alert generated")

    print("\n" + "=" * 80)
    print()


def test_data_driven_matching():
    """Test data-driven matching"""
    print("=" * 80)
    print("TEST 2: DATA-DRIVEN MATCHING")
    print("=" * 80)
    print()

    matcher = ContextMatcher(use_real_data=True, enhance_with_llm=False)

    # Check if data was loaded successfully
    if not matcher.use_real_data:
        print("⚠️  Data-driven mode not available (data files not found)")
        print("   This is expected if you don't have the data files.")
        print("   The system gracefully falls back to heuristic mode.")
        return

    print("✅ Data-driven mode successfully initialized!")
    print()

    events = create_test_events()

    for i, event in enumerate(events, 1):
        print(f"\nEvaluating Event {i}: {event.title}")
        print("-" * 80)

        alert = matcher.evaluate_single_event(event)

        if alert:
            print(f"✅ ALERT GENERATED")
            print(f"   Severity: {alert.severity}")
            print(f"   Confidence: {alert.decision.confidence:.2f}")
            print(f"   Affected Categories: {', '.join(alert.affected_categories) if alert.affected_categories else 'None'}")
            print(f"\n   Decision Reasoning (with data insights):")
            for reason in alert.decision.reasoning:
                print(f"     • {reason}")
        else:
            print("❌ No alert generated")

    print("\n" + "=" * 80)
    print()


def main():
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "DATA INTEGRATION TEST SUITE" + " " * 31 + "║")
    print("╚" + "=" * 78 + "╝")
    print()

    # Test heuristic matching
    test_heuristic_matching()

    # Test data-driven matching
    test_data_driven_matching()

    print("✅ All tests completed!")
    print()


if __name__ == "__main__":
    main()
