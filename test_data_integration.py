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
    """Create test events for evaluation - covering all 5 event types"""

    events = [
        # 1. Health Emergency
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

        # 2. Major Event
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
        ),

        # 3. Weather Extreme
        DetectedEvent(
            event_type="weather_extreme",
            title="Heatwave Warning Issued for Dublin",
            description="Met Éireann has issued a high temperature warning for Dublin and surrounding areas. Temperatures expected to reach 28°C over the next 5 days, unusually high for this time of year.",
            severity="medium",
            urgency="immediate",
            location="Dublin, Ireland",
            confidence="high",
            event_date="2024-11-16",
            published_at="2024-11-15T06:00:00Z",
            source_url="https://test.example.com/heatwave",
            key_facts=[
                "Temperatures 10°C above seasonal average",
                "UV index very high",
                "Public advised to stay hydrated",
                "Elderly and children at risk"
            ],
            potential_relevance="Increased demand for sun protection, hydration products, and allergy medications"
        ),

        # 4. Supply Disruption
        DetectedEvent(
            event_type="supply_disruption",
            title="Port Delays Affecting Pharmaceutical Shipments",
            description="Major delays at Dublin Port are affecting pharmaceutical and medical supply shipments. Customs processing times have tripled due to new regulations, creating supply chain bottlenecks.",
            severity="high",
            urgency="immediate",
            location="Dublin Port, Ireland",
            confidence="high",
            event_date="2024-11-15",
            published_at="2024-11-15T07:00:00Z",
            source_url="https://test.example.com/port-delays",
            key_facts=[
                "Processing delays of 3-5 days",
                "Affects imports from UK and EU",
                "Multiple pharmaceutical suppliers impacted",
                "Port working to resolve issues"
            ],
            potential_relevance="Potential stock shortages of imported pharmaceutical products, need to contact suppliers"
        ),

        # 5. Viral Trend
        DetectedEvent(
            event_type="viral_trend",
            title="Magnesium Supplements Trending on Social Media",
            description="Magnesium supplements are going viral on TikTok and Instagram with #MagnesiumMiracle trending. Influencers claiming benefits for sleep, anxiety, and energy. Demand surging across Irish retailers.",
            severity="medium",
            urgency="immediate",
            location="Ireland (Online)",
            confidence="medium",
            event_date="2024-11-15",
            published_at="2024-11-15T11:00:00Z",
            source_url="https://test.example.com/magnesium-trend",
            key_facts=[
                "Over 2M views in 48 hours",
                "Sales up 400% at major retailers",
                "Primarily targeting 18-35 age group",
                "Multiple Irish influencers promoting"
            ],
            potential_relevance="Opportunity to capitalize on viral trend if magnesium supplements in stock, risk of stockouts"
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
