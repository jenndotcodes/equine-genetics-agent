# Equine Genetics Agent & Simulation Infrastructure

An advanced biological simulation dashboard and multi-agent verification system designed to compute offspring coat color inheritance probabilities in horses, audit compliance safety, and retrieve grounded historical registry guidelines.

---

## 📂 Project Architecture

The workspace is organized as follows:

```
├── .agents/
│   └── skills/
│       ├── genetics/
│       │   └── SKILL.md          # Primary genetics engine tool specifications (v3.0.0)
│       └── critique/
│           └── SKILL.md          # Critique validation rules & safety instructions
├── tools/
│   ├── genetics_engine.py        # 9-loci Punnett square logic & context retriever
│   └── critique_agent.py         # Safety auditor checking for lethal genetic crosses
├── app.py                        # Streamlit interactive dashboard & agent log monitor
├── breed_registry_notes.json     # Grounded biological and historical reference data
├── deploy.sh                     # Google Cloud Run deployment script
├── Dockerfile                    # Containerization script for production environment
├── requirements.txt              # Project package dependencies
└── README.md                     # Project documentation (this file)
```

### Architectural Breakdown
- **Streamlit Application (`app.py`)**: Renders the premium dark-themed UI, handles parent allele selectors, renders progress bars, displays the interactive Locus Breakdown Table, and houses the Mock Terminal log monitor.
- **Genetics Engine (`tools/genetics_engine.py`)**: The deterministic backbone. It computes Mendelian 2x2 Punnett crossovers for all nine loci individually (`E`, `A`, `Cr`, `D`, `Z`, `Ch`, `prl`, `G`, `O`) and aggregates them into a probability matrix representing up to $262,144$ possible genotypes.
- **Critique Agent (`tools/critique_agent.py`)**: An validation layer that intercepts calculated probability payloads. It runs safety audits to flag hazardous crosses—such as the homozygous Frame Overo (`OO`) Lethal White Syndrome (LWS) condition—and blocks standard outputs to return high-priority veterinary warnings.
- **Breed Registry Notes (`breed_registry_notes.json`)**: A database of historical and registry information matched dynamically against resolved offspring phenotypes.

---

## 🧬 Key Features & Implementation Details

### 1. 9-Loci Deterministic Genetic Engine
Computes independent Punnett squares simultaneously across all major equine coat color layers:
*   **Base Coat Loci**: Extension (`E/e`) and Agouti (`A/a`) specifying Black, Bay, or Chestnut base.
*   **Dilutions & Modifiers**: Cream (`Cr/n`), Dun (`D/d`), Silver (`Z/z`), Champagne (`Ch/ch`), and Pearl (`prl/n`).
*   **Patterns & Masks**: Grey (`G/g`) and Frame Overo (`O/n`).
*   **Biological Epistasis Rules**:
    *   **Silver Modifier**: Restricts Silver (`Z`) dilution to black-pigmented bases (`EE` or `Ee`).
    *   **Pearl & Cream Co-dominance**: Models recessive Pearl (`prlprl`) and the co-dominant Cream-Pearl phenotype (`prln` + `Crn`).
    *   **Progressive Greying**: Visible phenotypes containing a dominant Grey gene (`GG` or `Gn`) are dynamically modified to return `Grey (Born [Base/Diluted Color])` to indicate progressive whitening.

### 2. Multi-Agent Safety Verification
Intercepts output payloads to enforce safety guidelines:
*   **LWS Intercept**: If the genetics engine computes a homozygous Frame Overo cross (`OO`), the Critique Agent flags the outcome as `Lethal White Syndrome (Fatal)`.
*   **Compliance Alerts**: If a cross contains a non-zero probability of LWS, it stops standard reports and issues a high-priority red breeding warning alerting the breeder of intestinal defects and breeding violation standards.

---

## 🚀 Installation & Execution

### Prerequisites
- **Python**: version 3.9 or higher
- **Git**: for cloning and repository operations
- **Docker**: (Optional) for containerized execution

### Quick-Start Local Run
1. Clone the repository and navigate to the project directory:
   ```bash
   git clone https://github.com/jenndotcodes/equine-genetics-agent.git
   cd equine-genetics-agent
   ```
2. Install the application dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the local Streamlit server:
   ```bash
   python3 -m streamlit run app.py
   ```
4. Open your browser and navigate to:
   *   **Local URL**: [http://localhost:8501](http://localhost:8501)

---

## 📦 Production Deployment

### 1. Streamlit Community Cloud
To host this project on Streamlit Community Cloud:
- Push all changes to your GitHub repository.
- Connect your GitHub account to the Streamlit Community Cloud dashboard.
- Create a new app, select this repository and the `main` branch, and set the entrypoint file to `app.py`.
- Any subsequent pushes to `main` will trigger an automated build and hot-reload.

### 2. Google Cloud Run (Containerized Setup)
The project includes a production-grade [Dockerfile](file:///Users/jennbee/equine-genetics-agent/Dockerfile) and a [deploy.sh](file:///Users/jennbee/equine-genetics-agent/deploy.sh) script tailored to host the container securely on Google Cloud Run.

#### Configured Guardrails
- **Single-Instance Limit (`--max-instances=1`)**: Restricts the deployment to a single active container instance to enforce a strict singleton pattern, ensuring consistent state representation.
- **Execution Timeout Guardrail (`--timeout=15`)**: Restricts maximum execution duration for requests to 15 seconds to prevent runaway calculations or hanging API calls.

To run the containerized deployment:
```bash
./deploy.sh
```
This runs `gcloud run deploy` with the hardcoded configuration rules.
