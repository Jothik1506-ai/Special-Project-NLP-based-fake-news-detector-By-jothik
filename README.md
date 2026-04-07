# Fake News Detector - NLP Based Project

**Live Website:** [https://fakenewsdetectorbynlp1556.streamlit.app](https://fakenewsdetectorbynlp1556.streamlit.app)

A web application that detects fake news articles using Natural Language Processing (NLP) and an NLP LSTM model. Built as a Special Project for Semester VI.

## How It Works

1. **Text Preprocessing (NLP):** Input text is cleaned by removing non-alphabetic characters, converting to lowercase, and filtering out English stopwords using NLTK.
2. **Tokenization:** Cleaned text is converted into integer sequences using a word index vocabulary of 10,000 words, then padded/truncated to a fixed length of 500 tokens.
3. **NLP Model:** A 2-layer LSTM neural network classifies the text as Real or Fake news.

## Model Architecture

```
Embedding (10000 vocab, 128 dims) → LSTM (128 units) → LSTM (64 units) → Dropout (0.5) → Dense (1, sigmoid)
```

- **Loss:** Binary Crossentropy
- **Optimizer:** Adam
- **Training Data:** Combination of Fake/True news datasets + LIAR dataset

## Tech Stack

| Component       | Technology                  |
|-----------------|-----------------------------|
| Frontend        | Streamlit                   |
| Model Inference | Pure NumPy (no TensorFlow)  |
| NLP             | NLTK (stopwords)            |
| Data Handling   | Pandas                      |
| Model Training  | TensorFlow / Keras          |

## Project Structure

```
fake-news-detector/
├── streamlit_app.py          # Main Streamlit web app
├── numpy_model.py            # Pure NumPy LSTM inference engine
├── model_weights.npz         # Exported model weights
├── tokenizer.json            # Word index for tokenization
├── requirements.txt          # Python dependencies
├── model_training/
│   ├── train_model.py        # Model training script
│   ├── Fake.csv              # Fake news dataset
│   └── True.csv              # True news dataset
└── website/
    ├── app.py                # Flask app (legacy)
    └── templates/
        └── index.html        # Flask frontend template
```

## Installation

```bash
git clone https://github.com/Jothik1506-ai/Special-Project-NLP-based-fake-news-detector.git
cd Special-Project-NLP-based-fake-news-detector
pip install -r requirements.txt
```

## Usage

```bash
streamlit run streamlit_app.py
```

The app opens at `http://localhost:8501` with two modes:
- **Text Analysis** - Paste an article and get a Real/Fake prediction with confidence scores
- **Batch Processing** - Upload a CSV file with a `text` column to analyze multiple articles at once

## Requirements

- Python 3.11+
- streamlit
- numpy
- pandas
- nltk