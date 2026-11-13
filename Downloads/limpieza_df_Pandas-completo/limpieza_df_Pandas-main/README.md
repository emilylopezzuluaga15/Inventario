# Taller práctico proyecto integrador: calidad de datos para la retención estudiantil

Una institución de educación superior quiere entender qué factores están asociados a la deserción, para diseñar estrategias de retención tempranas. Antes de responder preguntas de análisis, el equipo de datos debe garantizar que la información sea confiable. Este taller trabaja justo ese paso: auditar, limpiar y documentar los datos, y después responder cinco preguntas con esos datos limpios.

Los datos son sintéticos. Fueron generados para el taller y no corresponden a estudiantes reales.

## Requisitos

- Python 3.10 o superior
- Git
- Lo visto en los talleres de Pandas y de limpieza de datos


## Estructura del proyecto

```
proyecto/
├── analisis_desercion.py   Script principal. Tiene un TODO por cada paso.
├── requirements.txt        Versiones de las librerías.
├── LEEME_ambiente.txt      Pasos para crear el ambiente virtual.
├── README.md               Este archivo.
├── .gitignore              Archivos que Git no debe subir.
└── Data/
    ├── raw/
    │   └── datos_estudiantes.csv   Dataset original. No lo modifiques.
    └── processed/
        ├── .gitkeep                Mantiene la carpeta en el repositorio.
        ├── dataset_limpio.csv      Lo genera el script. No se sube (está en .gitignore).
        ├── decisiones.csv          Lo genera el script. Sí se sube.
        └── graficos/               Lo genera el script. Sí se sube.


````
## Mis decisiones y respuestas

### 0. Diccionario de datos

| Columna | Tipo | Descripción | Rol |
|---|---|---|---|
| id_estudiante | texto | Código del estudiante | identificación |
| programa | categórica | Programa que estudia | explicativa |
| facultad | categórica | Facultad del programa | explicativa |
| jornada | categórica | Diurna, Nocturna o Fin de semana | explicativa |
| semestre | numérica | Semestre que cursa (1 a 10) | explicativa |
| promedio_acumulado | numérica | Nota promedio, de 0 a 5 | explicativa |
| creditos_aprobados | numérica | Créditos que ha aprobado | explicativa |
| materias_reprobadas | numérica | Cuántas materias ha perdido | explicativa |
| asistencia_pct | numérica | Porcentaje de asistencia a clase | explicativa |
| sesiones_tutoria | numérica | Tutorías a las que asistió | explicativa |
| cambios_programa | numérica | Veces que cambió de programa | explicativa |
| estrato | numérica | Estrato socioeconómico (1 a 6) | explicativa |
| beca | categórica | Si tiene beca (sí/no) | explicativa |
| trabaja | categórica | Si trabaja (sí/no) | explicativa |
| horas_trabajo_semana | numérica | Horas que trabaja por semana | explicativa |
| distancia_km | numérica | Distancia de su casa a la institución | explicativa |
| edad | numérica | Edad en años | explicativa |
| genero | categórica | Femenino o Masculino | explicativa |
| ciudad_procedencia | categórica | Ciudad de donde viene | explicativa |
| tipo_colegio | categórica | Colegio público o privado | explicativa |
| fecha_matricula | fecha | Fecha en que se matriculó | explicativa |
| estado | categórica | activo, graduado o desertor | resultado |
| motivo_retiro | categórica | Por qué se retiró (solo desertores) | resultado |

### 1. Diagnóstico de calidad

El archivo original tiene 10.150 filas y 23 columnas. Esto fue lo que encontré:

- Nulos: promedio_acumulado (304), distancia_km (199), tipo_colegio (152) y ciudad_procedencia (103). motivo_retiro tiene 6.877 nulos, pero eso es normal porque solo aplica a los desertores.
- Faltantes disfrazados: "-" en asistencia_pct (202) y en horas_trabajo_semana (2.822), y 999 en distancia_km (152).
- Columnas numéricas que venían como texto: asistencia_pct (tenía el símbolo % en 300 celdas) y horas_trabajo_semana (por los guiones).
- Fechas en dos formatos en fecha_matricula: 3.052 estaban como DD/MM/AAAA.
- Errores de escritura en programa (Ingenieria de Sistemas, Psicologia), jornada (diurna, NOCTURNA con espacio), genero (M, F, femenino) y ciudad_procedencia (BOGOTÁ, bogota, medellin).
- Valores imposibles: edades de 150 (8 filas) y 12 (4 filas), y promedios de 45, 62 y 78 (17 filas) cuando la escala es de 0 a 5.
- 150 filas duplicadas.

Creo que los promedios fuera de escala y las columnas que venían como texto son lo que más afecta el análisis. Con esos promedios, la media de la columna daba 3,76 y la mediana era 3,68, y sin convertir la asistencia no se podían calcular los cuartiles.

### 2. Decisiones de limpieza

Cada decisión quedó en `Data/processed/decisiones.csv`, con las filas afectadas.

- asistencia_pct: quité el % y pasé los "-" a nulo para poder convertirla a número.
- horas_trabajo_semana: los "-" eran de quienes no trabajan, así que les puse 0. A quienes trabajan y no tenían dato (o tenían más de 100 horas) les puse la mediana de quienes trabajan.
- distancia_km: el 999 lo pasé a nulo y lo dejé así, porque no la uso en las preguntas y no quise inventar una distancia.
- programa, jornada, genero y ciudad_procedencia: quité espacios, pasé a minúscula y unifiqué con los valores de VALIDOS, porque son el mismo valor escrito distinto.
- fecha_matricula: leí los dos formatos por separado y los junté.
- Duplicados: eliminé 150 filas, porque dos estudiantes distintos no pueden tener las 23 columnas iguales, incluido el id.
- promedio_acumulado: eliminé las 298 filas sin nota y las 15 con nota fuera de 0 a 5. Una nota no se puede inventar, y con 45, 62 o 78 no se sabe cuál era la real.
- ciudad_procedencia y tipo_colegio: los nulos los puse como "Sin dato", para no perder esas filas.
- edad: las 12 edades de 150 y 12 años las reemplacé por la mediana.
- motivo_retiro: lo dejé con nulos porque no es un error.
- asistencia_pct: quedaron 197 nulos (los guiones). No los inventé, así que esas filas no entran en la pregunta 5.

El dataset limpio quedó con 9.687 filas y 25 columnas (las 23 originales más desertor y cuartil_asistencia).

### 3. Respuestas a las cinco preguntas

1. El programa con más deserción es Ingeniería Industrial, con 40,2 % (1.271 estudiantes). Le siguen Ingeniería de Sistemas con 38,2 % (1.386) y Diseño Gráfico con 35,6 % (848). El más bajo es Psicología con 26,0 % (1.137). Todos los grupos son grandes.
2. Sí hay diferencia. Los becados desertan 21,9 % (2.683 estudiantes) y los no becados 36,4 % (7.004), unos 14,5 puntos menos.
3. La jornada con menor promedio es la Nocturna con 3,46 (2.666 estudiantes). Fin de semana tiene 3,70 (949) y Diurna 3,73 (6.072).
4. Los desertores han reprobado en promedio 3,07 materias (3.136 estudiantes) y los activos 0,62 (5.692). Excluí a los graduados porque la comparación es entre quienes siguen y quienes se fueron, y los graduados ya terminaron.
5. Sí, la deserción sube cuando baja la asistencia: en el cuartil 1 (asistencia promedio 73,9 %) es 61,9 % (2.385 estudiantes); en el 2 (84,4 %) es 36,7 % (2.386); en el 3 (91,3 %) es 20,7 % (2.348); y en el 4 (98,7 %) es 9,4 % (2.371). Esto muestra una relación, pero no prueba que la baja asistencia cause la deserción, porque alguien que ya piensa irse también puede empezar a faltar.

### 4. Reflexión: asociación y causalidad

No, que los becados deserten menos (21,9 % frente a 36,4 %) no prueba que la beca cause la permanencia. Las becas muchas veces se dan por buen rendimiento, así que esos estudiantes ya tenían más probabilidad de quedarse. También puede haber otras cosas detrás, como el estrato, el colegio de origen o el apoyo de la familia. Para saber si la beca causa la permanencia habría que asignarla al azar, o comparar estudiantes becados y no becados con perfiles parecidos.

### 5. Reflexión: motivo_retiro y la predicción

No se puede usar para predecir, porque solo se conoce después de que el estudiante ya desertó. Si el modelo la usa, sabría la respuesta de antemano (todos los que tienen motivo son desertores). Algo parecido pasa con estado, que es lo que se quiere predecir, y con columnas como materias_reprobadas, creditos_aprobados o asistencia_pct si se miden hasta el momento del retiro y no antes.

### 6. Reflexión: variables sensibles

No creo que la institución deba usar género, estrato o ciudad para decidir quién recibe apoyo. Esas variables reflejan desigualdades sociales, y usarlas podría dejar sin ayuda a grupos que ya están en desventaja, o marcar a ciertos estudiantes como "de riesgo" solo por su origen. Además, que haya asociación con la deserción no significa que sea la causa. Es mejor guiarse por señales académicas, como la asistencia, las materias reprobadas o las tutorías, y usar las variables sensibles solo para revisar que el apoyo llegue de forma justa.
````