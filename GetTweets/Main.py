import sys
if sys.version_info[0] < 3:
    import got
else:
    import got3 as got

def main():

	def printTweet(descr, t):
		print(descr)
		print("Username: %s" % t.username)
		#print("Retweets: %d" % t.retweets)
		print("Text: %s" % t.text)        
		print("Date: %s" % t.date)
        #print("Date: %s" % t.date)
		#print("Hashtags: %s\n" % t.hashtags)

	# Get tweets by query search
	tweetCriteria = got.manager.TweetCriteria().setQuerySearch('').setSince("2019-09-01").setUntil("2019-09-02").setMaxTweets(10)
	tweet = got.manager.TweetManager.getTweets(tweetCriteria)[1]   
	printTweet("### Example 2 - Get tweets by query search [Coach]", tweet)

if __name__ == '__main__':
	main()