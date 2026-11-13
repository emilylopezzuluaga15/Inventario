from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 30)

RAW = Path(__file__).parent / "Data" / "raw" / "datos_estudiantes.csv"
PROCESSED = Path(__file__).parent / "Data" / "processed"
GRAFICOS = PROCESSED / "graficos"

# Valores válidos de cada columna categórica (la forma correcta de escribirlos).
VALIDOS = {
    "programa": ["Administración de Empresas", "Contaduría Pública", "Derecho", "Psicología",
                 "Ingeniería de Sistemas", "Ingeniería Industrial", "Enfermería", "Diseño Gráfico"],
    "jornada": ["Diurna", "Nocturna", "Fin de semana"],
    "genero": ["Femenino", "Masculino"],
    "ciudad_procedencia": ["Bogotá", "Medellín", "Cali", "Bucaramanga", "Rionegro",
                           "Barranquilla", "Otra ciudad"],
}

DECISIONES = []


def registrar(paso, columna, accion, filas, justificacion):
    """Guarda una decisión para la tabla de decisiones. Ya está escrita: solo úsala."""
    DECISIONES.append({
        "paso": paso, "columna": columna, "accion": accion,
        "filas_afectadas": int(filas), "justificacion": justificacion,
    })


def explorar(df):
    """Paso 1 del Word: primera mirada al dataset.

    Muestra la forma, los tipos y los nulos de cada columna, las estadísticas
    numéricas, y los valores de las columnas programa, jornada, genero y estado.
    Pregunta: ¿alguna columna numérica aparece como texto? ¿Por qué crees que pasa?
    """
    print(df.shape)
    df.info()
    print(df.describe())
    for col in ["programa", "jornada", "genero", "estado"]:
        print(df[col].value_counts())



def auditar(df):
    """Paso 2 del Word: buscar problemas sin corregirlos todavía.

    Revisa: nulos reales, faltantes disfrazados ('-', 999), valores imposibles
    (edad, promedio, horas), duplicados y formatos de fecha.
    Pregunta: ¿cuál de estos problemas afecta más el análisis? ¿Por qué?
    """
    print("Nulos:")
    print(df.isnull().sum())
    print("Guiones en asistencia:", (df["asistencia_pct"] == "-").sum())
    print("Guiones en horas de trabajo:", (df["horas_trabajo_semana"] == "-").sum())
    print("999 en distancia:", (df["distancia_km"] == 999).sum())
    print("Edades raras:", ((df["edad"] < 15) | (df["edad"] > 60)).sum())
    print("Promedios fuera de 0-5:", ((df["promedio_acumulado"] < 0) | (df["promedio_acumulado"] > 5)).sum())
    print("Asistencia con %:", df["asistencia_pct"].str.contains("%").sum())
    print("Fechas con /:", df["fecha_matricula"].str.contains("/").sum())
    print("Duplicados:", df.duplicated().sum())



def convertir_numericos(df):
    """Paso 3 del Word: columnas que deberían ser numéricas, pero llegan como texto.

    Pistas: quitar el símbolo % con str.replace; reemplazar '-' por nulo;
    convertir con pd.to_numeric(..., errors="coerce"); reemplazar 999 por nulo en distancia_km.
    Registra cada conversión con registrar().
    """
    n = df["asistencia_pct"].str.contains("%|-").sum()
    df["asistencia_pct"] = df["asistencia_pct"].str.replace("%", "").replace("-", np.nan)
    df["asistencia_pct"] = pd.to_numeric(df["asistencia_pct"], errors="coerce")
    registrar("numericos", "asistencia_pct", "quitar % y pasar '-' a nulo", n,
              "Era texto por el % y los guiones. Si no se convierte no se pueden sacar cuartiles.")

    n = (df["horas_trabajo_semana"] == "-").sum()
    df["horas_trabajo_semana"] = pd.to_numeric(df["horas_trabajo_semana"].replace("-", np.nan), errors="coerce")
    registrar("numericos", "horas_trabajo_semana", "pasar '-' a nulo y convertir", n,
              "El guion es un dato faltante. Se arregla en el paso 8 segun si el estudiante trabaja.")

    n = (df["distancia_km"] == 999).sum()
    df["distancia_km"] = df["distancia_km"].replace(999, np.nan)
    registrar("numericos", "distancia_km", "999 a nulo", n,
              "999 es un codigo de sin dato, no una distancia real.")
    return df


def unificar_categorias(df):
    """Paso 4 del Word: errores tipográficos en columnas categóricas.

    Pistas: primero df[col].str.strip().str.lower(); después .replace(diccionario)
    con las variantes que encontraste con value_counts(). Los valores correctos están en VALIDOS.
    Pregunta: ¿qué variantes son el mismo valor? ¿Hay alguna que no debas unificar?
    """
    cambios = {
        "programa": {"ingenieria de sistemas": "Ingeniería de Sistemas", "psicologia": "Psicología"},
        "jornada": {"diurna": "Diurna", "nocturna": "Nocturna"},
        "genero": {"femenino": "Femenino", "masculino": "Masculino", "f": "Femenino", "m": "Masculino"},
        "ciudad_procedencia": {"bogota": "Bogotá", "bogotá": "Bogotá", "medellin": "Medellín"},
    }
    for col in cambios:
        antes = df[col].copy()
        df[col] = df[col].str.strip()
        # primero los valores correctos de VALIDOS, que quedan igual
        for valido in VALIDOS[col]:
            df.loc[df[col].str.lower() == valido.lower(), col] = valido
        df[col] = df[col].str.lower().replace(cambios[col])
        for valido in VALIDOS[col]:
            df.loc[df[col].str.lower() == valido.lower(), col] = valido
        n = (antes != df[col]).sum()
        registrar("categorias", col, "unificar escritura", n,
                  "Son el mismo valor escrito distinto (mayusculas, espacios, tildes). Separados partirian los grupos.")
    return df


def convertir_fechas(df):
    """Paso 5 del Word: fechas escritas en dos formatos.

    Pista: intenta el formato AAAA-MM-DD y luego DD/MM/AAAA, cada uno con errors="coerce",
    y junta los resultados con fillna(). Registra cuántas fechas tenían el segundo formato.
    """
    fecha1 = pd.to_datetime(df["fecha_matricula"], format="%Y-%m-%d", errors="coerce")
    fecha2 = pd.to_datetime(df["fecha_matricula"], format="%d/%m/%Y", errors="coerce")
    df["fecha_matricula"] = fecha1.fillna(fecha2)
    registrar("fechas", "fecha_matricula", "convertir los dos formatos a fecha", fecha1.isnull().sum(),
              "Habia fechas en AAAA-MM-DD y en DD/MM/AAAA. Se leen por separado y se juntan.")
    return df


def eliminar_duplicados(df):
    """Paso 6 del Word: filas repetidas.

    Pregunta: ¿podrían existir dos estudiantes distintos con todos los datos iguales?
    Pista: duplicated() y drop_duplicates(), con reset_index(drop=True).
    """
    n = df.duplicated().sum()
    df = df.drop_duplicates().reset_index(drop=True)
    registrar("duplicados", "todas", "eliminar filas repetidas", n,
              "Dos estudiantes distintos no pueden tener las 23 columnas iguales, incluido el id.")
    return df


def tratar_faltantes(df):
    """Paso 7 del Word: decidir qué hacer con los nulos reales.

    Preguntas:
    - ¿Puedes inventar una nota? ¿Qué pasa si imputas el promedio?
    - Para ciudad o tipo de colegio, ¿conviene eliminar la fila o marcar el dato como 'Sin dato'?
    - motivo_retiro tiene muchos nulos. ¿Son errores? (Pista: ¿para quiénes aplica esa columna?)
    """
    n = df["promedio_acumulado"].isnull().sum()
    df = df.dropna(subset=["promedio_acumulado"]).reset_index(drop=True)
    registrar("faltantes", "promedio_acumulado", "eliminar filas", n,
              "Una nota no se puede inventar y imputar el promedio cambiaria los resultados.")

    for col in ["ciudad_procedencia", "tipo_colegio"]:
        n = df[col].isnull().sum()
        df[col] = df[col].fillna("Sin dato")
        registrar("faltantes", col, "rellenar con 'Sin dato'", n,
                  "Son pocos y es una categoria; asi no se pierde la fila.")

    registrar("faltantes", "motivo_retiro", "dejar nulo", df["motivo_retiro"].isnull().sum(),
              "No es error: solo aplica a los desertores.")
    registrar("faltantes", "distancia_km", "dejar nulo", df["distancia_km"].isnull().sum(),
              "No se usa en las preguntas y no conviene inventar la distancia.")
    registrar("faltantes", "asistencia_pct", "dejar nulo", df["asistencia_pct"].isnull().sum(),
              "No se sabe la asistencia real. Esas filas quedan fuera de la pregunta 5.")
    return df


def tratar_imposibles(df):
    """Paso 8 del Word: valores que no pueden existir.

    Preguntas:
    - La escala del promedio es de 0 a 5. ¿Qué harías con un 45?
    - Una edad de 150 años es un error. ¿Qué valor pondrías en su lugar?
    - Si el estudiante no trabaja, ¿cuántas horas de trabajo tiene? ¿Cómo lo aplicas en código?
    """
    # edad
    mala = (df["edad"] < 15) | (df["edad"] > 60)
    mediana = df.loc[~mala, "edad"].median()
    df.loc[mala, "edad"] = mediana
    registrar("imposibles", "edad", "reemplazar por la mediana", mala.sum(),
              "Edades de 150 o 12 anos son errores de registro.")

    # promedio fuera de la escala 0 a 5
    mala = (df["promedio_acumulado"] > 5) | (df["promedio_acumulado"] < 0)
    n = mala.sum()
    df = df[~mala].reset_index(drop=True)
    registrar("imposibles", "promedio_acumulado", "eliminar filas", n,
              "Valores como 45, 62 o 78 no son notas validas y no se sabe cual era la real.")

    # horas de trabajo
    n = (df["trabaja"] == "no").sum()
    df.loc[df["trabaja"] == "no", "horas_trabajo_semana"] = 0
    registrar("imposibles", "horas_trabajo_semana", "poner 0 si no trabaja", n,
              "Si no trabaja, las horas son 0.")

    mediana = df.loc[df["trabaja"] == "sí", "horas_trabajo_semana"].median()
    mala = (df["horas_trabajo_semana"] > 100) | ((df["trabaja"] == "sí") & df["horas_trabajo_semana"].isnull())
    df.loc[mala, "horas_trabajo_semana"] = mediana
    registrar("imposibles", "horas_trabajo_semana", "reemplazar por la mediana de quienes trabajan", mala.sum(),
              "Mas de 100 horas a la semana no es realista; la mediana casi no cambia con valores extremos.")
    return df


def crear_variables(df):
    """Paso 9 del Word: variables nuevas para el análisis.

    Crea:
    - desertor: True si estado es 'desertor', False si no.
    - cuartil_asistencia: divide asistencia_pct en cuatro grupos iguales con pd.qcut.
    Pregunta: ¿por qué conviene usar cuartiles y no valores exactos de asistencia?
    """
    df["desertor"] = df["estado"].eq("desertor")
    df["cuartil_asistencia"] = pd.qcut(df["asistencia_pct"], 4, labels=["Q1 baja", "Q2", "Q3", "Q4 alta"])
    registrar("variables", "desertor y cuartil_asistencia", "crear columnas", len(df),
              "Los cuartiles dejan cuatro grupos parecidos en tamano y son mas faciles de comparar que cada valor.")
    return df


def _guardar_fig(nombre):
    GRAFICOS.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(GRAFICOS / nombre, dpi=120)
    plt.show()
    plt.close()


def grafico_faltantes(df):
    """Gráfico 1: mapa de faltantes del dataset original.

    Pista: sns.heatmap(df.isnull(), cbar=False)
    """
    plt.figure(figsize=(12, 5))
    # gris = dato presente, rojo = dato faltante
    sns.heatmap(df.isnull(), cbar=False, cmap=["lightgray", "red"], yticklabels=False)
    plt.xticks(rotation=60, ha="right")
    plt.title("Mapa de faltantes (dataset original): rojo = nulo")
    _guardar_fig("mapa_faltantes.png")


def grafico_distribuciones(antes, despues):
    """Gráfico 2: boxplots de promedio_acumulado y edad, antes y después de limpiar.

    Pregunta: ¿qué cambió en cada distribución? ¿Por qué?
    """
    fig, ax = plt.subplots(2, 2, figsize=(10, 7))
    for i, col in enumerate(["promedio_acumulado", "edad"]):
        sns.boxplot(y=antes[col], ax=ax[i, 0]).set_title(f"{col} - antes")
        sns.boxplot(y=despues[col], ax=ax[i, 1]).set_title(f"{col} - después")
    _guardar_fig("distribuciones_antes_despues.png")


def grafico_tasa_programa(df):
    """Gráfico 3: tasa de deserción por programa.

    Pista: df.groupby("programa")["desertor"].mean()
    """
    t = df.groupby("programa")["desertor"].mean().sort_values()
    t.plot.barh(figsize=(9, 5))
    plt.xlabel("Tasa de deserción")
    plt.title("Tasa de deserción por programa")
    _guardar_fig("tasa_desercion_por_programa.png")


def grafico_tasa_asistencia(df):
    """Gráfico 4: tasa de deserción por cuartil de asistencia.

    Pista: df.groupby("cuartil_asistencia", observed=True)["desertor"].mean()
    """
    t = df.groupby("cuartil_asistencia", observed=True)["desertor"].mean()
    t.plot.bar(figsize=(7, 5), rot=0)
    plt.ylabel("Tasa de deserción")
    plt.title("Tasa de deserción por cuartil de asistencia")
    _guardar_fig("tasa_desercion_por_asistencia.png")


def responder_preguntas(df):
    """Paso 10 del Word: las cinco preguntas de la institución.

    Cada pregunta debe imprimir el resultado con el número de estudiantes por grupo.
    Pregunta 1: ¿Qué programa presenta la tasa de deserción más alta?
    Pregunta 2: ¿Hay diferencia en la deserción entre becados y no becados?
    Pregunta 3: ¿Qué jornada tiene el menor promedio acumulado?
    Pregunta 4: ¿Cuántas materias reprobadas tienen en promedio los desertores frente a los activos?
                (Excluye a los graduados.)
    Pregunta 5: ¿La deserción aumenta conforme baja la asistencia?
                (Usa cuartil_asistencia.)
    """
    def tasa(col):
        return df.groupby(col, observed=True).agg(
            tasa=("desertor", "mean"), estudiantes=("desertor", "size"),
            asistencia_prom=("asistencia_pct", "mean")).round(3)

    print("\nP1. Tasa de deserción por programa:")
    print(tasa("programa").sort_values("tasa", ascending=False))
    print("\nP2. Becados vs no becados:")
    print(tasa("beca"))
    print("\nP3. Promedio acumulado por jornada:")
    print(df.groupby("jornada").agg(promedio=("promedio_acumulado", "mean"),
                                    estudiantes=("jornada", "size")).round(3).sort_values("promedio"))
    print("\nP4. Materias reprobadas (sin graduados):")
    print(df[df["estado"] != "graduado"].groupby("estado").agg(
        reprobadas_prom=("materias_reprobadas", "mean"), estudiantes=("estado", "size")).round(3))
    print("\nP5. Deserción por cuartil de asistencia:")
    print(tasa("cuartil_asistencia"))


def guardar(df):
    """Paso 11 del Word: guardar el dataset limpio y la tabla de decisiones. Ya está escrito."""
    PROCESSED.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED / "dataset_limpio.csv", index=False)
    pd.DataFrame(DECISIONES).to_csv(PROCESSED / "decisiones.csv", index=False)
    print(f"\nDataset limpio guardado: {df.shape[0]} filas, {df.shape[1]} columnas.")


def main():
    original = pd.read_csv(RAW)
    df = original.copy()

    explorar(df)
    auditar(df)
    grafico_faltantes(df)

    df = convertir_numericos(df)
    df = unificar_categorias(df)
    df = convertir_fechas(df)
    df = eliminar_duplicados(df)
    df = tratar_faltantes(df)
    df = tratar_imposibles(df)
    df = crear_variables(df)

    grafico_distribuciones(original, df)
    grafico_tasa_programa(df)
    grafico_tasa_asistencia(df)

    responder_preguntas(df)
    print("\nTabla de decisiones:")
    print(pd.DataFrame(DECISIONES))
    guardar(df)


if __name__ == "__main__":
    main()
