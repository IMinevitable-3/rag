# Repository

## Installation

- see `.env.example`

**macOS or linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
streamlit run RAG.py
```

**for graphs**

```
git checkout feat/json
cd frontend && npm i
cd json-service && npm i
```

- see .env.example in json-service

```
npx ng serve --proxy-config proxy.conf.json # for frontend service

npm run dev #backend service
```
