import ujson as json
import timeit, math, time, pytz
from collections import defaultdict
from datetime import datetime, timedelta
from pytz import timezone

def timestamp2datetime(timestamp_ms):
    # USAGE: http://www.tutorialspoint.com/python/time_ctime.htm
    return time.ctime(int(timestamp_ms/1000.0))

def pytz_function(timestamp_ms):

    utc = pytz.utc
    # reference: https://docs.python.org/2/library/time.html#time.strftime
    # format matching event_time in main()
    fmt = '%a %b %d %H:%M:%S %Y %Z%z'

    utc_dt = utc.localize(datetime.utcfromtimestamp((timestamp_ms/1000.0)))
    utc_output = utc_dt.strftime(fmt)

    au_tz = timezone('US/Eastern')
    au_dt = au_tz.normalize(utc_dt.astimezone(au_tz))
    local_output = au_dt.strftime(fmt)

    return utc_output, local_output

def read_daily_json_write_train_label(daily_json, record0, MONTHS, train_json, before_dict, after_dict):

    for line in open(daily_json, 'r'):
        
        tweet = json.loads(line.decode('utf-8'))
        # tweet.keys() = [u'filtering', u'contributors', u'truncated', u'text', u'in_reply_to_status_id', u'id', u'favorite_count', u'datetime retrieved', u'source', u'quoted_status_id', u'retweeted', u'coordinates', u'timestamp_ms', u'quoted_status', u'entities', u'in_reply_to_screen_name', u'id_str', u'retweet_count', u'in_reply_to_user_id', u'favorited', u'user', u'geo', u'in_reply_to_user_id_str', u'possibly_sensitive', u'lang', u'created_at', u'quoted_status_id_str', u'filter_level', u'in_reply_to_status_id_str', u'place']

        msg_id = tweet['id']
        message = tweet['text']

        user = tweet['user']       
        # user.keys() = [u'follow_request_sent', u'profile_use_background_image', u'id', u'verified', u'profile_image_url_https', u'profile_sidebar_fill_color', u'is_translator', u'geo_enabled', u'profile_text_color', u'followers_count', u'protected', u'location', u'default_profile_image', u'id_str', u'utc_offset', u'statuses_count', u'description', u'friends_count', u'profile_link_color', u'profile_image_url', u'notifications', u'profile_background_image_url_https', u'profile_background_color', u'profile_banner_url', u'profile_background_image_url', u'screen_name', u'lang', u'profile_background_tile', u'favourites_count', u'name', u'url', u'created_at', u'contributors_enabled', u'time_zone', u'profile_sidebar_border_color', u'default_profile', u'following', u'listed_count']
        userid = user['id']

        timestamp_ms = float(tweet['timestamp_ms'])

        # method 1 using time.ctime
        # local_output1 = timestamp2datetime(timestamp_ms)

        # # method 2 provided by Chris
        # created_at = tweet['created_at']
        # utc_output = datetime.strptime(created_at, "%a %b %d %H:%M:%S +0000 %Y")
        # local_output2 = utc_output - timedelta(hours = 4)

        # method 3 using pytz, http://pytz.sourceforge.net/
        local_output3 = pytz_function(timestamp_ms)[1]

        record = parse_datetime(local_output3)

        # if (record[0] <= record0[0]) and (MONTHS.index(record[1]) <= MONTHS.index(record0[1])) and (record[2] <= record0[2]) and (record[4] < record0[4]):
        #     time_label = -1
        #     before_dict[msg_id] += 1
        # else:
        #     time_label = +1
        #     after_dict[msg_id] += 1

        # basic = {}
        # basic['msg_id'] = msg_id
        # basic['message'] = message
        # basic['userid'] = userid
        # basic['time_label'] = time_label

        # json.dump(basic, train_json)
        # train_json.write("\n")

def parse_datetime(datetime_format):

    datetime_elements = datetime_format.split()
    day = datetime_elements[0]
    month = datetime_elements[1]
    date = datetime_elements[2]
    moment = datetime_elements[3]
    hour = moment.split(":")[0]
    minute = moment.split(":")[1]
    second = moment.split(":")[2]
    year = datetime_elements[4]
    timezone = datetime_elements[5]
    
    record = int(year), month, int(date), day, int(hour), int(minute), int(second), timezone

    return record

def main():
    # mark the beginning time of process
    start = timeit.default_timer()

    MONTHS = [u'Jan', u'Feb', u'Mar', u'Apr', u'May', u'Jun', u'Jul', u'Aug', u'Sep', u'Oct', u'Nov', u'Dec']

    event_time = "Wed Aug 19 23:00:00 2015 EDT-0400"
    record0 = parse_datetime(event_time)

    directory = "/Users/tl8313/Documents/ROC_shooting/"
    # input daily Twitter json files
    one_day_before = "19-08-2015.json"
    one_day_after = "20-08-2015.json"

    # output destination
    train_json = open(directory + "train.json", "w")

    before_dict = defaultdict(int)
    after_dict = defaultdict(int)

    for daily_json in [one_day_before, one_day_after]:
        read_daily_json_write_train_label(daily_json, record0, MONTHS, train_json, before_dict, after_dict)

    print "Number of tweets before shooting: " + str(len(before_dict))
    print "Number of tweets after shooting: " + str(len(after_dict))

    ##### mark the ending time of process #####
    end = timeit.default_timer()
    seconds = math.ceil(end - start)
    # Convert Secs Into Human Readable Time String (HH:MM:SS)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    print "This process took %d:%02d:%02d" % (h, m, s)

if __name__ == '__main__':
    main()