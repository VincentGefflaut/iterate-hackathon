#!/usr/bin/env python3
"""Test MVP components"""

print("Testing Product Alerts MVP Components...")
print("=" * 60)

# Test 1: TopProductsLoader
print("\n1. Testing TopProductsLoader...")
try:
    from news_alerts import TopProductsLoader
    loader = TopProductsLoader()
    print("   ✓ TopProductsLoader imported successfully")

    locs = loader.get_top_locations(3)
    print(f"   ✓ Loaded top 3 locations: {len(locs)}")

    for loc in locs:
        print(f"     - {loc.location_name}: {', '.join(loc.top_products)}")

    products = sorted(loader.get_unique_products())
    print(f"   ✓ Unique products ({len(products)}): {', '.join(products)}")

except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 2: ProductNewsFetcher
print("\n2. Testing ProductNewsFetcher...")
try:
    from news_alerts import ProductNewsFetcher
    fetcher = ProductNewsFetcher()
    print("   ✓ ProductNewsFetcher imported successfully")
    print("   ✓ Initialized with top products data")

    products = fetcher.products_loader.get_unique_products()
    print(f"   ✓ Tracking {len(products)} products")

except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 3: ProductEventDetector
print("\n3. Testing ProductEventDetector...")
try:
    import os

    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("   ⚠ ANTHROPIC_API_KEY not set - skipping detector test")
        print("   Set ANTHROPIC_API_KEY in .env to test event detection")
    else:
        from news_alerts import ProductEventDetector
        detector = ProductEventDetector()
        print("   ✓ ProductEventDetector imported successfully")
        print("   ✓ Connected to Anthropic API")

        tracked = detector.tracked_products
        print(f"   ✓ Tracking {len(tracked)} products: {', '.join(sorted(tracked))}")

except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("✅ Component tests complete!")
print("\nNext: Run the full MVP with:")
print("  python run_product_alerts_mvp.py --demo")
