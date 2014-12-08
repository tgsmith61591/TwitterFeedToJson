import time, sys, string, csv, re, io, os
import tweepy
from tweepy.parsers import JSONParser
startTime = time.time()

#-----------------Preference Section:-----------------#
def parseBool(arg):
    punct = ['-','--','\'',"\""]
    a = ''.join([ch for ch in str(arg) if not ch in punct]).lower()
    return a == 't' or a == 'true'
    
## Username:
UserName = sys.argv[1] if len(sys.argv) > 0 else None
maxTweets= sys.argv[2] if len(sys.argv) > 1 else None
writeCsv = parseBool(sys.argv[3]) if len(sys.argv) > 2 else True
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
    

#-----------------Clas def Section:-----------------#
class TwitterUserFeed:
    ## Note: max_tweets cannot be greater than 200
    def __init__(self, auth, username, max_tweets):
        self.username = username
        self.max_tweets = max_tweets if (max_tweets <= 200 and max_tweets > 0)\
                            else 20 if max_tweets <= 0 else 200 ## Catch dumb users
        self.auth = auth
        self.tweets = None  ## Init null
        self.feed = None    ## Init null
        self.headers = None ## Csv headers, init null
        
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
        
    def _parseUserTweetsToCsv_(self, json):
        ## Name, text
        parsed = list()
        for key in self.headers:
            ## print key
            if key == 'text':
                parsed.append( str(self._removePunct(self._removeNonAscii(json[key]))) )
            elif key == 'user':
                parsed.append( str(json[key]['screen_name']) )
            else:
                parsed.append(str(json[key]))
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
        
        removes = ['entities','possibly_sensitive'] ## Headers we don't want
        headers = json[0].keys()
        self.headers = [k for k in headers if not k in removes]
        
        for tweet in json:
            parsed_tweet = self._parseUserTweetsToCsv_(tweet)
            tweets.append(parsed_tweet)
        
        if not tweets or len(tweets)==0:
            raise ("No tweets to write")
        
        with open(self.username + '_TwitterFeed.csv' , 'w') as output:
            writer = csv.writer(output, delimiter= ',', lineterminator = '\n')
            writer.writerow(self.headers)
            writer.writerows(tweets)
            
    def writeTweetsToJson(self):
        tweets = self.getTweets()
        jsonOut = '['+os.linesep
        for tweet in tweets:
            jsonOut+='\t'+str(tweet)+os.linesep
        jsonOut += ']'
        with io.open(self.username+'_TwitterFeed.json','w') as output:
            output.write(unicode(jsonOut))

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
    if writeCsv: ## third command line arg
        t.writeTweetsToCsv()
    
    runtime = "Completed request in " + str(time.time() - startTime) + " seconds"
    print runtime
#------------------/End Main/------------------#

