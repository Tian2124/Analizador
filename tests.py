import unittest
from analyzer import normalize_text, tokenize, TextAnalyzer


# ---------------------------------------------------------------------------
# Pruebas de normalización
# ---------------------------------------------------------------------------

class TestNormalizeText(unittest.TestCase):

    def test_lowercase(self):
        self.assertEqual(normalize_text("HOLA MUNDO"), "hola mundo")

    def test_removes_punctuation(self):
        result = normalize_text("Hola, Mundo!! Python 3.")
        self.assertEqual(result, "hola mundo python 3")

    def test_extra_spaces_collapsed(self):
        self.assertEqual(normalize_text("  hola   mundo  "), "hola mundo")

    def test_preserves_accents_and_enie(self):
        result = normalize_text("Murciélago y ñoño")
        self.assertEqual(result, "murciélago y ñoño")

    def test_removes_parentheses_and_brackets(self):
        result = normalize_text("texto (entre) [corchetes]")
        self.assertEqual(result, "texto entre corchetes")

    def test_empty_string(self):
        self.assertEqual(normalize_text(""), "")

    def test_only_punctuation(self):
        self.assertEqual(normalize_text("!!!???..."), "")

    def test_mixed_numbers_and_letters(self):
        result = normalize_text("Python3 es genial!")
        self.assertEqual(result, "python3 es genial")

    def test_type_error(self):
        with self.assertRaises(TypeError):
            normalize_text(123)  # type: ignore


# ---------------------------------------------------------------------------
# Pruebas de tokenización
# ---------------------------------------------------------------------------

class TestTokenize(unittest.TestCase):

    def test_basic_split(self):
        self.assertEqual(tokenize("hola mundo python"), ["hola", "mundo", "python"])

    def test_empty_string(self):
        self.assertEqual(tokenize(""), [])

    def test_single_word(self):
        self.assertEqual(tokenize("python"), ["python"])

    def test_numbers_included(self):
        tokens = tokenize("python 3 es la version 3")
        self.assertIn("3", tokens)


# ---------------------------------------------------------------------------
# Pruebas de TextAnalyzer (conteo + query)
# ---------------------------------------------------------------------------

class TestTextAnalyzer(unittest.TestCase):

    # 11 tokens: el gato come el pescado y el perro come el hueso
    SAMPLE = "el gato come el pescado y el perro come el hueso"

    def setUp(self):
        self.analyzer = TextAnalyzer(self.SAMPLE)
        self.analyzer.analyze()

    def test_total_tokens(self):
        self.assertEqual(len(self.analyzer.tokens), 11)

    def test_unique_tokens(self):
        # el, gato, come, pescado, y, perro, hueso = 7 únicas
        self.assertEqual(len(self.analyzer.unique_tokens), 7)

    def test_count_el(self):
        self.assertEqual(self.analyzer.counts["el"], 4)

    def test_count_come(self):
        self.assertEqual(self.analyzer.counts["come"], 2)

    def test_count_gato(self):
        self.assertEqual(self.analyzer.counts["gato"], 1)

    def test_query_found(self):
        result = self.analyzer.query("el")
        self.assertIn("4", result)
        self.assertIn("36.36%", result)

    def test_query_not_found(self):
        result = self.analyzer.query("dinosaurio")
        self.assertIn("no se encontró", result)

    def test_query_rare(self):
        result = self.analyzer.query("gato")
        self.assertIn("rara", result)

    def test_query_common(self):
        # Para que sea "común" necesitamos freq >= 5;
        # usemos un texto donde "el" aparece 5 veces
        text = "el el el el el gato come pescado"
        a = TextAnalyzer(text)
        a.analyze()
        result = a.query("el")
        self.assertIn("común", result)

    def test_empty_text_raises(self):
        with self.assertRaises(ValueError):
            TextAnalyzer("").analyze()

    def test_only_punctuation_raises(self):
        with self.assertRaises(ValueError):
            a = TextAnalyzer("!!!")
            a.analyze()

    def test_report_contains_total(self):
        report = self.analyzer.report()
        self.assertIn("10", report)


# ---------------------------------------------------------------------------
# Pruebas rápidas con asserts (complementarias)
# ---------------------------------------------------------------------------

def run_asserts():
    """Asserts documentados como pruebas de humo rápidas."""

    # Normalización básica
    assert normalize_text("Hola, Mundo!! Python 3.") == "hola mundo python 3", \
        "normalize_text: puntuación y mayúsculas"

    # Tokenización
    assert tokenize("hola mundo") == ["hola", "mundo"], \
        "tokenize: split simple"
    assert tokenize("") == [], \
        "tokenize: cadena vacía"

    # Conteo correcto
    a = TextAnalyzer("la casa es la casa bonita")
    a.analyze()
    assert a.counts["la"] == 2, "counts: 'la' debe aparecer 2 veces"
    assert a.counts["casa"] == 2, "counts: 'casa' debe aparecer 2 veces"
    assert a.counts["bonita"] == 1, "counts: 'bonita' debe aparecer 1 vez"
    assert len(a.unique_tokens) == 4, "unique_tokens: 4 palabras únicas"

    print("✓ Todos los asserts rápidos pasaron correctamente.")


if __name__ == "__main__":
    print("=" * 50)
    print("   PRUEBAS RÁPIDAS CON ASSERTS")
    print("=" * 50)
    run_asserts()
    print()
    print("=" * 50)
    print("   PRUEBAS UNITTEST")
    print("=" * 50)
    unittest.main(verbosity=2)