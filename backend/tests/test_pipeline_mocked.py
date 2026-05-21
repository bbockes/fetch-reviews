from app.analyze_pipeline import run_analysis_pipeline
from app.models import ReportResult


def test_pipeline_produces_themes_and_takeaways(mock_llm, audiopen_reviews):
    metadata = {
        "app_name": "AudioPen: AI Voice to Text",
        "app_url": "https://apps.apple.com/us/app/id6502638001",
        "primary_genre": "Productivity",
        "genres": ["Productivity"],
        "description": "Voice notes app.",
    }
    result = run_analysis_pipeline(
        audiopen_reviews,
        "6502638001",
        metadata,
    )
    assert isinstance(result, ReportResult)
    assert result.summary.app_name == "AudioPen: AI Voice to Text"
    assert len(result.loves) >= 1
    assert len(result.pain_points) >= 1
    assert len(result.takeaways) >= 4
    titles = [t.title.lower() for t in result.takeaways]
    assert not any(t == "unknown" for t in titles)


def test_jobs_require_llm(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    from app.analyze_pipeline import require_llm_configured
    from app.errors import AnalysisError
    import pytest

    with pytest.raises(AnalysisError):
        require_llm_configured()
