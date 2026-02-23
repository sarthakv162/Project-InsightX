# InsightX - Multi-Agent Sports Analysis System

Vision-Language-Action (VLA) multi-agent framework for biomechanical and tactical sports analysis.

## Structure

```
SynapseAI2.0/
├── backend/
│   ├── agents/                 # Multi-agent implementations
│   ├── workflows/              # LangGraph orchestration
│   ├── models/                 # Data models and types
│   ├── utils/                  # Video + Gemini utilities
│   ├── config/                 # Settings and environment loading
│   ├── main.py                 # CLI entry point
│   ├── requirements.txt        # Python dependencies
│   └── .env.example            # Environment template
├── .gitignore
└── README.md
```

## Setup (Windows)

1. Create and activate a virtual environment:

```bash
python -m venv .venv
.\.venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r backend\requirements.txt
```

3. Configure your API key:

```bash
copy backend\.env.example backend\.env
```

Then edit backend\.env and set:

```
GEMINI_API_KEY=your_gemini_api_key_here
```

## Run the CLI

```bash
cd backend
python main.py
```

The CLI supports:
- YouTube URLs (passed directly to Gemini)
- Local video files
- Multi-turn chat follow-ups for the same video

## Core Features

- Multi-agent analysis: scouter, analyst, strategist, coach
- Temporal grounding with timestamps
- Biomechanical and tactical reasoning
- Natural-language coaching response + drills
- Gemini 2.x video understanding

## Environment Variables

```
GEMINI_API_KEY=your_gemini_api_key_here
```

## License

Proprietary - InsightX Project
