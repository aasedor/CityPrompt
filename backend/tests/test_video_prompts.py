import pytest

from app.services.video_prompts import (
    ENTOURAGE,
    LOOK_STYLE_IDS,
    MAX_LOOK_SHEET_PROMPT_CHARS,
    STUDENT_NOTE_MAX_CHARS,
    VACE_NEGATIVE_PROMPT,
    VIDEO_LOOKS,
    build_grok_look_prompt,
    build_look_sheet,
    build_omni_look_prompt,
    build_vace_depth_prompt,
    sanitize_student_note,
)

LEGACY_LOCK_MARKERS = ("B1", "P1", "CHECKSUM", "SOURCE POLICY", "LOCK", "Image1", "@Video1")


def test_every_look_is_short_and_shares_the_image_vocabulary():
    assert set(LOOK_STYLE_IDS) == set(VIDEO_LOOKS)
    assert "photorealistic" in VIDEO_LOOKS and "night" in VIDEO_LOOKS
    for look_id, sentence in VIDEO_LOOKS.items():
        assert len(sentence) <= 160, f"{look_id} is {len(sentence)} characters"
        assert not sentence.endswith("."), look_id
        assert sentence[0].islower(), look_id


def test_entourage_table_is_exhaustive():
    assert set(ENTOURAGE) == {(False, False), (True, False), (False, True), (True, True)}
    assert ENTOURAGE[(False, False)] == "No people or vehicles."


def test_omni_prompt_names_one_change_and_keeps_everything_else():
    prompt = build_omni_look_prompt(build_look_sheet(look_style="photorealistic", add_people=True))

    assert prompt.startswith("Change only the look of this video: photographic finish")
    assert "Keep everything else the same" in prompt
    assert "Same camera path, speed and timing as the source video." in prompt
    assert "A few pedestrians at natural scale" in prompt
    assert prompt.endswith("No text, labels or markers.")
    assert "reference image" not in prompt
    for marker in LEGACY_LOCK_MARKERS:
        assert marker not in prompt
    assert len(prompt) <= MAX_LOOK_SHEET_PROMPT_CHARS


def test_omni_prompt_mentions_the_anchor_only_when_attached():
    anchored = build_omni_look_prompt(build_look_sheet(anchor_attached=True))
    assert "Match the materials, light and colour of the reference image." in anchored


def test_every_look_fits_the_budget_with_a_maximal_note():
    note = "x" * (STUDENT_NOTE_MAX_CHARS + 50)
    for look_id in LOOK_STYLE_IDS:
        sheet = build_look_sheet(look_style=look_id, add_people=True, add_vehicles=True, student_note=note)
        assert len(sheet.note) <= STUDENT_NOTE_MAX_CHARS + 1  # trailing period
        assert len(build_omni_look_prompt(sheet)) <= MAX_LOOK_SHEET_PROMPT_CHARS
        assert len(build_grok_look_prompt(sheet)) <= MAX_LOOK_SHEET_PROMPT_CHARS
        positive, negative = build_vace_depth_prompt(sheet)
        assert len(positive) <= MAX_LOOK_SHEET_PROMPT_CHARS
        assert negative == VACE_NEGATIVE_PROMPT


def test_student_note_is_one_clean_line():
    assert sanitize_student_note("  keep the\n\n  plaza   busy ") == "keep the plaza busy."
    assert sanitize_student_note("Already ends?") == "Already ends?"
    assert sanitize_student_note(None) == ""
    long_note = sanitize_student_note("word " * 100)
    assert len(long_note) <= STUDENT_NOTE_MAX_CHARS + 1
    prompt = build_omni_look_prompt(build_look_sheet(student_note="rain on the market street"))
    assert "Note: rain on the market street." in prompt


def test_vace_prompt_describes_the_end_state_and_the_depth_authority():
    positive, negative = build_vace_depth_prompt(build_look_sheet(look_style="night"))

    assert positive.startswith("Blue-hour night:")
    assert "where the depth video places it" in positive
    assert "Same camera path, speed and timing as the control video." in positive
    assert "extra buildings" in negative and "text" in negative
    for marker in LEGACY_LOCK_MARKERS:
        assert marker not in positive


def test_grok_prompt_has_no_reference_sentence():
    prompt = build_grok_look_prompt(build_look_sheet(look_style="winter", anchor_attached=True))
    assert "reference image" not in prompt
    assert "Keep everything else the same" in prompt


def test_unknown_look_is_rejected():
    with pytest.raises(ValueError, match="Unknown video look"):
        build_look_sheet(look_style="neon")
