import time, sys, string, csv, re, io
import tweepy
from tweepy.parsers import JSONParser
startTime = time.time()

#-----------------Preference Section:-----------------#
## Username:
UserName = sys.argv[1] if len(sys.argv) > 0 else None
maxTweets= sys.argv[2] if len(sys.argv) > 1 else None
auth = None
api = None

#-----------------Authorization Section:-----------------#
#It is important to check for newline characters at the end of each
#text document; these will result in an OAuth failure with a "failed
#to validate tokens" Traceback. Always check twice!
def _authorize():
    global auth
    global api
    
    CONSUMER_SECRET = open('Credentials/Consumer Secret.txt', 'r').read()
    CONSUMER_KEY = open('Credentials/Consumer Key.txt', 'r').read()
    #PASSWORD = open('Credentials/password.txt','r').read()
    #USER = open('Credentials/user.txt','r').read()

    ACCESS_TOKEN = open('Credentials/Access Token.txt', 'r').read()
    ACCESS_TOKEN_SECRET = open('Credentials/Access Token Secret.txt', 'r').read()

    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth, parser=JSONParser())
    

class TwitterUserFeed:
    ## Note: max_tweets cannot be greater than 200
    def __init__(self, auth, username, max_tweets):
        self.username = username
        self.max_tweets = max_tweets if (max_tweets <= 200 and max_tweets > 0)\
                            else 20 if max_tweets <= 0 else 200 ## Catch dumb users
        self.auth = auth
        self.tweets = None
        self.feed = None
        
    def getTweets(self):
        ## Cached if already run for this user
        if not self.feed is None:
            return self.feed
        
        ## Else go grab 'em
        try:
            feed = api.user_timeline(screen_name = self.username, count=self.max_tweets)
            self.feed = feed
            return feed
            #return tweets
        except:
            print "There was a problem accessing", self.username+"'s feed."
        
    def _parseUserTweetsToJson_(self, json):
        ## Name, text
        parsed = list()
        
        name = str(json['user']['screen_name'])
        date = str(json['created_at'])
        text = str( self._removeUrls(self._removePunct(self._removeNonAscii(json['text']))) )
        rtwtd= str(json['retweeted'])
        
        parsed.extend([name,date,text,rtwtd])
        return parsed
        
    def _removeNonAscii(self, s): ## Clean up the unparseables
        #Replace with '.' because later remove punct;
        #if we were to replace with a ' ' then there would
        #be appended a large number of ''s later.
        s = re.sub(r'[^\x00-\x7F]+','.', s)
        return "".join(i for i in s if ord(i)<128)
    
    def _removePunct(self,s): ## Remove all punct except @
        exclude = set(string.punctuation)
        exclude = [pun for pun in exclude if not (pun == '@')]
        s = ''.join(ch for ch in s if ch not in exclude)
        return s
    
    def _removeUrls(self, s):
        s = s.split(' ')
        ## Admittedly, potential bugs here... but rarely will httptco show up otherwise
        s = ' '.join(ch for ch in s if not ('httptco' in ch or 'httpstco' in ch) )
        return s
    
    def writeTweetsToCsv(self):
        json = self.getTweets()
        tweets = list()
        for tweet in json:
            parsed_tweet = self._parseUserTweetsToJson_(tweet)
            tweets.append(parsed_tweet)
        
        if not tweets or len(tweets)==0:
            raise ("No tweets to write")
        
        with open(self.username + '_TwitterFeed.csv' , 'w') as output:
            writer = csv.writer(output, delimiter= ',', lineterminator = '\n')
            writer.writerow(['User','Date','Text','Retweeted'])
            writer.writerows(tweets)
            
    def writeTweetsToJson(self):
        tweets = self.getTweets()
        with io.open(self.username+'_TwitterFeed.json','w') as output:
            output.write(unicode(tweets))

#-----------------Define Main:-----------------#   
if __name__ == '__main__':
    ## Check, make sure cmd line args are good
    if not UserName: 
        raise ("Illegal Twitter username")
    elif not maxTweets:
        raise ("Need number of tweets to pull")
    _authorize()
    
    t = TwitterUserFeed(auth, UserName, maxTweets)
    t.writeTweetsToJson()
    #t.writeTweetsToCsv() # << If you want to write it to CSV
    
    runtime = str(time.time() - startTime) + " seconds"
    #print runtime
#------------------/End Main/------------------#

