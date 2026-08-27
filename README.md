# hyperchess

Chess website built using a FastApi backend, SvelteKit frontend and PostgreSQL database as part of my CompSci NEA

<img width="739" height="400" alt="image" src="https://github.com/user-attachments/assets/cd5dd48b-bafa-4504-bac6-bca90d84488f" />

## Features

- Account system
- Play versus engines
- Play versus other players
- Match analysis with engine
- Highly customisable GUI

## Setup

### Clone repository

```zsh
git clone https://github.com/hypRe1/hyperchess.git
```

### Environment variables

Example `.env` file below:

```env
URL_DATABASE = postgresql+asyncpg://...

JWT_SECRET_KEY = [32 byte hex]
JWT_ALGORITHM = HS256

ENGINES_LOC = [path to engine executables]
```

JWT_SECRET_KEY can be generated using the following Node.js script:

```zsh
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

### Backend

```zsh
cd backend
python -m venv env
source env/bin/activate
pip install -r requirements.txt
python main.py
```

### Frontend

```zsh
cd frontend
npm install
npm run dev
```
