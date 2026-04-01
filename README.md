# Analizador de Texto 📄

Analiza un texto y genera un reporte con métricas (frecuencias, tokens únicos, top 10 palabras, longitud promedio, etc.)
con consultas interactivas por palabra.

## Estructura del proyecto
```
text_analyzer/
├── analyzer.py   ← código principal (funciones + clase TextAnalyzer)
├── tests.py      ← pruebas unittest + asserts documentados
├── sample.txt    ← texto de ejemplo para prueba en modo archivo
└── README.md
```
## Cómo ejecutar

### Modo interactivo (consola)

Se presentará un menú:
1. **Modo archivo** → ingresar la ruta a un `.txt`
2. **Modo consola** → pegar texto directamente; finalizar con `END`

Ejemplo sesión:
```
Opción (1/2): 2
Pegue o escriba el texto...
El rápido zorro salta sobre el perro.
END

[reporte impreso]

Palabra: zorro
'zorro': frecuencia = 1, porcentaje = 12.50%, clasificación = rara (aparece una sola vez)

Palabra: exit
¡Hasta luego!
```

### Modo archivo

```bash
python3 analyzer.py
# Opción 1
# Ruta: sample.txt
```

## Decisiones de diseño
 Normalización  `re.sub(r"[^\w\s]", " ")` → conserva letras Unicode (acentos, ñ) y dígitos sin librerías externas 
 Conteos  `collections.Counter` (subclase de `dict`) → O(n) tiempo, API limpia 
 Únicos  `set` → membresía O(1) y eliminación automática de duplicados 
 Empates (más larga/corta)  Se listan todas las palabras empatadas, ordenadas alfabéticamente 
 Umbrales query  rara ≤ 1, común ≥ 5; ajustables en `TextAnalyzer.query()` 
 Errores  `try/except` específico en cada punto de fallo (carga, análisis, consulta) 

---
## Ejemplo de reporte
```
=======================================================
           REPORTE DE ANÁLISIS DE TEXTO
=======================================================
  Total de tokens          : 312
  Tokens únicos            : 145
  Longitud promedio        : 5.23 caracteres
  Palabra(s) más larga(s)  : extraordinariamente (18 chars)
  Palabra(s) más corta(s)  : a, e, o, y (1 chars)

  TOP 10 TOKENS MÁS FRECUENTES
  -----------------------------------
   1. de                    28  (9.0%)
   2. la                    21  (6.7%)
   ...
=======================================================
```
