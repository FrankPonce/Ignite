# -*- coding: utf-8 -*-
import pandas as pd
import json
import numpy as np
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
import streamlit as st
import string
from textblob import TextBlob


# Load the JSON data
with open('all_reviews.json') as file:
    data = json.load(file)

# Preprocessing Text Data
def clean_text(text):
    # Tokenize text
    tokens = word_tokenize(text.lower())
    # Remove punctuation
    tokens = [word for word in tokens if word.isalpha()]
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [w for w in tokens if not w in stop_words]
    # Lemmatization
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(w) for w in tokens]
    return ' '.join(tokens)

# Flatten the data into a list of dictionaries, each representing a single review
flat_data = [review for sublist in data for review in sublist]

# Convert the list of dictionaries into a DataFrame
reviews_df = pd.DataFrame(flat_data)
reviews_df['cleaned_comments'] = reviews_df['Comment'].apply(clean_text)


# Print the names of the columns
print(reviews_df.columns)

# Display the first few rows of the DataFrame to verify its structure
reviews_df.head()



nltk.download('popular')
nltk.download('stopwords')


# Handle Missing Values

# For numerical columns, convert to float and replace NaN with the column mean
numerical_cols = ['Quality', 'Difficulty']
for col in numerical_cols:
    reviews_df[col] = pd.to_numeric(reviews_df[col], errors='coerce')
    reviews_df[col].fillna(reviews_df[col].mean(), inplace=True)

# For text columns, replace NaN with a placeholder
categorical_cols = ['For Credit', 'Would Take Again', 'Textbook']
for col in categorical_cols:
    reviews_df[col].fillna('Unknown', inplace=True)

# Encode Categorical Data
# One-hot encoding for the 'department' column
reviews_df = pd.get_dummies(reviews_df, columns=['department'])

# Display the first few rows to verify changes
reviews_df.head()


from textblob import TextBlob

# Sentiment Analysis with TextBlob
reviews_df['sentiment'] = reviews_df['Comment'].apply(lambda comment: TextBlob(comment).sentiment.polarity)

# Aggregate Features
# Define the columns for which we want to calculate aggregate statistics
columns_to_aggregate = ['Quality', 'Difficulty', 'sentiment']

# Group by professor and aggregate with mean, median, and std
aggregated_features = reviews_df.groupby('professor')[columns_to_aggregate].agg(['mean', 'median', 'std']).reset_index()

# Flattening the multiindex for easier column access
aggregated_features.columns = ['_'.join(col).strip() for col in aggregated_features.columns.values]

# Display the aggregated features to verify
print(aggregated_features.head())

print(aggregated_features.columns)

# Categorizing 'sentiment'

def sentiment_category(score):
    if score > 0:
        return 'Positive'
    elif score < 0:
        return 'Negative'
    else:
        return 'Neutral'

# Categorize sentiment
reviews_df['sentiment_category'] = reviews_df['sentiment'].apply(sentiment_category)

# Calculate the percentage of each sentiment category per professor
sentiment_distribution = reviews_df.groupby('professor')['sentiment_category'].value_counts(normalize=True).unstack().fillna(0)

# Multiply by 100 for percentage representation and reset index for readability
sentiment_distribution = (sentiment_distribution * 100).reset_index()

# Display the sentiment distribution for each professor
print(sentiment_distribution)



# Ensuring numeric columns are of a numeric dtype
reviews_df['Quality'] = pd.to_numeric(reviews_df['Quality'], errors='coerce')
reviews_df['Difficulty'] = pd.to_numeric(reviews_df['Difficulty'], errors='coerce')
reviews_df['Would Take Again'] = pd.to_numeric(reviews_df['Would Take Again'], errors='coerce')
reviews_df['sentiment'] = pd.to_numeric(reviews_df['sentiment'], errors='coerce')

# Convert 'Would Take Again' to a numerical format for aggregation
reviews_df['Would Take Again'] = reviews_df['Would Take Again'].replace({'Yes': 1, 'No': 0})

# Convert 'Grade' to a numerical format for aggregation
grade_mapping = {
    'A+': 4.3, 'A': 4.0, 'A-': 3.7,
    'B+': 3.3, 'B': 3.0, 'B-': 2.7,
    'C+': 2.3, 'C': 2.0, 'C-': 1.7,
    'D+': 1.3, 'D': 1.0, 'F': 0,
    'Drop/Withdrawal': np.nan,
    'Incomplete': np.nan,
    'Not sure yet': np.nan,
    'Not_Sure_Yet': np.nan,
    'Rather not say': np.nan,
    'Rather_Not_Say': np.nan,
    'Unknown': np.nan
}

# Apply the mapping to the 'Grade' column
reviews_df['Grade_Numerical'] = reviews_df['Grade'].map(grade_mapping)

# Fill NaN values
reviews_df['Grade_Numerical'].fillna(reviews_df['Grade_Numerical'].mean(), inplace=True)
reviews_df['Quality'].fillna(reviews_df['Quality'].mean(), inplace=True)
reviews_df['Difficulty'].fillna(reviews_df['Difficulty'].mean(), inplace=True)
reviews_df['Would Take Again'].fillna(0, inplace=True)
reviews_df['sentiment'].fillna(0, inplace=True) # Neutral sentiment if missing

# Aggregate features by professor, also considering course if we need to filter by it later
aggregated_features = reviews_df.groupby(['professor', 'course_id']).agg({
    'Quality': 'mean',
    'Difficulty': 'mean',
    'Would Take Again': 'mean',
    'sentiment': 'mean',
    'Grade_Numerical': 'mean'
}).reset_index()

def get_best_professor(department=None, course_id=None, df=aggregated_features):
    if course_id:
        df = df[df['course_id'] == course_id]

    if df.empty:
        # If no matches found, return a message indicating this
        return f"No data found for the given criteria."

    # Calculate the composite score
    df['composite_score'] = (df['Quality'] * 2 + df['Would Take Again'] * 1.5 +
                             df['sentiment'] * 1 - df['Difficulty'] * 2 +
                             df['Grade_Numerical'] * 1)

    # Get the best professor based on the highest composite score
    best_professor = df.sort_values(by='composite_score', ascending=False).iloc[0]

    return best_professor[['professor']]

# Example
best_prof_for_course = get_best_professor(course_id=' FHS01')

print("Best Professor for Course:", best_prof_for_course)


# Import TF-IDF
from sklearn.feature_extraction.text import TfidfVectorizer

# Fix professor names
reviews_df['professor'] = reviews_df['professor'].str.strip().str.lower()

def preprocess_text(text):
    text = text.lower()
    # Replace punctuation with space
    text = ''.join([char if char.isalnum() or char.isspace() else ' ' for char in text])
    return text

# Preprocess comment column
#reviews_df['cleaned_comments'] = reviews_df['Comment'].apply(preprocess_text)

# Misspelled words and words to avoid
extended_stop_words = list(set(stopwords.words('english')) | {'ive', 'youll', 'alot', 'isnt', 'doesnt', 'wasnt',
                                                              'makes', 'really', 'extremely', 'very', 'teaches',
                                                              'often', 'would', 'little', 'took', 'students', 'might',
                                                              'go', 'give', 'try', 'already', 'says', 'whole', 'think',
                                                              'times', 'taken', 'expect', 'come', 'catch', 'life',
                                                              'also', 'must', 'class', 'classes', 'much', 'making',
                                                              'prof', 'professor', 'us', 'person', 'guy', 'wants',
                                                              'style', 'last', 'every', 'say', 'grader', 'make',
                                                              'always', 'im', 'anyone', 'term', 'looking', 'however',
                                                              'student', 'definitely', 'pretty', 'call', 'though', 'takes',
                                                              'one', 'many', 'material', 'things', 'thing', 'know', 'feel',
                                                              'subject', 'teacher', 'office', 'way', 'rather', 'load',
                                                              'overall', '10', '50', '20', 'comes', 'tends', 'need',
                                                              'assigned', 'stands', 'else', 'bring', 'school', 'actual',
                                                              'designed', 'since', 'even', 'shows', 'could', 'want',
                                                              'course', 'truly', 'first', 'taking', 'hours', 'although'
                                                              })

# Relevant words to look for
relevant_words = ['funny', 'bad', 'good', 'harsh', 'boring', 'easy', 'test', 'exam', 'hard',
                  'fun', 'great', 'unclear', 'lectures', 'avoid', 'take', 'interesting', 'passionate',
                  'kind', 'smart', 'experience', 'homework', 'project', 'projects', 'exams', 'mean',
                  'curve', 'knowledgeable', 'loved', 'time', 'cares', 'paper', 'papers', 'writing',
                  'lab', 'labs', 'impossible', 'wise', 'anecdotes', 'easier', 'harder', 'intimidating',
                  'friendly', 'terrible', 'amazing', 'difficult', 'help', 'struggle', 'struggling',
                  'best', 'worst', 'textbook', 'reputation', 'attention', 'willing', 'possible',
                  'confusing', 'brilliant', 'amazing', 'succeed', 'discussions', 'discussion', 'loves',
                  'serious', 'clear', 'organized', 'disorganized', 'great', 'recommend', 'different',
                  'debate', 'debates', 'write', 'sweet', 'essay', 'essays', 'reading', 'read', 'book',
                  'participate', 'helpful', 'awesome', 'nice', 'readings', 'final', 'quiz', 'quizzes',
                  'respect', 'open', 'lecturer', 'excellent', 'scholar', 'approachable', 'confused',
                  'confusing', 'tangents', 'tangent', 'ok', 'okay', 'accent', 'funniest', 'hardest',
                  'cute', 'jokes', 'tough', 'enjoyable', 'idiot', 'waste', 'entertaining', 'elective',
                  'weird', 'project', 'projects', 'presentation', 'ridiculous', 'fair', 'unfair', 'dry',
                  'handwriting', 'stupid', 'horrible', 'decent']

def get_top_keywords(professor, reviews_df, top_n=5, boost_factor=1.5):
    # Get reviews for the selected professor
    professor = professor.strip().lower()
    prof_comments = reviews_df[reviews_df['professor'] == professor]['cleaned_comments']

    if prof_comments.empty:
        return "No comments available for this professor."

    # Create the tfidf with stop words list
    tfidf = TfidfVectorizer(stop_words=extended_stop_words, max_df=0.5, min_df=2)
    tfidf_matrix = tfidf.fit_transform(prof_comments)

    # Boost scores for relevant words
    feature_names = np.array(tfidf.get_feature_names_out())
    for word in relevant_words:
        if word in feature_names:
            index = list(feature_names).index(word)
            tfidf_matrix[:, index] *= boost_factor

    # Sum tfidf scores for each term across all documents
    sum_tfidf = tfidf_matrix.sum(axis=0)
    sorted_indices = np.argsort(sum_tfidf).flatten()[::-1]

    # Extract top n keywords with highest sum tfidf scores
    top_keywords = feature_names[sorted_indices][:top_n]

    return top_keywords.tolist()




# Now, let's integrate Streamlit for the user interface
st.title("Find the Best Professor for Your Course")

# Flatten the data to get a list of unique course IDs for the dropdown
flat_data = [review for sublist in data for review in sublist]
#reviews_df = pd.DataFrame(flat_data)

# Extract unique course IDs and sort them
course_ids = sorted(reviews_df['course_id'].unique())

# Create a dropdown for course selection
selected_course_id = st.selectbox("Select a Course", course_ids)

# When a course is selected, display the best professor for that course
if st.button("Find Best Professor"):
    best_professor = get_best_professor(course_id=selected_course_id)
    professor_name = best_professor.iloc[0]  # Added .strip() to remove any leading/trailing spaces
    prof_keywords = get_top_keywords(professor_name, reviews_df, boost_factor=2)
    # If prof_keywords is a list of lists and you need it to be a single list of strings
    prof_keywords = [keyword for sublist in prof_keywords for keyword in sublist]

    st.write(f"The best professor for {selected_course_id} is: {professor_name}")
    if prof_keywords:
        st.markdown("Keywords for " + professor_name + " are:")
        st.markdown("* " + "\n* ".join(prof_keywords))
# Example
#best_prof_for_course = get_best_professor(course_id=' FHS01')

#print("Best Professor for Course:", best_prof_for_course)