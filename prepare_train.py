import ujson as json
import timeit, math, time

def timestamp2datetime(timestamp_ms):
    
    return time.ctime(int(int(timestamp_ms)/1000.0))

def read_daily_json_write_train_label(one_day_before, directory, record0, MONTHS):

    train_json = open(directory + "train.json", "w")

    for line in open(one_day_before, 'r'):
        
        tweet = json.loads(line.decode('utf-8'))
        # tweet.keys() = [u'filtering', u'contributors', u'truncated', u'text', u'in_reply_to_status_id', u'id', u'favorite_count', u'datetime retrieved', u'source', u'quoted_status_id', u'retweeted', u'coordinates', u'timestamp_ms', u'quoted_status', u'entities', u'in_reply_to_screen_name', u'id_str', u'retweet_count', u'in_reply_to_user_id', u'favorited', u'user', u'geo', u'in_reply_to_user_id_str', u'possibly_sensitive', u'lang', u'created_at', u'quoted_status_id_str', u'filter_level', u'in_reply_to_status_id_str', u'place']

        msg_id = tweet['id']
        message = tweet['text']

        user = tweet['user']       
        # user.keys() = [u'follow_request_sent', u'profile_use_background_image', u'id', u'verified', u'profile_image_url_https', u'profile_sidebar_fill_color', u'is_translator', u'geo_enabled', u'profile_text_color', u'followers_count', u'protected', u'location', u'default_profile_image', u'id_str', u'utc_offset', u'statuses_count', u'description', u'friends_count', u'profile_link_color', u'profile_image_url', u'notifications', u'profile_background_image_url_https', u'profile_background_color', u'profile_banner_url', u'profile_background_image_url', u'screen_name', u'lang', u'profile_background_tile', u'favourites_count', u'name', u'url', u'created_at', u'contributors_enabled', u'time_zone', u'profile_sidebar_border_color', u'default_profile', u'following', u'listed_count']
        userid = user['id']

        timestamp_ms = tweet['timestamp_ms']
        datetime = timestamp2datetime(timestamp_ms)

        record = parse_datetime(datetime)

        if (record[0] <= record0[0]) and (MONTHS.index(record[1]) <= MONTHS.index(record0[1])) and (record[2] <= record0[2]) and (record[4] < record0[4]):
            time_label = 'before'
        else:
            time_label = 'after'

        basic = {}
        basic['msg_id'] = msg_id
        basic['message'] = message
        basic['userid'] = userid
        basic['time_label'] = time_label

        json.dump(basic, train_json)
        train_json.write("\n")

def parse_datetime(datetime):

    datetime_elements = datetime.split()
    day = datetime_elements[0]
    month = datetime_elements[1]
    date = datetime_elements[2]
    moment = datetime_elements[3]
    hour = moment.split(":")[0]
    minute = moment.split(":")[1]
    second = moment.split(":")[2]
    year = datetime_elements[4]
    
    record = int(year), month, int(date), day, int(hour), int(minute), int(second)

    return record

def main():
    # mark the beginning time of process
    start = timeit.default_timer()

    MONTHS = [u'Jan', u'Feb', u'Mar', u'Apr', u'May', u'Jun', u'Jul', u'Aug', u'Sep', u'Oct', u'Nov', u'Dec']

    event_time = "Wed Aug 19 23:00:00 2015"
    record0 = parse_datetime(event_time)

    directory = "/Users/tl8313/Documents/ROC_shooting/"
    one_day_before = "19-08-2015.json"

    read_daily_json_write_train_label(one_day_before, directory, record0, MONTHS)

    ##### mark the ending time of process #####
    end = timeit.default_timer()
    seconds = math.ceil(end - start)
    # Convert Secs Into Human Readable Time String (HH:MM:SS)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    print "This process took %d:%02d:%02d" % (h, m, s)

if __name__ == '__main__':
    main()