import pytest

from app.formatting import DARK_SYNTAX, highlight, segment_message
def test_python_highlighting_is_preserved():
    rendered = highlight(
        "def greet(name):\n    return name",
        "python",
        DARK_SYNTAX,
    )


    assert f'color:{DARK_SYNTAX["keyword"]}' in rendered

@pytest.mark.parametrize("language", [
    "html", "xml", "css", "scss", "yaml", "yml",
    "toml", "md", "markdown",
])
def test_formats_without_dedicated_highlighting_remain_plain(language):
    code = "<tag> value: 'hello'"

    assert highlight(code, language, DARK_SYNTAX) == (
        "&lt;tag&gt; value: &#x27;hello&#x27;"
    )

@pytest.mark.parametrize("language", [
    "html", "xml", "css", "scss", "yaml", "yml",
    "toml", "md", "markdown", "diff", "dockerfile",
    "ini", "rb", "ruby", "php", "lua", "r",
])
def test_requested_languages_are_recognized(language):
    rendered = highlight(
        "if value < 10:\n    return value",
        language,
        DARK_SYNTAX,
    )
    assert rendered
    assert "&lt;" in rendered or language in {
        "diff", "dockerfile", "ini", "markdown", "md"
    }


@pytest.mark.parametrize("fence,language", [
    ("~~~", "python"),
    ("````", "python"),
    ("   ```", "python"),
])
def test_supported_fence_styles(fence, language):
    message = f"{fence}{language}\nprint(1)\n{fence}\n"

    segments = segment_message(message)

    assert len(segments) == 1
    assert segments[0]["kind"] == "code"
    assert segments[0]["lang"] == language
    assert segments[0]["text"] == "print(1)"
    assert segments[0]["open"] is False

def test_indented_fence_strips_opening_fence_indentation():
    message = "  ```python\n  print(1)\n    value = 2\n  ```\n"

    segments = segment_message(message)

    assert len(segments) == 1
    assert segments[0]["text"] == "print(1)\n  value = 2"
def test_shorter_nested_fence_does_not_close_outer_fence():
    message = "````python\n```\nprint(1)\n````\n"

    segments = segment_message(message)

    assert len(segments) == 1
    assert segments[0]["text"] == "```\nprint(1)"


def test_diff_additions_and_removals_use_existing_palette():
    rendered = highlight(
        "+added\n-removed\n unchanged",
        "diff",
        DARK_SYNTAX,
    )

    assert f'color:{DARK_SYNTAX["keyword"]}' in rendered
    assert f'color:{DARK_SYNTAX["comment"]}' in rendered