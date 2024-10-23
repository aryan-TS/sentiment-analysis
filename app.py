from flask import Flask, request, jsonify, render_template_string
from textblob import TextBlob
import os

app = Flask(__name__)

# HTML template with added loading state and error handling
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>TextBlob Sentiment Analysis</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        textarea {
            width: 100%;
            height: 150px;
            margin: 10px 0;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 16px;
        }
        button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
        }
        button:disabled {
            background-color: #cccccc;
            cursor: not-allowed;
        }
        .result {
            margin-top: 20px;
            padding: 15px;
            border-radius: 4px;
        }
        .positive { background-color: #dff0d8; border: 1px solid #d6e9c6; }
        .neutral { background-color: #f5f5f5; border: 1px solid #e3e3e3; }
        .negative { background-color: #f2dede; border: 1px solid #ebccd1; }
        .error { background-color: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }
        .loading { text-align: center; color: #666; }
        .metrics { display: flex; justify-content: space-between; margin-top: 10px; }
        .metric { flex: 1; text-align: center; padding: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Sentiment Analysis</h1>
        <div>
            <textarea id="text-input" placeholder="Enter text to analyze..."></textarea>
            <button onclick="analyzeSentiment()" id="analyze-btn">Analyze</button>
        </div>
        <div id="result"></div>
    </div>

    <script>
        async function analyzeSentiment() {
            const textInput = document.getElementById('text-input');
            const resultDiv = document.getElementById('result');
            const analyzeBtn = document.getElementById('analyze-btn');
            const text = textInput.value.trim();
            
            if (!text) {
                resultDiv.innerHTML = '<div class="error">Please enter some text to analyze</div>';
                return;
            }
            
            try {
                // Disable button and show loading state
                analyzeBtn.disabled = true;
                resultDiv.innerHTML = '<div class="loading">Analyzing...</div>';
                
                const response = await fetch('/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: text })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    let sentimentClass = 'neutral';
                    if (data.polarity > 0.1) sentimentClass = 'positive';
                    if (data.polarity < -0.1) sentimentClass = 'negative';
                    
                    resultDiv.innerHTML = `
                        <div class="result ${sentimentClass}">
                            <h3>Analysis Result:</h3>
                            <div class="metrics">
                                <div class="metric">
                                    <h4>Sentiment</h4>
                                    <p>${data.sentiment}</p>
                                </div>
                                <div class="metric">
                                    <h4>Polarity</h4>
                                    <p>${data.polarity.toFixed(2)}</p>
                                </div>
                                <div class="metric">
                                    <h4>Subjectivity</h4>
                                    <p>${data.subjectivity.toFixed(2)}</p>
                                </div>
                            </div>
                        </div>
                    `;
                } else {
                    resultDiv.innerHTML = `<div class="error">Error: ${data.error}</div>`;
                }
            } catch (error) {
                resultDiv.innerHTML = `<div class="error">Error: ${error.message}</div>`;
            } finally {
                analyzeBtn.disabled = false;
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/analyze', methods=['POST'])
def analyze_sentiment():
    try:
        data = request.json
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
        
        text = data['text'].strip()
        if not text:
            return jsonify({'error': 'Empty text provided'}), 400
        
        # Analyze sentiment using TextBlob
        analysis = TextBlob(text)
        
        # Determine sentiment label
        polarity = analysis.sentiment.polarity
        if polarity > 0.1:
            sentiment = "Positive"
        elif polarity < -0.1:
            sentiment = "Negative"
        else:
            sentiment = "Neutral"
        
        return jsonify({
            'text': text,
            'sentiment': sentiment,
            'polarity': analysis.sentiment.polarity,
            'subjectivity': analysis.sentiment.subjectivity
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)