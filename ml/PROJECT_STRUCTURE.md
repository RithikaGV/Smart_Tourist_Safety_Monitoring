# My Project Folder — Simple Guide

This is your `ml/` folder. It's the only part of the project you own.
Frontend and Backend teammates are working outside this folder.

Open this whole `ml` folder in VS Code (File → Open Folder).

---

## The Folder Map (in plain words)

```
ml/
├── data/
│   ├── raw/            → the "ingredients" — original data, untouched
│   └── processed/      → the "cooked" data — cleaned and ready for models
│
├── src/                → all your actual code lives here
│   ├── data_pipeline/   → scripts that COLLECT and CLEAN data
│   ├── features/        → (empty for now) shared code to build features
│   ├── models/          → one folder per AI module — the "brains"
│   ├── explainability/  → (empty for now) code that explains predictions
│   └── api/              → (empty for now) code that connects to Backend
│
├── artifacts/           → saved trained models (the finished "brain files")
├── docs/                 → all explanations, notes, and reports
├── notebooks/           → (empty for now) for exploring data visually
└── tests/                → (empty for now) code that checks things work
```

Think of it like a kitchen:
- **data/raw** = ingredients you bought
- **data/processed** = ingredients washed and chopped, ready to cook
- **src/data_pipeline** = the recipes for washing/chopping
- **src/models** = the recipes for actually cooking each dish
- **artifacts** = the finished dish, saved for later
- **docs** = your recipe notes explaining why you did things this way

---

## What's in each file right now

### `data/raw/` — original data, don't edit these by hand
| File | What it is |
|---|---|
| `nilgiris_places.csv` | List of 60 real places in Nilgiris (name, coordinates, type) |
| `tourist_movements.csv` | Fake (synthetic) tourist trips, used to test the AI |
| `crowd_density.csv` | Fake crowd numbers per place |
| `crime_score.csv` | Fake crime risk numbers per place |

### `data/processed/` — cleaned data, ready to train models
| File | What it is |
|---|---|
| `final_features.csv` | All the important numbers about each place, merged into one table |
| `risk_labels.csv` | For each place: is it "Safe" or "Dangerous"? (used to teach the model) |

### `src/data_pipeline/` — scripts that get and clean data
| File | What it does | Where to run it |
|---|---|---|
| `verify_coordinates.py` | Checks the exact GPS location of each place | Google Colab |
| `fetch_restricted_zones.py` | Gets the real boundary shapes of forbidden areas | Google Colab |
| `fetch_weather_data.py` | Downloads real weather data | Google Colab |
| `fetch_emergency_services.py` | Finds hospitals and police stations nearby | Google Colab |
| `generate_synthetic_data.py` | Creates fake tourist/crowd/crime data (already run once) | Anywhere |
| `pipeline_phase2_to_4.py` | Cleans everything and combines it into `final_features.csv` | Anywhere |

### `src/models/risk_prediction/` — the first working AI model
| File | What it does |
|---|---|
| `generate_risk_labels.py` | Decides which places are "Safe" or "Dangerous" (a starting rule, since we don't have real accident data yet) |
| `train_risk_model.py` | Trains the actual AI model (XGBoost) and checks how good it is |

### `artifacts/` — the trained AI model, ready to use
| File | What it is |
|---|---|
| `risk_model.json` | The trained model itself (this is what the API will load and use) |
| `risk_model_columns.json` | A small helper file so the API knows the model's exact input format |

### `docs/` — all your explanation notes, in one place
| File | What it explains |
|---|---|
| `phase0_ai_ml_planning.md` | The master plan: all 6 AI modules, what each one does |
| `nilgiris_places_README.md` | Notes on how accurate the place list is |
| `synthetic_data_README.md` | Honest notes on what's fake data vs real, and why |
| `disaster_alerts_notes.md` | Why there's no real landslide/flood alert API, and what we did instead |
| `eda_summary.txt` | Quick facts learned from looking at the data |
| `risk_model_metrics.txt` | How well the first AI model performed |

---

## Empty folders — what they're FOR (you'll fill these later)

- **`notebooks/`** → Later, for exploring data with charts (Phase 3, EDA)
- **`src/features/`** → Later, shared code so all 6 models can reuse the same feature-building logic
- **`src/models/safety_score/`** → Phase 6, the next model you'll build
- **`src/models/deviation/`** → Phase 7 (the "off your route" alert — no AI needed, just math)
- **`src/models/behaviour_analysis/`** → Phase 8
- **`src/models/suspicious_movement/`** → Phase 9
- **`src/models/pattern_detection/`** → Phase 10
- **`src/explainability/`** → Phase 12, code using SHAP to explain predictions
- **`src/api/`** → Phase 13, the code that lets Backend call your models
- **`tests/`** → Phase 14, code that checks everything still works correctly

---

## What to do next in VS Code

1. Open the `ml` folder in VS Code
2. Everything you see above is already there and working
3. Next step (Phase 5, continued): run the 4 scripts in `src/data_pipeline/`
   that say "Google Colab" above — once done, re-run `pipeline_phase2_to_4.py`,
   then `generate_risk_labels.py`, then `train_risk_model.py` again to get
   real (not placeholder) results
