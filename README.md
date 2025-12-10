# Luffy Learning - AI Education Coach

An AI-powered educational platform with multiple learning modules including speaking practice, book tutoring, and curriculum analysis.

## Project Structure

```
Luffy-Learning/
├── app.py                          # Main entry point (runs src/ui/main_app.py)
├── requirements.txt                # Python dependencies
├── python_curriculum_detailed.txt  # Sample curriculum file
│
├── src/                            # Main source code
│   ├── __init__.py
│   │
│   ├── ui/                         # User interface components
│   │   ├── __init__.py
│   │   ├── main_app.py            # Main Streamlit app
│   │   └── components.py          # Reusable UI components (footer, etc.)
│   │
│   ├── modules/                    # Application modules
│   │   ├── __init__.py
│   │   │
│   │   ├── speaking/              # Speaking practice module
│   │   │   ├── __init__.py
│   │   │   ├── coach.py          # SpeechCoach class
│   │   │   └── ui.py             # Speaking UI component
│   │   │
│   │   ├── book_tutor/           # Book tutoring module
│   │   │   ├── __init__.py
│   │   │   ├── tutor.py          # ReadingTutor class
│   │   │   └── ui.py             # Book tutor UI component
│   │   │
│   │   └── curriculum/           # Curriculum analysis module
│   │       ├── __init__.py
│   │       ├── agent.py          # Curriculum agent (LLM processing)
│   │       ├── helpers.py        # Text extraction helpers
│   │       └── ui.py             # Curriculum UI component
│   │
│   ├── services/                  # External services and APIs
│   │   ├── __init__.py
│   │   ├── openai_client.py      # OpenAI client initialization
│   │   └── vector_store.py       # Vector store service (ChromaDB)
│   │
│   └── utils/                      # Utility functions
│       ├── __init__.py
│       ├── analyzer.py            # Error detection utilities
│       ├── audio_cleaner.py       # Audio processing utilities
│       ├── feedback.py            # Feedback generation
│       ├── response_check.py      # Content safety checking
│       └── text_to_speech.py     # TTS functionality
│
└── data/                           # Data directory
    ├── novels/                    # PDF books for tutoring
    └── chroma_stores/            # Vector store databases
```

## Features

### 🗣️ Speaking Practice
- Generate reading passages by grade level
- Record and analyze pronunciation
- Get detailed feedback on errors
- Pronunciation scoring with visual heatmap
- Articulation tips for improvement

### 📖 Ask The Book
- Upload and query books using AI
- Get answers based on book content
- Full book summarization
- Text-to-speech responses
- Content safety filtering

### 📚 Curriculum Summarization
- Upload curriculum documents (PDF/TXT)
- Extract structured curriculum information
- Organize into modules and skills
- Use sample Python curriculum

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   Create a `.env` file with:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

3. **Add PDF books (for Ask The Book feature):**
   Place your PDF files in the `data/novels/` directory:
   ```
   data/novels/
     ├── the_lost_symbol.pdf
     └── Halo - The Fall Of Reach.pdf
   ```
   
   The app will automatically create vector stores for these books on first use.

4. **Run the application:**
   ```bash
   streamlit run app.py
   ```
   
   Or directly:
   ```bash
   streamlit run src/ui/main_app.py
   ```

## Data Migration

If you have existing data in the root directory:
- Move `novels/` → `data/novels/`
- Move `chroma_stores/` → `data/chroma_stores/`

The code will automatically look in the `data/` directory for these files.

## Architecture

The project follows a modular architecture:

- **UI Layer** (`src/ui/`): Streamlit interface components
- **Module Layer** (`src/modules/`): Feature-specific business logic
- **Service Layer** (`src/services/`): External API integrations
- **Utils Layer** (`src/utils/`): Reusable utility functions

This structure makes it easy to:
- Add new features (create new modules)
- Maintain and test code
- Scale the application
- Reuse components

## Notes

- The app uses Streamlit's caching for performance optimization
- Vector stores are persisted in `data/chroma_stores/`
- Feedback logs are stored in `feedback.db` (SQLite)
- All modules are lazy-loaded to improve startup time

