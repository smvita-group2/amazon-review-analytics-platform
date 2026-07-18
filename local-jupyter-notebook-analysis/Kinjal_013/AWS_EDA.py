# Databricks notebook source
reviews_df = spark.read.parquet(
"/Volumes/project/proj_schema/proj_volume/Video_Games.parquet"
)

reviews_df.printSchema()
reviews_df.show(5)

# COMMAND ----------

# DBTITLE 1,Cell 2
import pyarrow.parquet as pq
import pandas as pd

# Use PyArrow to read the Parquet file and handle duplicate columns
parquet_path = "/Volumes/project/proj_schema/proj_volume/meta_Video_Games.parquet"
table = pq.read_table(parquet_path)

# Deduplicate column names
cols = table.column_names
seen = {}
deduped_cols = []

for c in cols:
    if c in seen:
        seen[c] += 1
        deduped_cols.append(f"{c}_{seen[c]}")
    else:
        seen[c] = 0
        deduped_cols.append(c)

# Create pandas DataFrame with deduplicated columns
pandas_df = table.to_pandas()
pandas_df.columns = deduped_cols

# Convert to Spark DataFrame
meta_df = spark.createDataFrame(pandas_df)

print(meta_df.columns)

# COMMAND ----------

reviews_df.show(5, truncate=False)

# COMMAND ----------

display(reviews_df)

# COMMAND ----------

meta_df.printSchema()

# COMMAND ----------

meta_df.show(10, truncate=False)

# COMMAND ----------

display(meta_df)

# COMMAND ----------

print("Reviews Rows:", reviews_df.count())
print("Meta Rows:", meta_df.count())

# COMMAND ----------

print("Reviews Columns:", len(reviews_df.columns))
print("Meta Columns:", len(meta_df.columns))

# COMMAND ----------

from pyspark.sql.functions import rand

sample_df = reviews_df.orderBy(rand()).limit(5000)

# COMMAND ----------

sample_df.count()

# COMMAND ----------

from pyspark.sql.functions import *

sample_df.select([
    count(when(col(c).isNull(),c)).alias(c)
    for c in sample_df.columns
]).show()

# COMMAND ----------

sample_df.printSchema()

# COMMAND ----------

full_df.select(
    "rating",
    "helpful_vote"
).describe().show()

# COMMAND ----------

rating_pd = (
    full_df.groupBy("rating")
           .count()
           .orderBy("rating")
           .toPandas()
)

import matplotlib.pyplot as plt

plt.figure(figsize=(6,4))
plt.bar(rating_pd['rating'], rating_pd['count'])
plt.xlabel('Rating')
plt.ylabel('Number of Reviews')
plt.title('Rating Distribution')
plt.show()

# COMMAND ----------

verified_pd = (
    full_df.groupBy("verified_purchase")
           .count()
           .toPandas()
)

plt.figure(figsize=(5,5))
plt.pie(
    verified_pd['count'],
    labels=verified_pd['verified_purchase'],
    autopct='%1.1f%%'
)
plt.title('Verified Purchase Distribution')
plt.show()

# COMMAND ----------

yearly_pd = (
    full_df.groupBy(year("review_date").alias("year"))
           .count()
           .orderBy("year")
           .toPandas()
)

plt.figure(figsize=(8,4))
plt.plot(yearly_pd['year'], yearly_pd['count'], marker='o')
plt.xlabel('Year')
plt.ylabel('Review Count')
plt.title('Reviews Over Time')
plt.grid(True)
plt.show()

# COMMAND ----------

top_brands = (
    brand_summary.orderBy(col("reviews").desc())
                 .limit(10)
                 .toPandas()
)

plt.figure(figsize=(10,5))
plt.barh(top_brands['store'], top_brands['reviews'])
plt.xlabel('Reviews')
plt.ylabel('Store')
plt.title('Top 10 Stores by Review Count')
plt.gca().invert_yaxis()
plt.show()

# COMMAND ----------

sample_df = sample_df.withColumn(
    "review_date",
    from_unixtime(col("timestamp")/1000)
)

# COMMAND ----------

sample_df = sample_df.withColumn(
    "review_date",
    to_timestamp("review_date")
)

# COMMAND ----------

sample_df.select(
    "timestamp",
    "review_date"
).show(5)

# COMMAND ----------

full_df = sample_df.join(
    meta_df,
    on="parent_asin",
    how="left"
)

# COMMAND ----------

full_df.printSchema()

# COMMAND ----------

full_df.groupBy("rating")\
       .count()\
       .orderBy("rating")\
       .show()

# COMMAND ----------

full_df.groupBy("verified_purchase")\
       .count()\
       .show()

# COMMAND ----------

from pyspark.sql.functions import year

full_df.groupBy(
    year("review_date").alias("year")
).count().orderBy("year").show()

# COMMAND ----------

full_df = full_df.withColumn(
    "sentiment",
    when(col("rating")>=4,1).otherwise(0)
)

# COMMAND ----------

# DBTITLE 1,Safely extract numeric price for price_clean
full_df.groupBy("sentiment").count().show()

# COMMAND ----------

# DBTITLE 1,Try robust cast to double for price_clean
text_df = full_df.select(
    "text",
    "sentiment"
).dropna()

# COMMAND ----------

# Convert to pandas for sklearn processing
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
import re

text_pandas = text_df.toPandas()

# COMMAND ----------

import re

text_pandas['text'] = (
    text_pandas['text']
    .astype(str)
    .apply(
        lambda x:
        re.sub(r'<.*?>',' ',x)
    )
)

# COMMAND ----------

from sklearn.feature_extraction.text import CountVectorizer

cv = CountVectorizer(
    stop_words='english',
    min_df=5
)

analyzer = cv.build_analyzer()

text_pandas['clean_text'] = (
    text_pandas['text']
    .apply(
        lambda x:
        " ".join(analyzer(x))
    )
)

# COMMAND ----------

clean_df = text_pandas

# COMMAND ----------

print(clean_df)

# COMMAND ----------

X_count = cv.fit_transform(
    clean_df['clean_text']
)

# COMMAND ----------

idx = 100

print("Original:")
print(clean_df['text'].iloc[idx])

print("\nAfter Stopword Removal:")
print(clean_df['clean_text'].iloc[idx])

# COMMAND ----------

print("Original Text:")
print(clean_df['text'].iloc[2])


# COMMAND ----------

print("\nAfter Stopword Removal:")
print(clean_df['clean_text'].iloc[2])

# COMMAND ----------

# DBTITLE 1,Cell 25
from sklearn.feature_extraction.text import TfidfVectorizer
tfidf = TfidfVectorizer()

X_tfidf = tfidf.fit_transform(
    clean_df['clean_text']
)

# COMMAND ----------

y = clean_df['sentiment']

# COMMAND ----------

# DBTITLE 1,Cell 26
from sklearn.model_selection import train_test_split

y = clean_df['sentiment']

X_train, X_test, y_train, y_test = train_test_split(
    X_tfidf,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print(X_train.shape)
print(X_test.shape)

# COMMAND ----------

from sklearn.naive_bayes import MultinomialNB

nb = MultinomialNB()

nb.fit(X_train, y_train)

y_pred_nb = nb.predict(X_test)

# COMMAND ----------

from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score

print("Accuracy :", accuracy_score(y_test,y_pred_nb))
print("Precision:", precision_score(y_test,y_pred_nb))
print("Recall   :", recall_score(y_test,y_pred_nb))
print("F1 Score :", f1_score(y_test,y_pred_nb))

# COMMAND ----------

from sklearn.linear_model import LogisticRegression

lr = LogisticRegression(max_iter=1000)

lr.fit(X_train,y_train)

y_pred_lr = lr.predict(X_test)

# COMMAND ----------

# DBTITLE 1,Cell 30
print("Accuracy :", accuracy_score(y_test,y_pred_lr))
print("Precision:", precision_score(y_test,y_pred_lr))
print("Recall   :", recall_score(y_test,y_pred_lr))
print("F1 Score :", f1_score(y_test,y_pred_lr))

# COMMAND ----------

# DBTITLE 1,Cell 31
from sklearn.ensemble import RandomForestClassifier

rf = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

rf.fit(X_train,y_train)

y_pred_rf = rf.predict(X_test)

# COMMAND ----------

print("Accuracy :", accuracy_score(y_test,y_pred_rf))
print("Precision:", precision_score(y_test,y_pred_rf))
print("Recall   :", recall_score(y_test,y_pred_rf))
print("F1 Score :", f1_score(y_test,y_pred_rf))

# COMMAND ----------

comparison = pd.DataFrame({
    'Model':['Naive Bayes',
             'Logistic Regression',
             'Random Forest'],
    'Accuracy':[
        accuracy_score(y_test,y_pred_nb),
        accuracy_score(y_test,y_pred_lr),
        accuracy_score(y_test,y_pred_rf)
    ],
    'F1 Score':[
        f1_score(y_test,y_pred_nb),
        f1_score(y_test,y_pred_lr),
        f1_score(y_test,y_pred_rf)
    ]
})

comparison

# COMMAND ----------

import matplotlib.pyplot as plt

comparison.plot(
    x='Model',
    y='Accuracy',
    kind='bar'
)

plt.title("Model Comparison")
plt.ylabel("Accuracy")
plt.show()

# COMMAND ----------

from sklearn.metrics import confusion_matrix

cm = confusion_matrix(
    y_test,
    y_pred_lr
)

print(cm)

# COMMAND ----------

import seaborn as sns
import matplotlib.pyplot as plt

sns.heatmap(
    cm,
    annot=True,
    fmt='d'
)

plt.title("Confusion Matrix")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.show()

# COMMAND ----------

coef = lr.coef_[0]

feature_names = tfidf.get_feature_names_out()

importance = pd.DataFrame({
    'word':feature_names,
    'coefficient':coef
})

top_positive = importance.sort_values(
    'coefficient',
    ascending=False
).head(20)

print(top_positive)

# COMMAND ----------

top_negative = importance.sort_values(
    'coefficient'
).head(20)

print(top_negative)

# COMMAND ----------

# DBTITLE 1,Cell 39
top_positive.plot(
    x='word',
    y='coefficient',
    kind='barh',
    figsize=(10,6)
)

plt.title("Top Positive Words")
plt.show()

# COMMAND ----------

# DBTITLE 1,Cell 40
top_negative.plot(
    x='word',
    y='coefficient',
    kind='barh',
    figsize=(10,6)
)

plt.title("Top Negative Words")
plt.show()

# COMMAND ----------

clean_df['review_length'] = (
    clean_df['clean_text']
    .apply(len)
)

# COMMAND ----------

corr_pd = full_df.select(
    "rating",
    "helpful_vote",
    "price_clean"
).dropna().toPandas()

sns.heatmap(
    corr_pd.corr(numeric_only=True),
    annot=True,
    cmap='Blues'
)

plt.title('Correlation Heatmap')
plt.show()

# COMMAND ----------

import seaborn as sns

sns.histplot(
    clean_df['review_length'],
    bins=30
)

plt.title("Review Length Distribution")
plt.show()

# COMMAND ----------

# DBTITLE 1,Cell 43
clean_df['sentiment'].value_counts()

# COMMAND ----------

clean_df['sentiment'].value_counts().plot(
    kind='bar'
)

plt.title("Sentiment Distribution")
plt.show()

# COMMAND ----------

# Transformer-Based Sentiment Analysis (DistilBERT)

# COMMAND ----------

# MAGIC %pip install transformers torch

# COMMAND ----------

from transformers import pipeline

# COMMAND ----------

sentiment_model = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english"
)

# COMMAND ----------

sample_review = clean_df['text'].iloc[0]

result = sentiment_model(
    sample_review[:512]
)

print(result)

# COMMAND ----------

sample_df = clean_df.sample(
    500,
    random_state=42
)

reviews = sample_df['text'].tolist()

predictions = sentiment_model(
    [review[:512] for review in reviews]
)

# COMMAND ----------

bert_pred = []

for pred in predictions:

    if pred['label'] == 'POSITIVE':
        bert_pred.append(1)

    else:
        bert_pred.append(0)

# COMMAND ----------

from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score

y_true = sample_df['sentiment']

bert_acc = accuracy_score(y_true, bert_pred)
bert_precision = precision_score(y_true, bert_pred)
bert_recall = recall_score(y_true, bert_pred)
bert_f1 = f1_score(y_true, bert_pred)

print("Accuracy :", bert_acc)
print("Precision:", bert_precision)
print("Recall   :", bert_recall)
print("F1 Score :", bert_f1)

# COMMAND ----------

nb_acc = accuracy_score(y_test, y_pred_nb)
lr_acc = accuracy_score(y_test, y_pred_lr)
rf_acc = accuracy_score(y_test, y_pred_rf)

comparison

# COMMAND ----------

comparison = pd.DataFrame({
    'Model': [
        'Naive Bayes',
        'Logistic Regression',
        'Random Forest',
        'DistilBERT'
    ],
    'Accuracy': [
        nb_acc,
        lr_acc,
        rf_acc,
        bert_acc
    ]
})

comparison.sort_values(
    by='Accuracy',
    ascending=False
)

# COMMAND ----------

from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained(
    "distilbert-base-uncased-finetuned-sst-2-english"
)

# COMMAND ----------

sample_review = clean_df['text'].iloc[0]

print(sample_review)

# COMMAND ----------

tokens = tokenizer.tokenize(sample_review)

print(tokens[:100])

# COMMAND ----------

from collections import Counter

all_words = " ".join(clean_df['clean_text']).split()

word_freq = Counter(all_words)

top_words = pd.DataFrame(
    word_freq.most_common(20),
    columns=['word', 'count']
)

print(top_words)

plt.figure(figsize=(10,5))
plt.bar(top_words['word'], top_words['count'])
plt.xticks(rotation=45)
plt.title('Top 20 Most Frequent Words')
plt.show()

# COMMAND ----------

token_ids = tokenizer.encode(
    sample_review,
    add_special_tokens=True
)

print(token_ids[:50])

# COMMAND ----------

ids = tokenizer.encode(
    sample_review,
    add_special_tokens=True
)

tokens = tokenizer.convert_ids_to_tokens(ids)

for token in tokens[:50]:
    print(token)

# COMMAND ----------

text = "unbelievable gameplay"

tokens = tokenizer.tokenize(text)

print(tokens)

# COMMAND ----------

sample_reviews = clean_df.sample(
    10,
    random_state=42
)[['text','sentiment']]

for idx, row in sample_reviews.iterrows():

    review = str(row['text'])[:512]

    prediction = sentiment_model(review)[0]

    actual = "POSITIVE" if row['sentiment']==1 else "NEGATIVE"

    print("="*120)

    print("Review:")
    print(review[:300])

    print("\nActual Sentiment:")
    print(actual)

    print("\nPredicted Sentiment:")
    print(prediction['label'])

    print("\nConfidence:")
    print(f"{prediction['score']:.4f}")

# COMMAND ----------

hard_reviews = [
    "The product is excellent but stopped working after one week",
    "The game has amazing graphics but the controls are terrible",
    "I loved the design but the battery life is awful",
    "The sound quality is fantastic but it crashes frequently",
    "The product works well although customer support is useless"
]

results = sentiment_model(hard_reviews)

for review, result in zip(hard_reviews, results):
    print("="*100)
    print("Review:", review)
    print("Prediction:", result['label'])
    print("Confidence:", f"{result['score']:.4f}")

# COMMAND ----------

hard_reviews = [
    "The product is not good",
    "The product is not bad",
    "I do not dislike this game",
    "I am not unhappy with this purchase",
    "The product is not terrible"
]

results = sentiment_model(hard_reviews)

print("\nNEGATION REVIEWS")
print("="*100)

for review, result in zip(hard_reviews, results):
    print("\nReview:")
    print(review)

    print("\nPrediction:")
    print(result['label'])

    print("\nConfidence:")
    print(f"{result['score']:.4f}")

    print("-"*100)

# COMMAND ----------

hard_reviews = [
    "Fantastic, it broke on the first day",
    "Great job, now the product won't even turn on",
    "Wonderful experience, I wasted my money",
    "Amazing quality, lasted only two hours",
    "Best purchase ever... not"
]

results = sentiment_model(hard_reviews)

print("\nSARCASM REVIEWS")
print("="*100)

for review, result in zip(hard_reviews, results):
    print("\nReview:")
    print(review)

    print("\nPrediction:")
    print(result['label'])

    print("\nConfidence:")
    print(f"{result['score']:.4f}")

    print("-"*100)

# COMMAND ----------

hard_reviews = [
    """
    Initially I loved this product.
    The packaging was great and setup was easy.
    After a few days the battery started draining rapidly
    and now it doesn't work at all.
    """
]

results = sentiment_model(hard_reviews)

print("\nLONG REVIEW WITH SENTIMENT SHIFT")
print("="*100)

for review, result in zip(hard_reviews, results):
    print("\nReview:")
    print(review)

    print("\nPrediction:")
    print(result['label'])

    print("\nConfidence:")
    print(f"{result['score']:.4f}")

    print("-"*100)

# COMMAND ----------

hard_reviews = [
    "The product is excellent but stopped working after one week",
    "The product is not bad",
    "Fantastic, it broke on the first day",
    """Initially I loved this product but after a week it completely stopped working.""",
    "The camera quality is amazing but the battery drains in two hours",
    "I expected it to be terrible but it turned out surprisingly good",
    "The game is fun, however frequent crashes make it frustrating",
    "Not the best purchase, but definitely not the worst either"
]

results = sentiment_model(hard_reviews)

print("\nADVANCED SENTIMENT ANALYSIS TEST CASES")
print("="*120)

for review, result in zip(hard_reviews, results):

    print("\nReview:")
    print(review)

    print("\nPredicted Sentiment:")
    print(result['label'])

    print("\nConfidence Score:")
    print(f"{result['score']:.4f}")

    print("="*120)

# COMMAND ----------

import seaborn as sns
import matplotlib.pyplot as plt

scores = [x['score'] for x in predictions]

plt.figure(figsize=(10,5))
sns.histplot(scores, bins=20, kde=True)

plt.title("DistilBERT Confidence Distribution")
plt.xlabel("Confidence Score")
plt.ylabel("Count")

plt.show()

# COMMAND ----------

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

pred_labels = [x['label'] for x in predictions]

pred_df = pd.DataFrame({
    'Prediction': pred_labels
})

plt.figure(figsize=(8,5))

sns.countplot(
    data=pred_df,
    x='Prediction'
)

plt.title("DistilBERT Prediction Distribution")

plt.show()

# COMMAND ----------

from sklearn.metrics import confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

cm = confusion_matrix(y_true, bert_pred)

plt.figure(figsize=(8,6))

sns.heatmap(
    cm,
    annot=True,
    fmt='d',
    cmap='Blues'
)

plt.title("DistilBERT Confusion Matrix")

plt.xlabel("Predicted")
plt.ylabel("Actual")

plt.show()

# COMMAND ----------

import seaborn as sns
import matplotlib.pyplot as plt

plt.figure(figsize=(10,6))

sns.barplot(
    data=comparison,
    x='Accuracy',
    y='Model'
)

plt.title("Model Accuracy Comparison")

plt.xlim(0,1)

plt.show()

# COMMAND ----------

review = """
The product is excellent but stopped working after one week
"""

result = sentiment_model(review)

print("Review:")
print(review)

print("\nPrediction:")
print(result[0]['label'])

print("\nConfidence:")
print(f"{result[0]['score']:.0f}")

# COMMAND ----------

product_summary = (
    full_df
    .groupBy("parent_asin")
    .agg(
        count("*").alias("review_count"),
        avg("rating").alias("avg_rating"),
        sum("helpful_vote").alias("total_helpful_votes")
    )
)

# COMMAND ----------

brand_summary = (
    full_df
    .groupBy("store")
    .agg(
        count("*").alias("reviews"),
        avg("rating").alias("avg_rating")
    )
)

# COMMAND ----------

full_df.select(
    corr("helpful_vote","rating")
).show()