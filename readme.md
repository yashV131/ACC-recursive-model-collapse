# ACC Recursive Model Collapse

Exploring how language models change when each generation is trained on text produced by the previous generation. The planned comparison covers three source corpora: **Archaic**, **Complex**, and **Modern**.

> **Project status:** Barebone Setup

## Repository map

```text
.
├── backend/
│   ├── notebooks/
│   │   ├── archaic/
│   │   │   ├── 01_data.ipynb
│   │   │   ├── 02_train_generation.ipynb
│   │   │   └── 03_charts.ipynb
│   │   ├── complex/              # Same three notebook stages
│   │   ├── modern/               # Same three notebook stages
│   │   └── corpora/              # Corpus-specific data directories
│   ├── results/
│   │   ├── archaic/              # Generation results (G0, G1, ...)
│   │   ├── complex/
│   │   ├── modern/
│   │   ├── src/
│   │   │   ├── generate.py
│   │   │   └── metrics.py
│   │   └── samples.json
│   └── venv/                     # Local environment; not project source
├── config/
│   └── settings.yaml
├── frontend/
│   ├── public/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
├── .venv/                        # Optional root Python environment
├── main.py
├── requirements.txt              # Python and JupyterLab dependencies
└── readme.md
```

## Prerequisites

- Python 3.11 or newer
- Node.js 22.12+, with npm

## Set up the Python environment

Run these commands from the repository root.

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell blocks environment activation, either allow locally created
scripts for the current user or use the environment's Python directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### macOS or Linux

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

The root requirements file installs JupyterLab. The notebooks are grouped
under `backend/notebooks/` by corpus (`archaic`, `complex`, and `modern`).
Launch JupyterLab from the repository root after activating the environment:

```bash
cd backend
cd notebooks
jupyter lab
```

The notebooks and results are under active development; inspect each notebook
for its current workflow and status.

## Set up the frontend

In a second terminal, from the repository root:

```bash
cd frontend
npm i
npm run dev
```

Open the local URL printed by Vite.
To make a production build:

```bash
cd frontend
npm run build
```

## Corpus and experiment workflow

The intended experiment will run independently for the three corpora:

1. Add and document the source text for each corpus.
2. Clean and split each corpus into reproducible training and evaluation sets.
3. Train generation `G0` on the original text.
4. Generate text, then use those samples as the training material for `G1`,
   continuing for the configured number of generations.
5. Measure and visualize changes in vocabulary, diversity, and other selected
   metrics.

## Contributing

Create a branch for your work and open a pull request rather than pushing
changes directly to `main`.

```bash
git switch -c feature/short-description
# Make and verify your changes
git add .
git commit -m "Describe the change"
git push -u origin feature/short-description
```

Include the relevant setup or test steps in the pull request description. For
frontend changes, run `npm run build` from `frontend/`.

## API Keys
Do not push API Keys. 