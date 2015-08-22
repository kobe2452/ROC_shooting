import HTMLParser, re, string, nltk, timeit, math
import ujson as json
from ark_twokenize import *

json_tweet_file_name = 'train.json'
words_work_file_name = 'dictionary.txt'
norm_tweets_file_name = 'normalized_tweets.txt'

p = re.compile(r'^#*[a-z]+[\'-/]*[a-z]*$', re.UNICODE)
pLink = re.compile(r'https*:\S+\.\w+', re.IGNORECASE)
pMention = re.compile(r'@[A-Za-z0-9_]+\b')
pNewLine = re.compile(r'[\r\n]+')
pRetweet = re.compile(r'\brt\b', re.IGNORECASE)
punctuation = {0x2018:0x27, 0x2019:0x27, 0x201C:0x22, 0x201D:0x22}
h = HTMLParser.HTMLParser()

def get_normalized_word(w):
    """
    Returns normalized word or None, if it doesn't have a normalized representation.
    """
    if pLink.match(w):
        return '[http://LINK]'
    if pMention.match(w):
        return '[@SOMEONE]'
    if type(w) is unicode:
        # w1 = w.translate(punctuation).encode('ascii', 'ignore')  # find ASCII equivalents for unicode quotes
        w = w.translate(punctuation)
        # w3 = w.translate(punctuation).encode('unicode-escape')  # find unicode-escape equivalents for unicode quotes
    if len(w) < 1:
        return None
    if w[0] == '#':
        w = w.strip('.,*;-:"\'`?!)(').lower()
    else:
        w = w.strip(string.punctuation).lower()
    if not(p.match(w)):
        return None
    return w

def filter_words(text, stopset):

    """
    Keep only words that pass get_normalized_word(), return them as a list ---- origin method
    """
    # # naive tokenization
    # words = text.split()

    # # ArkTweetNLP tokenizer
    words = tokenizeRawTweetText(text)

    tokens = []

    for w in words:
        normalized_word = get_normalized_word(w)
        if normalized_word is not None:
            # remove stopwords from normalized tweet
            if normalized_word not in stopset:
                tokens.append(normalized_word)

    # tokens = stemmer_lemmatizer(tokens)

    return tokens

def stemmer_lemmatizer(tokens):

    wnl = nltk.WordNetLemmatizer()
    return [wnl.lemmatize(t) for t in tokens]

    # porter = nltk.PorterStemmer()
    # return [porter.stem(t) for t in tokens]

    # lancaster = nltk.LancasterStemmer()
    # return [lancaster.stem(t) for t in tokens]

def build_slang_dict(directory):

    slang = directory + 'slangdict.txt'

    slangdict = dict()

    for line in open(slang, "r"):
        sl = (line.split("-")[0]).strip().lower()
        mean = (line.split("-")[1]).strip().lower()
        slangdict[sl] = mean

    return slangdict

def build_stopwords_set(directory):

    stop1 = nltk.corpus.stopwords.words('english')

    stop2 = []
    stopwords = directory + 'stopwords.txt'
    for line in open(stopwords, "r"):
        stop2.append(line.strip())

    stopset = set(stop1) | set(stop2)

    return stopset

def prepare_words_file(json_tweet_file_name, output_file_name, stopset):
    """
    Reads a JSON file with tweets and stores all encountered normalized words in a file, one word per line.
    """
    with open(json_tweet_file_name, 'r') as json_file, open(output_file_name, 'w') as output_file:
        word_set = set()
        
        for line in json_file:
            row = json.loads(line)
            words = filter_words(row['message'], stopset)
            for w in words:
                word_set.add(w.rstrip())
                
        for w in word_set:
            output_file.write(w.encode('utf-8') + '\n')
            
        print 'number of distinct words: %d' % (len(word_set))
        
def prepare_normalized_tweets(json_tweet_file_name, output_file_name, stopset):
    """
    Reads tweets from a JSON file, normalizes them and stores them in a file in the following format:
    
    label token_1 token_2
    
    where label is a number (-1 or 1) and token_1 ... token_n are normalized words from the tweet.
    """
    with open(json_tweet_file_name, 'r') as json_file:
        normalized_tweets = []
        for line in json_file:
            row = json.loads(line)
            words = filter_words(row['message'], stopset)
            new = []
            for item in words:
                new.append(item.encode('utf-8'))

            # print words, type(words), type(new), new
            label = row['time_label']
            tpl = (str(label), ' '.join(new))
            normalized_tweets.append(tpl)
            
    with open(output_file_name, 'w') as f:
        for tweet in normalized_tweets:
            f.write(' '.join(tweet) + '\n')
    
def read_normalized_tweets(norm_tweets_file_name):
    """
    Reads normalized tweets from a file. Each line represents a labeled tweet and has to be in the following format:
    
    label token_1 token_2
    
    where label is a number (-1 or 1) and token_1 ... token_n are normalized words from the tweet.
    
    Input:
        norm_tweets_file_name - file containing normalized labeled tweets
        
    Output:
        list of tuples where the first item in the tuple is a label and the second item is a string of normalized tokens
    """
    with open(norm_tweets_file_name, 'r') as f:
        tuples = []
        lines = f.readlines()
        for line in lines:
            tokens = line.split()
            tuples.append((tokens[0], ' '.join(tokens[1:])))
        return tuples
    
if __name__ == '__main__':

    # mark the beginning time of process
    start = timeit.default_timer()

    directory = "/Users/tl8313/Documents/ROC_shooting/"

    # # eal stopset    
    # stopset = build_stopwords_set(directory)
    # # empty stopset
    stopset = set()

    slangdict = build_slang_dict(directory)

    prepare_words_file(json_tweet_file_name, words_work_file_name, stopset)
    prepare_normalized_tweets(json_tweet_file_name, norm_tweets_file_name, stopset)

    ##### mark the ending time of process #####
    end = timeit.default_timer()
    seconds = math.ceil(end - start)
    # Convert Secs Into Human Readable Time String (HH:MM:SS)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    print "This process took %d:%02d:%02d" % (h, m, s)
