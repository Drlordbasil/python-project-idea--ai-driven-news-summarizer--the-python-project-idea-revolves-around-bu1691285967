import requests
from bs4 import BeautifulSoup
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from transformers import T5Tokenizer, T5ForConditionalGeneration
from langdetect import detect
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import tkinter as tk
from tkinter import messagebox

nltk.download('punkt')
nltk.download('vader_lexicon')

class NewsScraper:
    def __init__(self, source_url):
        self.source_url = source_url

    def scrape_articles(self):
        articles = []

        try:
            response = requests.get(self.source_url)
            soup = BeautifulSoup(response.text, 'html.parser')

            for article in soup.find_all('article'):
                title = article.find('h2').get_text().strip()
                publication_date = article.find('time').get_text().strip()
                content = article.find('div', class_='content').get_text().strip()
                metadata = article.find('div', class_='metadata').get_text().strip()

                articles.append({
                    'title': title,
                    'publication_date': publication_date,
                    'content': content,
                    'metadata': metadata
                })

        except requests.exceptions.RequestException as error:
            messagebox.showerror('Error', str(error))
            return articles

        return articles

class NLPProcessor:
    def __init__(self, articles):
        self.articles = articles
        self.stopwords = set(nltk.corpus.stopwords.words('english'))
        self.sentiment_analyzer = SentimentIntensityAnalyzer()

    def preprocess_articles(self):
        preprocessed_articles = []

        for article in self.articles:
            tokens = nltk.word_tokenize(article['content'])
            clean_tokens = [token.lower() for token in tokens if token.isalpha() and token.lower() not in self.stopwords]
            preprocessed_content = ' '.join(clean_tokens)

            article['content'] = preprocessed_content
            preprocessed_articles.append(article)

        return preprocessed_articles

    def perform_sentiment_analysis(self, text):
        sentiment_scores = self.sentiment_analyzer.polarity_scores(text)
        return sentiment_scores['compound']

    def perform_named_entity_recognition(self, text):
        # Implement named entity recognition logic here
        pass

    def perform_part_of_speech_tagging(self, text):
        # Implement part-of-speech tagging logic here
        pass

class TextSummarizer:
    def __init__(self, articles):
        self.articles = articles
        self.tokenizer = T5Tokenizer.from_pretrained('t5-base')
        self.model = T5ForConditionalGeneration.from_pretrained('t5-base')

    def summarize_articles(self):
        summarized_articles = []

        for article in self.articles:
            input_ids = self.tokenizer.encode(article['content'], return_tensors='pt')
            summary_ids = self.model.generate(input_ids, max_length=150, num_beams=2, repetition_penalty=2.5,
                                              length_penalty=1.0)
            summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)

            summarized_articles.append({
                'title': article['title'],
                'publication_date': article['publication_date'],
                'summary': summary
            })

        return summarized_articles


class NewsSummarizerGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title('AI-Driven News Summarizer')

        self.label = tk.Label(self.window, text='Enter article URL:')
        self.label.pack()

        self.url_entry = tk.Entry(self.window)
        self.url_entry.pack()

        self.summarize_button = tk.Button(self.window, text='Summarize', command=self.summarize_article)
        self.summarize_button.pack()

    def summarize_article(self):
        url = self.url_entry.get()

        if url:
            scraper = NewsScraper(url)
            articles = scraper.scrape_articles()

            if articles:
                nlp_processor = NLPProcessor(articles)
                preprocessed_articles = nlp_processor.preprocess_articles()

                summarizer = TextSummarizer(preprocessed_articles)
                summarized_articles = summarizer.summarize_articles()

                messagebox.showinfo('Summarized Article', summarized_articles[0]['summary'])
            else:
                messagebox.showerror('Error', 'Failed to scrape articles.')
        else:
            messagebox.showerror('Error', 'Please enter a valid URL.')

    def run(self):
        self.window.mainloop()

def main():
    gui = NewsSummarizerGUI()
    gui.run()

if __name__ == '__main__':
    main()