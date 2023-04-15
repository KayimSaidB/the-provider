import nltk
from nltk.corpus import wordnet
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords

FINAL_STOP_WORDS = stopwords.words("english") + stopwords.words("french")


def text_similarity(text1, text2):
    # initialize sentiment analyzer
    sid = SentimentIntensityAnalyzer()

    # perform sentiment analysis on text1 and text2
    sentiment1 = sid.polarity_scores(text1)
    sentiment2 = sid.polarity_scores(text2)

    # create TfidfVectorizer and fit_transform the texts
    tfidf = TfidfVectorizer(stop_words=FINAL_STOP_WORDS).fit_transform([text1, text2])

    # calculate cosine similarity score between the two texts
    cosine_score = cosine_similarity(tfidf[0], tfidf[1])[0][0]

    # calculate similarity score based on theme, vocabulary, and lexical field
    theme_score = 0
    vocabulary_score = 0
    lexical_field_score = 0

    # calculate theme score based on common wordnet synsets
    synsets1 = set(
        ss for word in nltk.word_tokenize(text1) for ss in wordnet.synsets(word)
    )
    synsets2 = set(
        ss for word in nltk.word_tokenize(text2) for ss in wordnet.synsets(word)
    )
    common_synsets = synsets1.intersection(synsets2)
    theme_score = len(common_synsets) / (
        len(synsets1) + len(synsets2) - len(common_synsets)
    )

    # calculate vocabulary score based on common words
    words1 = set(nltk.word_tokenize(text1))
    words2 = set(nltk.word_tokenize(text2))
    common_words = words1.intersection(words2)
    vocabulary_score = len(common_words) / (
        len(words1) + len(words2) - len(common_words)
    )

    # calculate lexical field score based on common wordnet hypernyms
    hypernyms1 = set(
        h for word in words1 for ss in wordnet.synsets(word) for h in ss.hypernyms()
    )
    hypernyms2 = set(
        h for word in words2 for ss in wordnet.synsets(word) for h in ss.hypernyms()
    )
    common_hypernyms = hypernyms1.intersection(hypernyms2)
    lexical_field_score = len(common_hypernyms) / (
        len(hypernyms1) + len(hypernyms2) - len(common_hypernyms)
    )

    # combine cosine similarity score with theme, vocabulary, and lexical field scores
    print(f"{cosine_score=}")
    print(f"{theme_score=}")
    print(f"{vocabulary_score=}")
    print(f"{lexical_field_score=}")
    combined_score = (
        cosine_score
        * theme_score
        * vocabulary_score
        * lexical_field_score
        * ((sentiment1["compound"] + 1) / 2)
        * ((sentiment2["compound"] + 1) / 2)
    )

    return combined_score


text1 = "j'aime les femmes qui aiment les femmes"
text2 = "je mange du fromage de chèvre"
print(text_similarity(text1, text2))
