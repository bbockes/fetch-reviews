from app.models import Quote, Theme
from app.report_quality import check_report_quality


def _theme(title: str, *, positive: bool, count: int = 2) -> Theme:
    return Theme(
        mention_count=count,
        title=title,
        quotes=[
            Quote(
                author="A",
                storefront="US",
                rating=5 if positive else 1,
                text="Sample quote text.",
                excerpt="Sample quote text.",
            )
        ],
    )


def test_quality_passes_with_loves_and_pains(audiopen_reviews):
    loves = [
        _theme("Voice transcription", positive=True),
        _theme("Easy to use", positive=True),
    ]
    pains = [_theme("Subscription too expensive", positive=False)]
    result = check_report_quality(loves, pains, audiopen_reviews)
    assert result.ok


def test_quality_fails_without_pains_when_one_stars(audiopen_reviews):
    loves = [_theme("Voice transcription", positive=True)]
    result = check_report_quality(loves, [], audiopen_reviews)
    assert not result.ok
    assert "no_pain_themes" in result.issues
