# -*- coding: utf-8 -*-
import json
import sys,getopt,datetime,codecs
from pymongo import MongoClient
if sys.version_info[0] < 3:
    import got
else:
    import got3 as got

def main(argv):
        
    MONGO_HOST = "mongodb://localhost:27017/"  #set up local mongo db
    
    if len(argv) == 0:
        print('You must pass some parameters. Use \"-h\" to help.')
        return

    if len(argv) == 1 and argv[0] == '-h':
        f = open('exporter_help_text.txt', 'r')
        print(f.read())
        f.close()

        return

    try:
        opts, args = getopt.getopt(argv, "", ("username=", "near=", "within=", "since=", "until=", "querysearch=", "toptweets", "maxtweets=", "output="))

        tweetCriteria = got.manager.TweetCriteria()
        outputFileName = "output_got.csv"

        for opt,arg in opts:
            if opt == '--username':
                tweetCriteria.username = arg
                outputFileName = "username--" + arg + ".csv"

            elif opt == '--since':
                tweetCriteria.since = arg

            elif opt == '--until':
                tweetCriteria.until = arg

            elif opt == '--querysearch':
                tweetCriteria.querySearch = arg
                outputFileName = arg + ".csv"

            elif opt == '--toptweets':
                tweetCriteria.topTweets = True

            elif opt == '--maxtweets':
                tweetCriteria.maxTweets = int(arg)
            
            elif opt == '--near':
                tweetCriteria.near = '"' + arg + '"'
            
            elif opt == '--within':
                tweetCriteria.within = '"' + arg + '"'

            elif opt == '--within':
                tweetCriteria.within = '"' + arg + '"'

            elif opt == '--output':
                outputFileName = arg
                
        outputFile = codecs.open(outputFileName, "w+", "utf-8")

        outputFile.write('username;date;retweets;favorites;text;geo;mentions;hashtags;id;permalink;v_neg;v_neu;v_pos;v_com;tb_score')

        print('Searching...\n')
        
        ### Create a dictionary holding every sub-dictionary (every row of tweets data)
        all_dict = {}
        
        def receiveBuffer(tweets): 
            
            client = MongoClient(MONGO_HOST)
            db = client.twitterdb
            num = len(all_dict) + 1
            
            for t in tweets:
                outputFile.write(('\n%s;%s;%d;%d;"%s";%s;%s;%s;"%s";%s;%f;%f;%f;%f;%f' % (t.username, t.date.strftime("%Y-%m-%d %H:%M"), t.retweets, t.favorites, t.text, t.geo, t.mentions, t.hashtags, t.id, t.permalink, t.v_neg, t.v_neu, t.v_pos, t.v_com, t.tb_score)))
                
                ### Create sub-dictionary data for every tweets                
                current_dict = 'tweet{}'.format(num)
                all_dict[current_dict] = {}                
                all_dict[current_dict]["keyword"] = outputFileName.replace('.csv', '')               
                all_dict[current_dict]["date"] = t.date.strftime("%Y-%m-%d %H:%M")
                all_dict[current_dict]["id"] = t.id
                all_dict[current_dict]["text"] = t.text 
                all_dict[current_dict]["permalink"] = t.permalink
                all_dict[current_dict]["vader_negative"] = t.v_neg
                all_dict[current_dict]["vader_neutral"] = t.v_neu
                all_dict[current_dict]["vader_positive"] = t.v_pos
                all_dict[current_dict]["vader_compound"] = t.v_com
                all_dict[current_dict]["textblob"] = t.tb_score                
                num += 1
                
                # Insert dictionary into mongodb database                
                tweet_dict = {"keyword":outputFileName.replace('.csv', ''),
                            "date": t.date.strftime("%Y-%m-%d %H:%M"),
                            "tweet_id": t.id, "text": t.text, "permalink":t.permalink,
                            "vader_negative": t.v_neg, "vader_neutral": t.v_neu,
                            "vader_positive": t.v_pos, "vader_compound": t.v_com,
                            "textblob": t.tb_score}
                db.twitter_search.insert_one(tweet_dict)                

                
            outputFile.flush()
            print('More %d saved on file...\n' % len(tweets))       

        got.manager.TweetManager.getTweets(tweetCriteria, receiveBuffer)

    except arg:
        print('Arguments parser error, try -h' + arg)
    finally:
        outputFile.close()
        ### Export all_dict to json
        with open(outputFileName.replace('csv', 'json'), 'w') as fp:
                json.dump(all_dict, fp, indent=2)
        print('Done. Output file generated "%s".' % outputFileName)
        print('Done. Output file generated "%s".' % outputFileName.replace('csv', 'json'))
        print('Done. Inserted tweets of "%s" to twitterdb (MongoDB).' % outputFileName.replace('.csv', ''))

if __name__ == '__main__':
    main(sys.argv[1:])
