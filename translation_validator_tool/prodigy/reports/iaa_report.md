# 📊 Reporte de Inter-Annotator Agreement (IAA)

**Dataset:** `pos_v2`  
**Fecha:** C:\Users\infor\Desktop\manu\LACUNA\guarani-corpus-lacuna-uni\translation_validator_tool

---

## 🎯 Resumen General


- **Acuerdo promedio (simple):** 12.98%
- **Cohen's Kappa promedio:** 0.305
- **Total de pares evaluados:** 3

### Interpretación de Kappa:
- `< 0.20`: Acuerdo pobre
- `0.21 - 0.40`: Acuerdo bajo
- `0.41 - 0.60`: Acuerdo moderado
- `0.61 - 0.80`: Acuerdo sustancial
- `0.81 - 1.00`: Acuerdo casi perfecto

---

## 👥 Acuerdo por Par de Anotadores


### `pos_v2-bob` ↔ `pos_v2-carlos`

- **Acuerdo simple:** 10.00%
- **Cohen's Kappa:** 0.556
- **Oraciones comparadas:** 2

**Acuerdo por etiqueta:**

| Etiqueta | Acuerdo |
|----------|--------|
| SUJETO | 16.67% |
| VERBO | 0.00% |
| OBJETO | 0.00% |
| SUSTANTIVO | 0.00% |


### `pos_v2-alice` ↔ `pos_v2-bob`

- **Acuerdo simple:** 17.84%
- **Cohen's Kappa:** 0.284
- **Oraciones comparadas:** 6

**Acuerdo por etiqueta:**

| Etiqueta | Acuerdo |
|----------|--------|
| SUJETO | 36.11% |
| VERBO | 16.67% |
| ADJETIVO | 0.00% |
| SUSTANTIVO | 0.00% |
| PRONOMBRE | 0.00% |
| OBJETO | 0.00% |
| PREPOSICIÓN | 0.00% |
| ADVERBIO | 0.00% |


### `pos_v2-alice` ↔ `pos_v2-carlos`

- **Acuerdo simple:** 11.11%
- **Cohen's Kappa:** 0.075
- **Oraciones comparadas:** 1

**Acuerdo por etiqueta:**

| Etiqueta | Acuerdo |
|----------|--------|
| SUJETO | 20.00% |
| VERBO | 0.00% |

---

## ⚠️ Outliers Detectados

Los siguientes anotadores tienen acuerdo promedio < 0.50 (considerado bajo):

- **pos_v2-alice**: Kappa promedio = 0.179
- **pos_v2-bob**: Kappa promedio = 0.420
- **pos_v2-carlos**: Kappa promedio = 0.315

**Recomendación:** Revisar guidelines con estos anotadores o proveer más ejemplos.

---

## 📈 Recomendaciones

1. **Kappa < 0.60:** Revisar guidelines y hacer sesión de calibración con anotadores.
2. **Desacuerdo en etiquetas específicas:** Añadir ejemplos claros en POS_ANNOTATION_GUIDE.md.
3. **Outliers detectados:** Sesión 1-on-1 para entender dudas.
4. **Alto acuerdo (>0.80):** Puede reducirse overlap (usar annotations_per_task=1.5).

---

*Generado por `calculate_iaa.py`*
