## Entrega final

### Declaración de uso

Durante el desarrollo de la entrega final se utilizó ChatGPT (OpenAI) como herramienta de apoyo para aclarar conceptos de aprendizaje automático, resolver dudas sobre la implementación de los modelos, solucionar errores puntuales de código en Python y mejorar la redacción de las interpretaciones y conclusiones del proyecto.

El equipo realizó los análisis e interpretó los resultados obtenidos en cada sección de los notebooks. A partir de estas interpretaciones, se compartieron con la IA las ideas, observaciones y conclusiones propias para solicitar apoyo en su redacción, buscando expresar los hallazgos de manera más clara, organizada y utilizando un lenguaje técnico adecuado, sin modificar el sentido original ni las cifras obtenidas.

También se utilizó para reforzar la comprensión de conceptos relacionados con la ingeniería de características, la validación cruzada, el desbalance de clases, los modelos de clasificación, los métodos de ensamble, las redes neuronales, las métricas de evaluación, la prueba de McNemar, el bootstrapping pareado, SHAP y la agrupación aglomerativa.

Adicionalmente, se solicitó apoyo para generar fragmentos de código, comprender el funcionamiento de algunas librerías de Python, construir gráficas que facilitaran la interpretación de los resultados y resolver dudas relacionadas con la implementación del pipeline, la API y el dashboard.

### Prompts utilizados

Los principales prompts utilizados, resumidos según su propósito, fueron:

**Comprensión de conceptos**

- "¿Qué limitaciones tiene utilizar una variable objetivo proxy para entrenar un modelo de clasificación cuando no conocemos los casos reales de pagos duplicados?".
- "¿Cuál es la diferencia entre Random Forest, Gradient Boosting y los métodos de ensamble como Voting y Stacking?".
- "¿Por qué es importante considerar métricas como precision, recall y F1 cuando las clases están desbalanceadas?".
- "¿Cómo se interpreta la prueba de McNemar y qué significa que el intervalo de confianza del bootstrap pareado incluya el cero?".
- "¿Cómo se interpreta el coeficiente de silueta en la agrupación aglomerativa y qué diferencias existen entre los métodos de enlace?".

**Dudas puntuales de código**

- "¿Cómo puedo utilizar `groupby` y `cumcount` para contar las facturas anteriores de cada proveedor sin incluir información futura?".
- "¿Cuál es la diferencia entre `fit`, `transform` y `fit_transform` en `StandardScaler` y cuándo debo utilizar cada uno?".
- "¿Cómo funciona `class_weight='balanced'` y cómo puedo aplicar una estrategia equivalente en `GradientBoostingClassifier`?".
- "¿Por qué `predict_proba` devuelve dos columnas y qué significa seleccionar `[:, 1]`?".
- "¿Cómo funciona `ColumnTransformer` y cómo puedo utilizarlo dentro de un pipeline para transformar diferentes tipos de variables?".

**Solución de errores de programación**

- "¿Por qué me aparece el error `AttributeError: Can only use .dt accessor with datetimelike values` cuando intento calcular la diferencia entre dos fechas?".
- "¿Cómo puedo solucionar el error `ValueError: Input X contains NaN` al entrenar un modelo?".
- "¿Qué significa la advertencia `ConvergenceWarning` al entrenar un modelo y cómo puedo solucionarla?".
- "¿Por qué obtengo dimensiones incompatibles al generar las gráficas de SHAP para un modelo de clasificación binaria?".
- "¿Cómo puedo solucionar el error `FileNotFoundError` al intentar cargar el pipeline guardado con joblib?".

**Generación y mejora de gráficas**

- "Ayúdame a generar el código para una gráfica que permita comparar las métricas de entrenamiento y validación de los diferentes modelos".
- "¿Cómo puedo mostrar los valores de las métricas encima de las barras y organizar la gráfica para facilitar su interpretación?".
- "¿Cómo puedo generar matrices de confusión que permitan comparar visualmente el desempeño de los modelos?".
- "Ayúdame a organizar las gráficas de SHAP para que sea más fácil identificar las variables que tienen mayor influencia sobre las predicciones".
- "¿Cómo puedo representar gráficamente la distribución de los tamaños de los grupos de proveedores y facilitar la identificación de agrupaciones demasiado grandes?".

**Redacción e interpretación de resultados**

- "Esta es mi interpretación de los resultados obtenidos. Ayúdame a mejorar la redacción sin cambiar las cifras, las ideas ni las conclusiones que planteé".
- "Considero que un buen desempeño frente a la variable objetivo proxy no significa necesariamente que el modelo identifique pagos duplicados reales. Ayúdame a expresar mejor esta idea y explicar sus implicaciones".
- "A partir de los resultados de la agrupación, considero que el coeficiente de silueta no debería ser el único criterio para seleccionar el umbral. Ayúdame a organizar esta interpretación y expresarla de manera más clara".
- "Estas son las conclusiones a las que llegué después de comparar los modelos. Ayúdame a redactarlas utilizando un lenguaje técnico adecuado, sin agregar conclusiones que no estén respaldadas por los resultados".
- "Teniendo en cuenta estas ideas, mis observaciones y los resultados de la validación realizada por el Banco, ayúdame a mejorar la redacción de las conclusiones y recomendaciones finales, manteniendo mi planteamiento original".

### Análisis crítico del resultado

La herramienta fue útil para reforzar la comprensión de los conceptos de aprendizaje automático, identificar posibles soluciones a errores de programación, facilitar la generación de gráficas y mejorar la claridad de las interpretaciones. Sin embargo, las respuestas no siempre tenían en cuenta las particularidades de los datos, el contexto del problema de negocio o las metodologías utilizadas durante el curso.

Por esta razón, las sugerencias se contrastaron con los resultados de los notebooks, las presentaciones y las prácticas realizadas en clase.

Se tuvo especial cuidado en evitar la fuga de información durante la preparación de los datos, comprender las implicaciones del desbalance de clases y diferenciar el desempeño de los modelos frente a la variable objetivo aproximada de su capacidad real para detectar pagos duplicados.

En la agrupación de proveedores, se consideraron las limitaciones de utilizar únicamente métricas estadísticas para seleccionar el umbral de agrupación, debido a que un resultado estadísticamente favorable no necesariamente representa una agrupación adecuada desde la perspectiva del negocio.

En cuanto al código, las soluciones propuestas se revisaron y ajustaron según las variables utilizadas, la estructura de los datos y el propósito de cada análisis.

Respecto a la redacción, en algunas ocasiones la herramienta podía generalizar demasiado las conclusiones, modificar el énfasis de las interpretaciones o realizar afirmaciones que no estaban suficientemente respaldadas por los resultados. Por esta razón, se revisaron los textos generados y se realizaron ajustes para mantener las ideas originales del equipo y garantizar su coherencia con los hallazgos del proyecto.

### Aportes propios del equipo

El equipo desarrolló el análisis de los datos, la construcción de las variables, la implementación y evaluación de los modelos de clasificación, el análisis de la agrupación de proveedores y la interpretación de los resultados obtenidos.

Entre las principales decisiones y aportes propios del proyecto se encuentran:

- La definición de los criterios para construir los pares de facturas y seleccionar la variable objetivo aproximada, considerando las limitaciones de los datos disponibles.
- La construcción y selección de variables, teniendo en cuenta su utilidad para el problema y los posibles riesgos de fuga de información.
- La evaluación y comparación de los modelos de clasificación, las pruebas estadísticas y los resultados de la agrupación de proveedores.
- La interpretación de los resultados de la validación realizada por el Banco y el ajuste de la estrategia de identificación y priorización de posibles pagos duplicados.
- La definición de las funcionalidades del producto de datos, el análisis del impacto económico y la formulación de las conclusiones y recomendaciones finales.

Las interpretaciones y conclusiones se formularon a partir de la revisión de las gráficas, las tablas, las métricas y los resultados obtenidos durante el desarrollo del proyecto. Posteriormente, estas ideas se compartieron con la IA para mejorar su redacción, organización y claridad, conservando el razonamiento y la perspectiva original del equipo.

La IA se utilizó como herramienta de apoyo para aclarar dudas conceptuales, generar y ajustar fragmentos de código, solucionar errores de programación y mejorar la comunicación de los resultados, mientras que las decisiones metodológicas, la revisión de las propuestas y las conclusiones finales fueron responsabilidad del equipo.

El proceso permitió reforzar los conocimientos adquiridos durante el curso, mejorar las habilidades de programación en Python, comprender las diferencias entre los modelos de aprendizaje automático y reconocer la importancia de complementar los resultados estadísticos con el conocimiento y la validación del negocio.
