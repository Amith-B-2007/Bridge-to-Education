"""
Prompt templates for the Study Hub.

Keep prompts in their own file so non-coders on the team can edit them
without touching the views/logic.
"""

LANGUAGE_NAMES = {
    "en": "English",
    "hi": "Hindi (हिन्दी)",
    "ta": "Tamil (தமிழ்)",
    "te": "Telugu (తెలుగు)",
    "bn": "Bengali (বাংলা)",
    "kn": "Kannada (ಕನ್ನಡ)",
    "mr": "Marathi (मराठी)",
}


def build_lesson_prompt(grade, syllabus, subject, chapter, language="en"):
    """
    Returns (system_prompt, user_prompt) for generating a lesson summary.

    The system prompt tells the AI WHO it is.
    The user prompt asks for a specific lesson.
    """
    lang_name = LANGUAGE_NAMES.get(language, "English")

    system_prompt = f"""You are a friendly school teacher for Indian students.
You teach Grade {grade} students following the {syllabus} syllabus.
ALWAYS reply in {lang_name}.
Use simple words a {grade}th grade student can understand.
Use real-life Indian examples (rupees, cricket, festivals, foods).
"""

    user_prompt = f"""Write a complete lesson summary for:
Subject: {subject}
Chapter: {chapter}

The summary MUST have these sections in this exact order:
## Introduction
(1 short paragraph - what is this chapter about?)

## Key Concepts
(3 to 5 bullet points - the main ideas)

## Worked Example
(1 simple example with step-by-step solution)

## Real-Life Connection
(How is this used in everyday life in India?)

## Summary
(2 lines summarizing what was learned)

Format the output as Markdown.
"""
    return system_prompt, user_prompt


def build_keypoints_prompt(summary_text, language="en"):
    """Asks the AI to extract bullet-point key takeaways from a generated summary."""
    lang_name = LANGUAGE_NAMES.get(language, "English")
    return (
        f"You extract study points in {lang_name}.",
        f"""Read this lesson summary and give me exactly 5 short bullet-point
key takeaways (each under 15 words). Reply ONLY with the bullets, one per line,
starting with "- ". No headers, no extra text.

Lesson:
{summary_text}
""",
    )
