# Operator Performance Benchmarking

Big data pipeline analysing UK bus operator reliability using BODS (Bus Open Data Service) timetable and disruption data, processed in PySpark, stored in SQLite, and evaluated with KMeans clustering.

See `docs/architecture.md` for the full pipeline design, module responsibilities, and documented limitations.

## Project structure

```
config/
  settings.yaml          # all paths, Spark settings, DB path, ML config - no hardcoded values in code
docs/
  architecture.md         # design write-up, PySpark-vs-pandas justification, limitations, security notes
  architecture.png        # diagram version
  figures/                # generated EDA/results charts (created by src/viz/charts.py)
notebooks/
  01_eda.ipynb            # exploratory data analysis (interactive)
  02_results.ipynb        # final results and figures for the report
src/
  ingest/                 # load_gtfs.py, parse_disruptions.py
  process/                # clean_join.py, headway.py
  db/                     # schema.sql, load_db.py, queries.py
  ml/                      # features.py, train_models.py, evaluate.py, interpret.py
  viz/                     # charts.py
tests/                    # unit tests for the modules above (pytest)
main.py                   # runs the entire pipeline end to end
requirements.txt
```

## Setup

```bash
pip install -r requirements.txt
```

Download BODS data manually (see `docs/architecture.md` for source links) and place it at the paths configured in `config/settings.yaml`:
- GTFS timetable files -> `data/raw/itm_west_midlands_gtfs/`
- SIRI-SX disruptions file -> `data/raw/sirisx/`

## Running the pipeline

```bash
python main.py
```

This runs the full pipeline (ingest -> process -> store -> model) and prints the model comparison table, then stores results in the SQLite database configured in `config/settings.yaml`.

For interactive exploration, open `notebooks/01_eda.ipynb` and `notebooks/02_results.ipynb` instead.

## Running the dashboard (optional)

After running `main.py` at least once (so the database has data in it):

```bash
pip install streamlit
streamlit run dashboard.py
```

(If `streamlit.exe` is blocked by a system security policy, use `python -m streamlit run dashboard.py` instead.)

This opens a browser dashboard where you can select an operator, see its performance tier and headway stats, and compare it against all other operators on a scatter chart.

## Running tests

```bash
pytest tests/
```

## Configuration

All paths, Spark settings, database location, and ML hyperparameters are defined in `config/settings.yaml` - no values are hardcoded in the source modules. See that file directly for the current settings.

## Security

- All SQL queries use parameterised placeholders (see `src/db/queries.py`), never string concatenation.
- No API keys or database credentials are hardcoded anywhere in this codebase.
