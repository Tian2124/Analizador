import re
from collections import Counter

def normalize_text(text: str) -> str:
    """
    Procesa el texto de entrada aplicando una normalización básica:

    - Convierte todo a minúsculas
    - Elimina signos de puntuación
    - Conserva letras Unicode (incluye acentos y ñ) y números
    - Sustituye múltiples espacios por uno solo

    Se utiliza una expresión regular con clase negada para evitar
    dependencias externas y mantener compatibilidad con Unicode.
    """
    if not isinstance(text, str):
        raise TypeError("Se esperaba una cadena de texto (str).")

    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    text = text.replace("_", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize(text: str) -> list[str]:
    """
    Divide el texto normalizado en una lista de tokens.

    Si el texto está vacío, devuelve una lista vacía.
    """
    if not text:
        return []
    return text.split()


# ---------------------------------------------------------------------------
# Clase principal de análisis
# ---------------------------------------------------------------------------

class TextAnalyzer:
    """
    Representa el motor de análisis de texto.

    Atributos principales:
        original_text   → Texto original proporcionado por el usuario
        normalized_text → Texto tras aplicar normalización
        tokens          → Lista de palabras detectadas
        counts          → Frecuencia de cada token (Counter)
        unique_tokens   → Conjunto de tokens únicos
    """

    def __init__(self, text: str) -> None:
        if not text or not text.strip():
            raise ValueError("El texto proporcionado está vacío.")

        self.original_text: str = text
        self.normalized_text: str = ""
        self.tokens: list[str] = []
        self.counts: Counter = Counter()
        self.unique_tokens: set[str] = set()

    # ------------------------------------------------------------------
    # Proceso de análisis
    # ------------------------------------------------------------------

    def analyze(self) -> None:
        """
        Ejecuta el flujo completo de análisis:

        1. Normalización del texto
        2. Tokenización
        3. Conteo de frecuencias
        """
        self.normalized_text = normalize_text(self.original_text)
        self.tokens = tokenize(self.normalized_text)

        if not self.tokens:
            raise ValueError("No se encontraron palabras válidas tras la normalización.")

        self.counts = Counter(self.tokens)
        self.unique_tokens = set(self.tokens)

    # ------------------------------------------------------------------
    # Generación de reporte
    # ------------------------------------------------------------------

    def report(self) -> str:
        """
        Construye un resumen estadístico del texto analizado.

        Devuelve el reporte como string y también lo imprime en consola.
        """
        if not self.tokens:
            raise RuntimeError("Debe ejecutar analyze() antes de generar el reporte.")

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
            "              INFORME DE ANÁLISIS TEXTUAL",
            "=" * 55,
            f"  Total de palabras        : {total}",
            f"  Palabras únicas          : {unique}",
            f"  Longitud promedio        : {avg_len:.2f} caracteres",
            f"  Palabra(s) más extensa(s): {', '.join(longest)} ({max_len} caracteres)",
            f"  Palabra(s) más corta(s)  : {', '.join(shortest)} ({min_len} caracteres)",
            "",
            "  TOP 10 PALABRAS MÁS FRECUENTES",
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
    # Consulta de palabras
    # ------------------------------------------------------------------

    def query(self, word: str) -> str:
        """
        Devuelve información detallada sobre una palabra específica.

        Clasificación:
        - rara → aparece una sola vez
        - común → aparece cinco o más veces
        - frecuencia media → valores intermedios
        """
        if not self.tokens:
            raise RuntimeError("Debe ejecutar analyze() antes de realizar consultas.")

        word_norm = normalize_text(word)

        if not word_norm:
            return "La entrada no contiene caracteres válidos para analizar."

        freq = self.counts.get(word_norm, 0)
        total = len(self.tokens)

        if freq == 0:
            return f"La palabra '{word_norm}' no aparece en el texto."

        pct = freq / total * 100

        if freq == 1:
            label = "rara (aparece una sola vez)"
        elif freq >= 5:
            label = "común (frecuencia alta)"
        else:
            label = "frecuencia media"

        return (
            f"Palabra: '{word_norm}'\n"
            f"Frecuencia: {freq}\n"
            f"Porcentaje: {pct:.2f}%\n"
            f"Clasificación: {label}"
        )


# ---------------------------------------------------------------------------
# Métodos de carga de texto
# ---------------------------------------------------------------------------

def load_from_file(path: str) -> str:
    """
    Carga el contenido de un archivo de texto (.txt).

    Maneja errores comunes como:
    - Archivo inexistente
    - Ruta inválida
    - Falta de permisos
    - Archivo vacío
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"No se encontró el archivo especificado: '{path}'")
    except IsADirectoryError:
        raise IsADirectoryError(f"La ruta indicada corresponde a un directorio: '{path}'")
    except PermissionError:
        raise PermissionError(f"No se tienen permisos para leer: '{path}'")
    except OSError as e:
        raise OSError(f"Ocurrió un error al leer el archivo: {e}")

    if not content.strip():
        raise ValueError("El archivo está vacío.")

    return content


def load_from_console() -> str:
    """
    Permite ingresar texto manualmente desde la consola.

    La captura finaliza cuando el usuario escribe 'END'
    en una línea independiente.
    """
    print("Ingrese o pegue el texto a analizar.")
    print("Escriba 'END' en una nueva línea para finalizar.\n")

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
        raise ValueError("No se ingresó contenido para analizar.")

    return text


# ---------------------------------------------------------------------------
# Interfaz de línea de comandos (CLI)
# ---------------------------------------------------------------------------

def main() -> None:
    print("\n╔══════════════════════════════════════╗")
    print("║        ANALIZADOR DE TEXTO CON         ║")
    print("║          ESTRUCTURAS BASICAS           ║")
    print("╚════════════════════════════════════════╝\n")

    print("Elija un método de entrada:")
    print("  1) Analizar archivo (.txt)")
    print("  2) Ingresar texto manualmente")

    mode = input("\nSeleccione una opción : ").strip()

    text = ""

    try:
        if mode == "1":
            path = input("Ingrese la ruta del archivo: ").strip()
            text = load_from_file(path)
            print(f"\n✔ Archivo cargado correctamente ({len(text)} caracteres).\n")

        elif mode == "2":
            text = load_from_console()
            print(f"\n✔ Texto recibido correctamente ({len(text)} caracteres).\n")

        else:
            print("Opción no válida. El programa finalizará.")
            return

    except (FileNotFoundError, IsADirectoryError, PermissionError,
            OSError, ValueError) as e:
        print(f"\n✖ Error al cargar el texto: {e}")
        return

    try:
        analyzer = TextAnalyzer(text)
        analyzer.analyze()
    except (TypeError, ValueError, RuntimeError) as e:
        print(f"\n✖ Error durante el análisis: {e}")
        return

    print()
    analyzer.report()

    print("\nPuede consultar palabras individuales.")
    print("Escriba 'exit' para finalizar.\n")

    while True:
        word = input("Consulta: ").strip()

        if word.lower() == "exit":
            print("\nPrograma finalizado. Gracias por utilizar el analizador.")
            break

        if not word:
            print("Ingrese una palabra válida.")
            continue

        print(analyzer.query(word))


if __name__ == "__main__":
    main()