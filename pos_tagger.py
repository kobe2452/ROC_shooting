# You can use this to run the CMU Tweet NLP package(http://www.ark.cs.cmu.edu/TweetNLP/)
# First, download the package at https://github.com/brendano/ark-tweet-nlp/
# Second, put everything in the project directory where you are running the python script
import ujson as json
import timeit, math, subprocess, codecs, os, psutil, tempfile
from collections import defaultdict

# use specific model ---- Penn Treebank-style POS tags for Twitter
def runFile(fileName, directory):
    os.chdir("ark-tweet-nlp-0.3.2")

    # subprocess.call(["ls", "-l"])

    command = './runTagger.sh --output-format pretsv --model model.ritter_ptb_alldata_fixed.20130723.txt ' + fileName
    commands = command.split()

    # p = subprocess.call(commands)

    p = subprocess.Popen(commands, stdout=subprocess.PIPE)
    file_name = directory + 'POStagged_tweets_work.txt'
    print "output to: " + file_name

    o = codecs.open(file_name, 'w', 'utf-8')
    while p.poll() is None:
        l = p.stdout.readline()
        o.write(l.decode('utf-8'))
        o.flush()
    o.close()

def main():
    # mark the beginning time of process
    start = timeit.default_timer()

    directory = "/Users/tl8313/Documents/work_project/svm-scikit/"

    work_json = open(directory+"work_new.json", "r")

    work_txt = directory+"work_new.txt"
    work_txt_output = open(work_txt, "w")

    work_dict = defaultdict(int)
    visited = set()

    for line in work_json:
        tweet = json.loads(line.decode('utf-8'))

        msg_id = tweet['msg_id']
        message = tweet['message']
        userid = tweet['userid']

        work_dict[msg_id] += 1

        if msg_id not in visited:
            visited.add(msg_id)
    
            work_txt_output.write(message.encode("utf-8") + "\n")

    print len(visited), len(work_dict)
    runFile(work_txt, directory)

    ##### mark the ending time of process #####
    end = timeit.default_timer()
    seconds = math.ceil(end - start)
    # Convert Secs Into Human Readable Time String (HH:MM:SS)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    print "This process took %d:%02d:%02d" % (h, m, s)

if __name__ == '__main__':
    main()