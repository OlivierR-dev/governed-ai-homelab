"""Tests for tools/lint_style.py (standard library unittest)."""

import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import lint_style  # noqa: E402

FIXTURE = ROOT / "tests" / "fixtures" / "tics.md"

BLOCKING_RULES = {"dash", "announcement", "inflated-word", "emoji-line-start", "multiple-punctuation"}
WARNING_RULES = {"rhetorical-question", "short-paragraphs", "parentheses"}

CLEAN = (
    "Jeudi soir, j'ai relu les quatre dernières PR de l'agent (c'est un rituel). "
    "La CI était verte sur trois d'entre elles, et la quatrième avait un test sauté.\n"
    "\n"
    "Du coup j'ai regardé pourquoi. Le test dépendait d'un fichier absent de la branche, "
    "et l'agent l'avait signalé dans son commentaire, avec la commande et sa sortie.\n"
)


def rules(findings, level=None):
    return {f.rule for f in findings if level is None or f.level == level}


def run_main(*args):
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = lint_style.main(list(args))
    return code, buf.getvalue()


class NegativeProbe(unittest.TestCase):
    """The fixture must be rejected, and by every blocking rule."""

    def test_fixture_is_rejected(self):
        code, out = run_main(str(FIXTURE))
        self.assertEqual(code, 1, out)

    def test_fixture_triggers_every_blocking_rule(self):
        findings = lint_style.lint_text(FIXTURE.read_text(encoding="utf-8"), str(FIXTURE))
        self.assertEqual(rules(findings, lint_style.BLOCKING), BLOCKING_RULES)

    def test_fixture_triggers_every_paragraph_warning(self):
        findings = lint_style.lint_text(FIXTURE.read_text(encoding="utf-8"), str(FIXTURE))
        self.assertTrue(WARNING_RULES <= rules(findings, lint_style.WARNING))

    def test_fixture_finds_every_announcement_and_word(self):
        findings = lint_style.lint_text(FIXTURE.read_text(encoding="utf-8"), str(FIXTURE))
        messages = " ".join(f.message for f in findings)
        for label in lint_style.ANNOUNCEMENTS:
            self.assertIn(repr(label), messages, label)
        for label, _ in lint_style.INFLATED:
            self.assertIn(f"({label})", messages, label)


class CleanText(unittest.TestCase):
    def test_clean_text_has_no_finding(self):
        self.assertEqual(lint_style.lint_text(CLEAN), [])

    def test_clean_file_exits_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "propre.md"
            p.write_text(CLEAN, encoding="utf-8")
            code, _ = run_main(str(p), "--kind", "none")
        self.assertEqual(code, 0)


class BlockingRules(unittest.TestCase):
    def check(self, text, rule):
        self.assertIn(rule, rules(lint_style.lint_text(text), lint_style.BLOCKING), text)

    def test_em_and_en_dash(self):
        self.check("Un mot — un autre.", "dash")
        self.check("De 2024 – 2025.", "dash")

    def test_hyphen_is_allowed(self):
        self.assertEqual(lint_style.lint_text("Un mot-clé, et laissez-le."), [])

    def test_announcement_case_and_apostrophe(self):
        self.check("SOYONS HONNÊTES, ça a coincé.", "announcement")
        self.check("Et c’est là que ça casse.", "announcement")

    def test_inflated_inflections(self):
        for text in ("Des étapes cruciales.", "Une règle essentielle.", "Ça boostera tout.",
                     "Au coeur du sujet.", "Un vrai game-changer.", "C'est véritablement neuf."):
            self.check(text, "inflated-word")

    def test_inflated_word_boundaries(self):
        # "levier" must not match inside an unrelated word, "paradigmes" must match.
        self.assertNotIn("inflated-word", rules(lint_style.lint_text("Le soulevier est un faux mot.")))
        self.check("Deux paradigmes.", "inflated-word")

    def test_emoji_at_line_start_only(self):
        self.check("💡 Une idée.", "emoji-line-start")
        self.check("1. 👉 Une étape.", "emoji-line-start")
        self.assertNotIn("emoji-line-start", rules(lint_style.lint_text("Une idée 💡 en fin.")))

    def test_multiple_punctuation(self):
        for text in ("Non !!", "Ah ??", "Quoi ?!", "Hein !?"):
            self.check(text, "multiple-punctuation")

    def test_code_is_ignored(self):
        text = "Voici du code :\n\n```\nx = a — b  # essentiel !!\n```\n\nEt `crucial` en ligne.\n"
        self.assertEqual(rules(lint_style.lint_text(text), lint_style.BLOCKING), set())

    def test_line_numbers(self):
        findings = lint_style.lint_text("Ligne une.\n\nLigne — trois.\n")
        self.assertEqual([(f.line, f.rule) for f in findings], [(3, "dash")])


class Warnings(unittest.TestCase):
    def warnings(self, text, kind=None):
        return rules(lint_style.lint_text(text, kind=kind), lint_style.WARNING)

    def test_rhetorical_question_end_of_paragraph(self):
        self.assertIn("rhetorical-question", self.warnings("Et le résultat ? Une CI verte."))
        self.assertNotIn("rhetorical-question", self.warnings("Et le résultat ? Une CI verte. Puis la suite, longue."))

    def test_short_paragraphs_threshold(self):
        two = "Un.\n\nDeux.\n"
        three = "Un.\n\nDeux.\n\nTrois.\n"
        self.assertNotIn("short-paragraphs", self.warnings(two))
        self.assertIn("short-paragraphs", self.warnings(three))

    def test_headings_lists_hashtags_are_not_short_paragraphs(self):
        text = "# Titre\n\n- un\n\n- deux\n\n#ia #sdlc #gouvernance\n"
        self.assertNotIn("short-paragraphs", self.warnings(text))

    def test_parentheses(self):
        self.assertNotIn("parentheses", self.warnings("Un (a) deux (b)."))
        self.assertIn("parentheses", self.warnings("Un (a) deux (b) trois (c)."))

    def test_length_post(self):
        self.assertIn("length", self.warnings("Trop court.", kind="post"))
        self.assertNotIn("length", self.warnings(" ".join(["mot"] * 150), kind="post"))
        self.assertIn("length", self.warnings(" ".join(["mot"] * 251), kind="post"))

    def test_length_article(self):
        self.assertIn("length", self.warnings(" ".join(["mot"] * 599), kind="article"))
        self.assertNotIn("length", self.warnings(" ".join(["mot"] * 900), kind="article"))

    def test_warnings_do_not_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "posts" / "fr" / "court.md"
            p.parent.mkdir(parents=True)
            p.write_text("Trop court, mais propre.\n", encoding="utf-8")
            code, out = run_main(str(p))
        self.assertEqual(code, 0)
        self.assertIn("[length]", out)


class Cli(unittest.TestCase):
    def test_missing_file_is_usage_error(self):
        code, _ = run_main("n-existe-pas.md")
        self.assertEqual(code, 2)

    def test_directory_recursion(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp) / "posts" / "fr"
            d.mkdir(parents=True)
            (d / "a.md").write_text("Un mot — un autre.\n", encoding="utf-8")
            (d / ".gitkeep").write_text("", encoding="utf-8")
            code, out = run_main(str(Path(tmp) / "posts"))
        self.assertEqual(code, 1)
        self.assertIn("1 file(s)", out)

    def test_kind_guess(self):
        self.assertEqual(lint_style.guess_kind(Path("posts/fr/x.md")), "post")
        self.assertEqual(lint_style.guess_kind(Path("brouillons/articles/en/x.md")), "article")
        self.assertIsNone(lint_style.guess_kind(Path("tests/fixtures/tics.md")))


if __name__ == "__main__":
    unittest.main()
