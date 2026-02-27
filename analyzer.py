import re
from collections import Counter


# ---------------------------------------------------------------------------
# Funciones de utilidad
# ---------------------------------------------------------------------------

def normalize_text(text: str) -> str:
    """
    Normaliza el texto:
      - convierte a minúsculas
      - elimina puntuación común (.,;:!?()[]{}"'¡¿-_/\\|@#$%^&*+=<>~`)
      - colapsa espacios múltiples
      - mantiene letras (incluyendo acentos/ñ) y números

    Decisión: usamos re.sub con una clase de caracteres negada para
    conservar letras Unicode y dígitos sin depender de nltk/unidecode.
    """
    if not isinstance(text, str):
        raise TypeError("El texto debe ser una cadena de caracteres (str).")

    text = text.lower()
    # Eliminar cualquier carácter que NO sea letra Unicode, dígito o espacio
    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    # \w incluye dígitos, letras y guión_bajo; quitamos guión_bajo por separado
    text = text.replace("_", " ")
    # Colapsar espacios múltiples
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize(text: str) -> list[str]:
    """
    Divide el texto normalizado en tokens (palabras/números).
    Retorna lista vacía si el texto está vacío.
    """
    if not text:
        return []
    return text.split()


# ---------------------------------------------------------------------------
# Clase principal
# ---------------------------------------------------------------------------

class TextAnalyzer:
    """
    Encapsula el análisis completo de un texto.

    Atributos:
        original_text  : texto tal como fue cargado
        normalized_text: texto después de normalize_text()
        tokens         : lista de tokens
        counts         : Counter con frecuencias de tokens
        unique_tokens  : set de tokens únicos
    """

    def __init__(self, text: str) -> None:
        if not text or not text.strip():
            raise ValueError("El texto no puede estar vacío.")
        self.original_text: str = text
        self.normalized_text: str = ""
        self.tokens: list[str] = []
        self.counts: Counter = Counter()
        self.unique_tokens: set[str] = set()

    # ------------------------------------------------------------------
    # Análisis
    # ------------------------------------------------------------------

    def analyze(self) -> None:
        """Ejecuta la pipeline completa: normalizar → tokenizar → contar."""
        self.normalized_text = normalize_text(self.original_text)
        self.tokens = tokenize(self.normalized_text)
        if not self.tokens:
            raise ValueError("El texto no contiene tokens válidos tras la normalización.")
        self.counts = Counter(self.tokens)
        self.unique_tokens = set(self.tokens)

    # ------------------------------------------------------------------
    # Reporte
    # ------------------------------------------------------------------

    def report(self) -> str:
        """
        Genera y retorna un reporte de texto con las métricas principales.
        También imprime el reporte en consola.
        """
        if not self.tokens:
            raise RuntimeError("Debe llamar a analyze() antes de report().")

        total = len(self.tokens)
        unique = len(self.unique_tokens)
        top10 = self.counts.most_common(10)
        avg_len = sum(len(t) for t in self.tokens) / total

        lengths = {len(t) for t in self.tokens}
        max_len = max(lengths)
        min_len = min(lengths)
        longest = sorted({t for t in self.unique_tokens if len(t) == max_len})
        shortest = sorted({t for t in self.unique_tokens if len(t) == min_len})

        lines = [
            "=" * 55,
            "           REPORTE DE ANÁLISIS DE TEXTO",
            "=" * 55,
            f"  Total de tokens          : {total}",
            f"  Tokens únicos            : {unique}",
            f"  Longitud promedio        : {avg_len:.2f} caracteres",
            f"  Palabra(s) más larga(s)  : {', '.join(longest)} ({max_len} chars)",
            f"  Palabra(s) más corta(s)  : {', '.join(shortest)} ({min_len} chars)",
            "",
            "  TOP 10 TOKENS MÁS FRECUENTES",
            "  " + "-" * 35,
        ]
        for rank, (token, count) in enumerate(top10, start=1):
            pct = count / total * 100
            lines.append(f"  {rank:>2}. {token:<20} {count:>5}  ({pct:.1f}%)")
        lines.append("=" * 55)

        report_str = "\n".join(lines)
        print(report_str)
        return report_str

    # ------------------------------------------------------------------
    # Consulta interactiva
    # ------------------------------------------------------------------

    def query(self, word: str) -> str:
        """
        Consulta la frecuencia de una palabra y devuelve un string descriptivo.

        Umbrales:
          - "rara"   : frecuencia == 1  (aparece una sola vez)
          - "común"  : frecuencia >= 5  (aparece 5 o más veces)
          - en otro caso: "frecuencia media"
        Justificación: umbrales ajustables según corpus; valores 1/5 son
        conservadores para textos cortos típicos de aula.
        """
        if not self.tokens:
            raise RuntimeError("Debe llamar a analyze() antes de query().")

        word_norm = normalize_text(word)
        if not word_norm:
            return "La palabra ingresada no contiene caracteres válidos."

        freq = self.counts.get(word_norm, 0)
        total = len(self.tokens)

        if freq == 0:
            return f"'{word_norm}' no se encontró en el texto."

        pct = freq / total * 100
        if freq == 1:
            label = "rara (aparece una sola vez)"
        elif freq >= 5:
            label = "común (frecuencia ≥ 5)"
        else:
            label = "frecuencia media"

        result = (
            f"'{word_norm}': frecuencia = {freq}, "
            f"porcentaje = {pct:.2f}%, clasificación = {label}"
        )
        return result


# ---------------------------------------------------------------------------
# Carga de texto (dos modos)
# ---------------------------------------------------------------------------

def load_from_file(path: str) -> str:
    """
    Lee un archivo .txt y retorna su contenido como str.
    Lanza excepciones descriptivas ante errores comunes.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"No se encontró el archivo: '{path}'")
    except IsADirectoryError:
        raise IsADirectoryError(f"La ruta apunta a un directorio, no a un archivo: '{path}'")
    except PermissionError:
        raise PermissionError(f"Sin permisos de lectura para: '{path}'")
    except OSError as e:
        raise OSError(f"Error al leer el archivo: {e}")

    if not content.strip():
        raise ValueError("El archivo existe pero está vacío.")
    return content


def load_from_console() -> str:
    """
    Permite pegar texto en consola.
    La entrada finaliza cuando el usuario escribe 'END' en una línea sola.
    """
    print("Pegue o escriba el texto a continuación.")
    print("Cuando termine, escriba 'END' en una línea nueva y presione Enter.\n")
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line.strip().upper() == "END":
            break
        lines.append(line)
    text = "\n".join(lines)
    if not text.strip():
        raise ValueError("No se ingresó ningún texto.")
    return text


# ---------------------------------------------------------------------------
# Interfaz principal (CLI)
# ---------------------------------------------------------------------------

def main() -> None:
    print("\n╔══════════════════════════════════╗")
    print("║     ANALIZADOR DE TEXTO v1.0     ║")
    print("╚══════════════════════════════════╝\n")

    # --- Selección de modo ---
    print("Seleccione el modo de entrada:")
    print("  1. Leer desde archivo (.txt)")
    print("  2. Ingresar texto por consola")
    mode = input("\nOpción (1/2): ").strip()

    text = ""
    try:
        if mode == "1":
            path = input("Ruta del archivo: ").strip()
            text = load_from_file(path)
            print(f"\n✓ Archivo cargado correctamente ({len(text)} caracteres).\n")
        elif mode == "2":
            text = load_from_console()
            print(f"\n✓ Texto recibido ({len(text)} caracteres).\n")
        else:
            print("Opción no válida. Saliendo.")
            return
    except (FileNotFoundError, IsADirectoryError, PermissionError,
            OSError, ValueError) as e:
        print(f"\n✗ Error al cargar el texto: {e}")
        return

    # --- Análisis ---
    try:
        analyzer = TextAnalyzer(text)
        analyzer.analyze()
    except (TypeError, ValueError, RuntimeError) as e:
        print(f"\n✗ Error durante el análisis: {e}")
        return

    # --- Reporte ---
    print()
    analyzer.report()

    # --- Consultas interactivas ---
    print("\nIngrese una palabra para consultar su frecuencia (o 'exit' para salir).")
    while True:
        word = input("\nPalabra: ").strip()
        if word.lower() == "exit":
            print("¡Hasta luego!")
            break
        if not word:
            print("Por favor ingrese una palabra.")
            continue
        print(analyzer.query(word))


if __name__ == "__main__":
    main()