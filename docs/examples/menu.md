# /menu dry run

El cliente es sintético (tests/skills/menu/client.md, "Lucía"; sin datos reales). Fecha de la ejecución: 2026-11-02, con la skill actual. DATA es una copia del estado inicial (profile.yaml y checkins.csv; sin `plan.md`, sin `tastes.yaml` y sin catálogo) usada como `COACH_DATA_DIR`; la skill no pasa `--data-dir`. Los `profile set` y `tastes set` se recortan a `...` cuando su salida repite el perfil.

Dos cosas de esta ejecución son deliberadamente sintéticas, para no usar datos reales de ninguna cadena ni de la red:

- Solo se usan las tablas base de alimentos (`foods/base.csv` y `regions/es/foods.csv`) y **un único producto de catálogo inventado**: "Mezcla de verduras salteadas congeladas (producto inventado)", código de barras 8400000000000, de una marca y una cadena inventadas ("Marca Ejemplo", "Supermercado Ejemplo"). Sus valores (71 kcal, 2 g de proteína, 9 g de hidratos, 3 g de grasa y 3 g de fibra por 100 g) están inventados, con las kcal coherentes con los macros. No existe en Open Food Facts: la fila se escribió con `coach.catalogue.save` en una llamada de Python puntual (`coach products` no tiene alta offline de OFF) con la fuente `Open Food Facts (unverified)`, que es la que llevaría una fila real de OFF. Sustituye aquí a la consulta `coach products search` + `coach products add` del paso 5, que necesita red.
- No hay búsqueda web ni red, así que los platos no llevan enlace de receta: la skill dice ofrecerlos sin enlace cuando no se puede buscar.
- Las respuestas de Lucía sobre el tupper, comer fuera y cocinar para dos amplían el archivo del cliente (que dice "no lo sé" para todo lo que no lista), para que los campos `tupper`, `eat_out` y `people` salgan en el borrador; `tests/skills/menu/client.md` no se ha tocado.

**Cliente:** ¿Me preparas un menú de tres días que cuadre con mis objetivos?

**Coach:** Claro. Primero miro tu perfil, la seguridad y tus objetivos.

```
$ coach profile show
{"data_dir": "DATA", "profile": {"sex": "female", "birth_date": "1992-03-14", "height_cm": 168.0, "weight_kg": 66.0, "goal": "fat_loss", "experience": "intermediate", "activity_level": "desk", "pal_override": null, "language": "es", "region": "es", "emergency_number": null, "medications": ["beta_blocker"], "conditions": ["hypertension"], "screening": {"scoff_positive": false, "parq_any_yes": true, "parq_followup_yes": false, "cardiac_symptoms": false, "menstrual": "normal", "bp_systolic": 132, "bp_diastolic": 84}, "injuries": [], "research_reminder_months": 6}, "missing": ["emergency_number"], "unrecognised": {"medications": [], "conditions": []}}

$ coach safety
{"screened": true, "no_deficit": false, "no_weight_targets": false, "hold_deficit": false, "use_rpe_not_hr": true, "prescriber_owns_weight": false, "refer_gp": false, "no_training": false, "cap_moderate": false, "no_calorie_targets": false, "hold_progression": false, "review_before_vigorous": true, "no_all_out_sprints": true, "emergency_number": "112", "paused_exercises": {}, "reasons": ["cardio-health.md: \"Beta-blockers: no formula-based HR zones\": prescribe by RPE and the talk test", "recovery-habits.md: \"PAR-Q+ specific thresholds\": a PAR-Q+ YES, so no all-out sprint formats (SIT, REHIT); they need every answer NO", "recovery-habits.md: \"PAR-Q+ specific thresholds\": a PAR-Q+ YES, so a qualified exercise professional or clinician reviews vigorous or maximal work (HIIT, 1RM tests, all-out sprints) before it starts; light-to-moderate work until then"]}

$ coach knowledge stale
{"months": 6, "stale": []}
```

(No hay `DATA/plan.md`, así que los objetivos salen de `coach macros` tal cual, sin `--kcal`, y se dice que son objetivos de partida hasta que `/plan` fije los del plan. `hold_deficit` es false, así que no hace falta `--current-kcal`. `refer_gp` no está activo: no hay frase final de derivación. Del `safety` solo importa aquí, y en una línea, que con el betabloqueante no se usan zonas de pulso y que con el SÍ del PAR-Q+ los menús no incluyen nada que dependa de entrenamientos intensos.)

```
$ coach macros
{"in_deficit": true, "kcal": 1500, "protein_g": 132.0, "fat_g": 41.67, "fat_min_g": 33.33, "carbs_g": 149.25, "fibre_g": 25, "protein_g_per_kg": 2.0, "notes": ["nutrition.md: \"Protein during fat loss\": 2 g/kg/day"]}

$ coach tastes show
{"tastes": {"loved_foods": null, "disliked_foods": null, "allergies": null, "intolerances": null, "cuisines": null, "flavours": null, "cooking_minutes": null, "cooking_skill": null, "equipment": null, "budget": null, "postal_code": null, "chains": null, "pantry": null, "untried": null, "ratings": []}, "missing": ["loved_foods", "disliked_foods", "allergies", "intolerances", "cuisines", "flavours", "cooking_minutes", "cooking_skill", "equipment", "budget", "postal_code", "chains"], "favoured": [], "disliked": [], "excluded": []}
```

Conocimiento cargado (recortado):

```
$ coach knowledge section nutrition "Protein distribution across meals"
### Protein distribution across meals
**Rule:** Use per-meal protein (about 0.3-0.4 g/kg, about 25-40 g for most adults, across 3-5 meals) as a practical way to reach the daily total, not as a separate requirement. If a client can only manage 2-3 meals, focus on the daily total.
**Grade:** moderate

$ coach knowledge section nutrition "Dietary fibre"
### Dietary fibre
**Rule:** Set a floor of at least 25 g/day of fibre (ideally 25-35 g) from whole grains, legumes, vegetables and fruit, including during fat loss and high-protein phases, plus at least 400 g/day of vegetables and fruit. Increase gradually, with fluids, to limit GI discomfort.
**Grade:** strong
```

**Coach:** Estos son tus objetivos de partida (hasta que `/plan` fije los del plan): 1500 kcal, 132,0 g de proteína, grasa de 41,67 g como mínimo (33,33 g de suelo) y 25 g de fibra [nutrition.md: "Protein during fat loss"; "Dietary fibre"]. Con el betabloqueante no uso zonas de pulso, y con tu SÍ en el PAR-Q+ no pongo nada que dependa de trabajo intenso [cardio-health.md: "Beta-blockers: no formula-based HR zones"; recovery-habits.md: "PAR-Q+ specific thresholds"]. Aún no tengo tus gustos. Te pregunto unas cosas:

1. ¿Qué alimentos te encantan y cuáles no te gustan?
2. ¿Alguna alergia o intolerancia?
3. ¿Qué cocinas y sabores prefieres?
4. ¿Cuántos minutos tienes por comida, qué nivel de cocina tienes y qué equipo (horno, airfryer, microondas...)?
5. ¿Presupuesto bajo, medio o alto, y tu código postal? Puedes preferir no darlo.

**Cliente:** Me encantan el aguacate, el pollo y los huevos; no me gusta el pescado. Sin alergias; intolerancia a la lactosa. Cocina mediterránea y mexicana, sabores picante y cítrico. 20 minutos por comida entre semana, nivel principiante, tengo horno, airfryer y microondas. Presupuesto medio. Código postal 46001.

```
$ coach tastes set loved_foods aguacate, pollo, huevos
$ coach tastes set disliked_foods pescado
$ coach tastes set allergies none
$ coach tastes set intolerances lactosa
$ coach tastes set cuisines mediterránea, mexicana
$ coach tastes set flavours picante, cítrico
$ coach tastes set cooking_minutes 20
$ coach tastes set cooking_skill beginner
$ coach tastes set equipment horno, airfryer, microondas
$ coach tastes set budget medium
$ coach tastes set postal_code 46001
... "loved_foods": ["aguacate", "pollo", "huevos"], "disliked_foods": ["pescado"], "allergies": [], "intolerances": ["lactosa"], "cuisines": ["mediterránea", "mexicana"], "flavours": ["picante", "cítrico"], "cooking_minutes": 20, "cooking_skill": "beginner", "equipment": ["horno", "airfryer", "microondas"], "budget": "medium", "postal_code": "46001", ...
```

**Coach:** Gracias. ¿En qué supermercados compras?

**Cliente:** En Mercadona y en Lidl.

(El cliente da las cadenas directamente, así que no hace falta buscar supermercados con el código postal ni enviarlo a ninguna búsqueda web.)

```
$ coach tastes set chains Mercadona, Lidl
{"tastes": {"loved_foods": ["aguacate", "pollo", "huevos"], "disliked_foods": ["pescado"], "allergies": [], "intolerances": ["lactosa"], "cuisines": ["mediterránea", "mexicana"], "flavours": ["picante", "cítrico"], "cooking_minutes": 20, "cooking_skill": "beginner", "equipment": ["horno", "airfryer", "microondas"], "budget": "medium", "postal_code": "46001", "chains": ["Mercadona", "Lidl"], "pantry": null, "untried": null, "ratings": []}, "missing": [], "favoured": [], "disliked": [], "excluded": []}
```

**Coach:** Perfecto. ¿Qué estructura quieres: cuántos días, qué comidas, alguna en tupper, alguna fuera de casa, algún plato que cocines para más de una persona? ¿Entrenas esos días y a qué hora?

**Cliente:** Tres días, con 4 comidas: desayuno, comida, merienda y cena. Si hace falta, la comida del segundo día en tupper, la cena del tercero fuera en un bar y la del primero la cocino para dos. Si entreno esos días, no lo sé.

(`training_schedule` no existe porque no hay `plan.md`, y la cliente no sabe si entrena: no se colocan comidas en torno a una sesión. Las dos reglas de entrenamiento no se cargan.)

**Coach:** Vale. Voy a buscar los alimentos y a armar los platos con tus gustos: sin pescado, sin lactosa (nada de leche, yogur, queso, nata ni mantequilla) y con picante y cítrico.

**Coach:** (Sin búsqueda web en esta prueba: los platos van sin enlace de receta. La biblioteca de recetas está vacía, así que no hay nada que reutilizar. Una cosa más: ¿compras alguna mezcla de verduras congelada que quieras usar?)

**Cliente:** Suelo comprar una mezcla de verduras salteadas congelada. No tengo el código de barras a mano.

(Aquí la skill buscaría el producto en Open Food Facts con `coach products search` y lo guardaría con `coach products add`, pidiendo el código de barras o los valores de la etiqueta. Esta prueba no usa red: el producto es la fila inventada descrita arriba, ya en `DATA/catalogue.csv`.)

```
$ coach foods search verduras
{"foods": [], "products": [{"product_name": "Mezcla de verduras salteadas congeladas (producto inventado)", "brand": "Marca Ejemplo", "chain": "Supermercado Ejemplo", "per": "100 g", "kcal": 71.0, "protein_g": 2.0, "carbs_g": 9.0, "fat_g": 3.0, "fibre_g": 3.0, "missing": [], "barcode": "8400000000000", "allergens": [], "source": "Open Food Facts (unverified)", "url": "synthetic: invented row, not a real product"}]}
```

(Antes de escribir la fila, la misma búsqueda devolvía `{"foods": [], "products": []}`: las tablas base no traen ninguna mezcla de verduras. `allergens` vacío no prueba que el producto sea seguro: se avisa a la cliente de que mire la etiqueta por la lactosa.)

**Coach:** Uso esa mezcla en un plato; ten en cuenta que es un dato sin verificar de una base pública (Open Food Facts), y que `alérgenos` sale vacío, así que mira la etiqueta del paquete por la lactosa. El resto de alimentos salen de las tablas base.

El borrador está en `DATA/menu-draft.yaml` (con `base` en cada comida y cena, `people: 2` en la primera cena, `tupper: true` en la comida del día 3 de noviembre y `eat_out: true` en la última cena):

```yaml
days:
  - date: 2026-11-02
    meals:
      - meal: Desayuno
        dishes:
          - dish: Tostada de aguacate con claras y tomate
            steps: ["Tostar el pan", "Hacer las claras en una sartén antiadherente 3 min", "Machacar el aguacate con limón y pimienta, poner las claras y el tomate encima"]
            seasoning: ["limón", "pimienta", "pimentón picante"]
            items: ["pan integral=50", "aguacate=40", "clara de huevo, cruda=200", "tomate=50"]
      - meal: Comida
        dishes:
          - dish: Bowl mexicano de pollo con judías negras y aguacate
            base: [pollo, arroz]
            steps: ["Sazonar el pollo con comino y pimentón y hacerlo a la plancha 6 min por lado", "Montar el bowl con arroz, judías, tomate, maíz y aguacate", "Terminar con lima y guindilla"]
            seasoning: ["comino", "pimentón picante", "lima", "cilantro", "guindilla"]
            items: ["pechuga de pollo, cruda=150", "judías negras, cocidas=120", "arroz blanco, cocido=90", "aguacate=20", "tomate=100", "maíz dulce en lata=30", "aceite de oliva=5"]
      - meal: Merienda
        dishes:
          - dish: Edamame con limón y pimentón picante y pavo en lonchas
            steps: ["Calentar el edamame en el microondas 2 min", "Aliñar con limón y pimentón y servir con el pavo"]
            seasoning: ["limón", "pimentón picante", "sal"]
            items: ["edamame=100", "pechuga de pavo en lonchas=100"]
      - meal: Cena
        people: 2
        dishes:
          - dish: Revuelto de huevo y claras con verduras salteadas
            base: [huevo, pan]
            steps: ["Saltear la mezcla de verduras 6 min", "Añadir el huevo y las claras batidos y cuajar sin dejar de mover", "Servir con el pan integral tostado"]
            seasoning: ["ajo en polvo", "pimienta", "guindilla", "limón"]
            items: ["huevo entero, crudo=60", "clara de huevo, cruda=200", "8400000000000=200", "pan integral=40", "aceite de oliva=5"]
  - date: 2026-11-03
    meals:
      - meal: Desayuno
        dishes:
          - dish: Gachas de avena con claras, plátano y canela
            steps: ["Cocer la avena con agua 4 min", "Añadir las claras removiendo 2 min", "Servir con plátano, canela y chía"]
            seasoning: ["canela", "vainilla"]
            items: ["copos de avena=40", "clara de huevo, cruda=170", "plátano=60", "semillas de chía=5"]
      - meal: Comida
        tupper: true
        dishes:
          - dish: Lentejas guisadas con pavo, zanahoria y pimentón picante
            base: [pavo, lentejas]
            steps: ["Sofreír cebolla y zanahoria con aceite 5 min", "Añadir el pavo en dados, la salsa de tomate, el pimentón y las lentejas", "Cocer a fuego medio 10 min y terminar con limón"]
            seasoning: ["pimentón picante", "comino", "limón", "perejil"]
            items: ["lentejas, cocidas=250", "pechuga de pavo, cruda=110", "zanahoria=60", "cebolla=40", "aceite de oliva=8", "salsa de tomate=40"]
      - meal: Merienda
        dishes:
          - dish: Rollitos de pavo con aguacate y pepino, y una mandarina
            steps: ["Untar el aguacate en las lonchas", "Añadir tiras de pepino y enrollar"]
            seasoning: ["lima", "pimienta"]
            items: ["pechuga de pavo en lonchas=130", "aguacate=30", "pepino=80", "mandarina=100"]
      - meal: Cena
        dishes:
          - dish: Tacos de ternera magra con aguacate y pico de gallo
            base: [ternera, maíz]
            steps: ["Dorar la carne en una sartén con comino y pimentón 6 min", "Calentar las tortillas de maíz en seco", "Servir con pico de gallo de tomate, cebolla, lima y cilantro, y el aguacate"]
            seasoning: ["comino", "pimentón picante", "lima", "cilantro"]
            items: ["carne picada de ternera magra, cruda=150", "tortilla de maíz=60", "aguacate=40", "tomate=80", "cebolla=30"]
  - date: 2026-11-04
    meals:
      - meal: Desayuno
        dishes:
          - dish: Huevos revueltos con espinacas y pan de centeno
            steps: ["Saltear las espinacas 2 min", "Añadir el huevo y las claras batidos y cuajar", "Tostar el pan de centeno"]
            seasoning: ["pimienta", "nuez moscada"]
            items: ["huevo entero, crudo=60", "clara de huevo, cruda=150", "espinacas, crudas=80", "pan de centeno=40", "naranja=100"]
      - meal: Comida
        dishes:
          - dish: Pasta integral con pollo al limón y brócoli picante
            base: [pollo, pasta]
            steps: ["Cocer la pasta y el brócoli juntos", "Dorar el pollo en tiras con ajo y guindilla 6 min", "Mezclar todo con limón y perejil"]
            seasoning: ["ajo", "guindilla", "limón", "perejil"]
            items: ["pasta integral, cruda=50", "pechuga de pollo, cruda=140", "brócoli, cocido=150", "aceite de oliva=8"]
      - meal: Merienda
        dishes:
          - dish: Garbanzos crujientes al airfryer con pavo
            steps: ["Escurrir y secar los garbanzos", "Airfryer 12 min a 200 grados con pimentón y comino", "Servir con el pavo en lonchas"]
            seasoning: ["pimentón picante", "comino", "sal"]
            items: ["garbanzos de bote, escurridos=120", "pechuga de pavo en lonchas=90"]
      - meal: Cena
        eat_out: true
        dishes:
          - dish: Solomillo de cerdo a la plancha con patata y ensalada (bar)
            base: [cerdo, patata]
            steps: ["Pedir el solomillo a la plancha, con la patata cocida y una ensalada de lechuga y tomate aliñada con poco aceite"]
            seasoning: ["limón", "pimienta"]
            items: ["solomillo de cerdo, crudo=200", "patata, cocida=200", "lechuga=60", "tomate=80", "aceite de oliva=10"]
```

Compruebo el primer día entero y, para repartir la proteína entre comidas, cada comida del primer día por separado (el CLI nunca suma por mí):

```
$ coach menu --item pan integral=50 --item aguacate=40 --item clara de huevo, cruda=200 --item tomate=50 --item pechuga de pollo, cruda=150 --item judías negras, cocidas=120 --item arroz blanco, cocido=90 --item aguacate=20 --item tomate=100 --item maíz dulce en lata=30 --item aceite de oliva=5 --item edamame=100 --item pechuga de pavo en lonchas=100 --item huevo entero, crudo=60 --item clara de huevo, cruda=200 --item 8400000000000=200 --item pan integral=40 --item aceite de oliva=5 --targets
{"totals": {"kcal": 1564.5, "protein_g": 142.38, "carbs_g": 111.24, "fat_g": 48.33, "fibre_g": 33.42, "unknown": [], "missing": {}}, "targets": {"in_deficit": true, "kcal": 1500, "protein_g": 132.0, "fat_g": 41.67, "fat_min_g": 33.33, "carbs_g": 149.25, "fibre_g": 25, "protein_g_per_kg": 2.0, "notes": ["nutrition.md: \"Protein during fat loss\": 2 g/kg/day"]}, "check": {"kcal": "ok", "protein_g": "ok", "fat_g": "ok", "fibre_g": "ok"}, "ok": true}

$ coach menu --item pan integral=50 --item aguacate=40 --item clara de huevo, cruda=200 --item tomate=50
{"kcal": 303.0, "protein_g": 29.27, "carbs_g": 21.89, "fat_g": 8.05, "fibre_g": 6.28, "unknown": [], "missing": {}}

$ coach menu --item pechuga de pollo, cruda=150 --item judías negras, cocidas=120 --item arroz blanco, cocido=90 --item aguacate=20 --item tomate=100 --item maíz dulce en lata=30 --item aceite de oliva=5
{"kcal": 569.7, "protein_g": 48.77, "carbs_g": 49.76, "fat_g": 13.33, "fibre_g": 13.94, "unknown": [], "missing": {}}

$ coach menu --item edamame=100 --item pechuga de pavo en lonchas=100
{"kcal": 215.0, "protein_g": 26.03, "carbs_g": 5.01, "fat_g": 8.5, "fibre_g": 4.8, "unknown": [], "missing": {}}

$ coach menu --item huevo entero, crudo=60 --item clara de huevo, cruda=200 --item 8400000000000=200 --item pan integral=40 --item aceite de oliva=5
{"kcal": 476.8, "protein_g": 38.32, "carbs_g": 34.58, "fat_g": 18.45, "fibre_g": 8.4, "unknown": [], "missing": {}}
```

(La proteína queda en 29,27, 48,77, 26,03 y 38,32 g: la comida pasa del rango de 25-40 g, porque los 132,0 g del día no caben en menos sin pasar de las kcal. La regla pide el total diario, no un requisito por comida, así que se deja y se dice.)

Ahora el plan entero:

```
$ coach mealplan check menu-draft.yaml
{"ok": true, "repeats": [], "taste_flags": [], "targets": {"in_deficit": true, "kcal": 1500, "protein_g": 132.0, "fat_g": 41.67, "fat_min_g": 33.33, "carbs_g": 149.25, "fibre_g": 25, "protein_g_per_kg": 2.0, "notes": ["nutrition.md: \"Protein during fat loss\": 2 g/kg/day"]}, "days": [{"date": "2026-11-02", "dishes": ["Tostada de aguacate con claras y tomate", "Bowl mexicano de pollo con judías negras y aguacate", "Edamame con limón y pimentón picante y pavo en lonchas", "Revuelto de huevo y claras con verduras salteadas"], "meals": [{"meal": "Desayuno", "tupper": false, "free": false, "dishes": ["Tostada de aguacate con claras y tomate"]}, {"meal": "Comida", "tupper": false, "free": false, "dishes": ["Bowl mexicano de pollo con judías negras y aguacate"]}, {"meal": "Merienda", "tupper": false, "free": false, "dishes": ["Edamame con limón y pimentón picante y pavo en lonchas"]}, {"meal": "Cena", "tupper": false, "free": false, "dishes": ["Revuelto de huevo y claras con verduras salteadas"]}], "totals": {"kcal": 1564.5, "protein_g": 142.38, "carbs_g": 111.24, "fat_g": 48.33, "fibre_g": 33.42, "unknown": [], "missing": {}}, "check": {"kcal": "ok", "protein_g": "ok", "fat_g": "ok", "fibre_g": "ok"}, "ok": true, "taste_flags": []}, {"date": "2026-11-03", "dishes": ["Gachas de avena con claras, plátano y canela", "Lentejas guisadas con pavo, zanahoria y pimentón picante", "Rollitos de pavo con aguacate y pepino, y una mandarina", "Tacos de ternera magra con aguacate y pico de gallo"], "meals": [{"meal": "Desayuno", "tupper": false, "free": false, "dishes": ["Gachas de avena con claras, plátano y canela"]}, {"meal": "Comida", "tupper": true, "free": false, "dishes": ["Lentejas guisadas con pavo, zanahoria y pimentón picante"]}, {"meal": "Merienda", "tupper": false, "free": false, "dishes": ["Rollitos de pavo con aguacate y pepino, y una mandarina"]}, {"meal": "Cena", "tupper": false, "free": false, "dishes": ["Tacos de ternera magra con aguacate y pico de gallo"]}], "totals": {"kcal": 1533.92, "protein_g": 133.88, "carbs_g": 123.66, "fat_g": 40.26, "fibre_g": 41.51, "unknown": [], "missing": {}}, "check": {"kcal": "ok", "protein_g": "ok", "fat_g": "ok", "fibre_g": "ok"}, "ok": true, "taste_flags": []}, {"date": "2026-11-04", "dishes": ["Huevos revueltos con espinacas y pan de centeno", "Pasta integral con pollo al limón y brócoli picante", "Garbanzos crujientes al airfryer con pavo", "Solomillo de cerdo a la plancha con patata y ensalada (bar)"], "meals": [{"meal": "Desayuno", "tupper": false, "free": false, "dishes": ["Huevos revueltos con espinacas y pan de centeno"]}, {"meal": "Comida", "tupper": false, "free": false, "dishes": ["Pasta integral con pollo al limón y brócoli picante"]}, {"meal": "Merienda", "tupper": false, "free": false, "dishes": ["Garbanzos crujientes al airfryer con pavo"]}, {"meal": "Cena", "tupper": false, "free": false, "dishes": ["Solomillo de cerdo a la plancha con patata y ensalada (bar)"]}], "totals": {"kcal": 1567.22, "protein_g": 141.39, "carbs_g": 127.79, "fat_g": 43.06, "fibre_g": 29.53, "unknown": [], "missing": {}}, "check": {"kcal": "ok", "protein_g": "ok", "fat_g": "ok", "fibre_g": "ok"}, "ok": true, "taste_flags": []}]}
```

(Los tres días salen `ok`, `repeats` está vacío y `taste_flags` también. Esto último no prueba que un plato sea seguro: el cruce es por nombre y no sabe de sinónimos, así que la lactosa se evitó a mano: ni leche, ni yogur, ni queso, ni nata, ni mantequilla. Las kcal de los tres días quedan entre el objetivo y un 5% por encima, la proteína y la fibra por encima de sus mínimos, y la grasa por encima de su suelo.)

**Coach (el plan):**

Sin enlaces de receta (no he podido buscar en la web). El producto de la cena del primer día, la mezcla de verduras congelada, es un dato sin verificar de una base pública (Open Food Facts); el resto sale de las tablas de alimentos del coach. La cena del día 2 de noviembre es para dos personas y la del día 4 la comes fuera: no se compra. La comida del día 3 de noviembre va en tupper.

**Lunes 2026-11-02:** 1564,5 kcal, 142,38 g de proteína.

| Comida | Plato |
|---|---|
| Desayuno | Tostada de aguacate con claras y tomate |
| Comida | Bowl mexicano de pollo con judías negras y aguacate |
| Merienda | Edamame con limón y pimentón picante y pavo en lonchas |
| Cena (para 2) | Revuelto de huevo y claras con verduras salteadas |

**Martes 2026-11-03:** 1533,92 kcal, 133,88 g de proteína.

| Comida | Plato |
|---|---|
| Desayuno | Gachas de avena con claras, plátano y canela |
| Comida (tupper) | Lentejas guisadas con pavo, zanahoria y pimentón picante |
| Merienda | Rollitos de pavo con aguacate y pepino, y una mandarina |
| Cena | Tacos de ternera magra con aguacate y pico de gallo |

**Miércoles 2026-11-04:** 1567,22 kcal, 141,39 g de proteína.

| Comida | Plato |
|---|---|
| Desayuno | Huevos revueltos con espinacas y pan de centeno |
| Comida | Pasta integral con pollo al limón y brócoli picante |
| Merienda | Garbanzos crujientes al airfryer con pavo |
| Cena (fuera) | Solomillo de cerdo a la plancha con patata y ensalada (bar) |

Los tres días cuadran con tus objetivos de partida (1500 kcal, 132,0 g de proteína, 25 g de fibra) [nutrition.md: "Protein during fat loss"; "Dietary fibre"]. La proteína por comida sale de 26,03 a 48,77 g el primer día: la comida pasa del rango de 25-40 g, pero la regla pide el total diario, no un mínimo por comida [nutrition.md: "Protein distribution across meals"]. ¿Te sirve este menú?

**Cliente:** Sí, lo acepto.

```
$ coach mealplan save menu-draft.yaml
... "saved": "menus/2026-11-02.yaml"}

$ coach shopping
{"menu": "menus/2026-11-02.yaml", "days": 3, "chains": {"Supermercado Ejemplo": [{"name": "Mezcla de verduras salteadas congeladas (producto inventado)", "grams": 400.0}], "any": [{"name": "aceite de oliva", "grams": 31.0}, {"name": "aguacate", "grams": 130.0}, {"name": "arroz blanco, cocido", "grams": 90.0}, {"name": "brócoli, cocido", "grams": 150.0}, {"name": "carne picada de ternera magra, cruda", "grams": 150.0}, {"name": "cebolla", "grams": 70.0}, {"name": "clara de huevo, cruda", "grams": 920.0}, {"name": "copos de avena", "grams": 40.0}, {"name": "edamame", "grams": 100.0}, {"name": "espinacas, crudas", "grams": 80.0}, {"name": "garbanzos de bote, escurridos", "grams": 120.0}, {"name": "huevo entero, crudo", "grams": 180.0}, {"name": "judías negras, cocidas", "grams": 120.0}, {"name": "lentejas, cocidas", "grams": 250.0}, {"name": "mandarina", "grams": 100.0}, {"name": "maíz dulce en lata", "grams": 30.0}, {"name": "naranja", "grams": 100.0}, {"name": "pan de centeno", "grams": 40.0}, {"name": "pan integral", "grams": 130.0}, {"name": "pasta integral, cruda", "grams": 50.0}, {"name": "pechuga de pavo en lonchas", "grams": 320.0}, {"name": "pechuga de pavo, cruda", "grams": 110.0}, {"name": "pechuga de pollo, cruda", "grams": 290.0}, {"name": "pepino", "grams": 80.0}, {"name": "plátano", "grams": 60.0}, {"name": "salsa de tomate", "grams": 40.0}, {"name": "semillas de chía", "grams": 5.0}, {"name": "tomate", "grams": 230.0}, {"name": "tortilla de maíz", "grams": 60.0}, {"name": "zanahoria", "grams": 60.0}]}, "unknown": [], "batches": [], "eaten_out": ["Solomillo de cerdo a la plancha con patata y ensalada (bar)"], "pantry_skipped": [], "note": "amounts are for the form each name gives (raw, cooked, drained); a batch is bought once at its servings, `left_over` of them are for other days or the freezer"}

$ coach mealplan export
{"pdf": "menus/2026-11-02.pdf", "menu": "menus/2026-11-02.yaml", "days": 3, "qr": true}
```

(El extra `pdf` está instalado en esta ejecución (`uv sync --extra pdf`), así que el export funciona. Sin el extra, el CLI avisa de que falta y la skill dice `uv sync --extra pdf` y enseña la lista de `coach shopping` como tabla.)

**Coach:** Guardado y exportado. El PDF está en `DATA/menus/2026-11-02.pdf`: lleva las recetas y la lista de la compra. Dos avisos de la lista: la cena del primer día es para dos personas, así que sus cantidades van multiplicadas en la compra (400,0 g de la mezcla de verduras y 180,0 g de huevo entero cuentan los dos platos, y las páginas por día del PDF muestran lo de una ración); y el solomillo de cerdo con patata y ensalada del día 2026-11-04 no se compra, porque lo tomas en un bar.

**Cliente:** El primer plato de la comida me encantó; el de la cena del segundo día no lo repetiría.

(La comida del primer día es el bowl mexicano de pollo; la cena del segundo día, los tacos de ternera.)

```
$ coach tastes rate Bowl mexicano de pollo con judías negras y aguacate loved
... "ratings": [{"dish": "Bowl mexicano de pollo con judías negras y aguacate", "rating": "loved", "date": "2026-11-02", "source": "", "note": ""}]}, "missing": [], "favoured": ["Bowl mexicano de pollo con judías negras y aguacate"], "disliked": [], "excluded": [], "recipe_saved": "recipes/bowl-mexicano-de-pollo-con-judias-negras-y-aguacate.yaml"}

$ coach tastes rate Tacos de ternera magra con aguacate y pico de gallo never_again
... "ratings": [{"dish": "Bowl mexicano de pollo con judías negras y aguacate", "rating": "loved", "date": "2026-11-02", "source": "", "note": ""}, {"dish": "Tacos de ternera magra con aguacate y pico de gallo", "rating": "never_again", "date": "2026-11-02", "source": "", "note": ""}]}, "missing": [], "favoured": ["Bowl mexicano de pollo con judías negras y aguacate"], "disliked": [], "excluded": ["Tacos de ternera magra con aguacate y pico de gallo"], "recipe_saved": null}

$ coach recipes list
{"recipes": [{"dish": "Bowl mexicano de pollo con judías negras y aguacate", "rating": "loved", "source": null, "servings": null, "file": "recipes/bowl-mexicano-de-pollo-con-judias-negras-y-aguacate.yaml", "has_steps": true}]}
```

**Coach (mensaje final):** Apuntado. El bowl mexicano de pollo queda como "me encantó" y se guarda en tu biblioteca de recetas, con sus pasos y sus ingredientes, para volver a usarlo. Los tacos de ternera quedan como "no lo repetiría" y no te los volveré a proponer.
