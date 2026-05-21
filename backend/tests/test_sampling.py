from app.review_sampling import min_mentions, stratified_review_sample


def test_min_mentions_thresholds():
    assert min_mentions(10) == 1
    assert min_mentions(30) == 2
    assert min_mentions(100) == 2


def test_stratified_sample_includes_low_ratings():
    reviews = []
    for i in range(10):
        reviews.append(
            {
                "id": f"low-{i}",
                "rating": 1,
                "title": "Bad",
                "text": "x" * 20,
                "storefront": "us",
            }
        )
    for i in range(30):
        reviews.append(
            {
                "id": f"high-{i}",
                "rating": 5,
                "title": "Great",
                "text": "x" * 200,
                "storefront": "us",
            }
        )
    sample = stratified_review_sample(reviews, limit=15)
    ratings = {r["rating"] for r in sample}
    assert 1 in ratings
