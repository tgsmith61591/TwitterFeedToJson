##Twitter Feed Scraper

In whatever file structure you have, make sure you have a folder named 'Credentials' (case-sensitive unless you edit the code) in the same root as the python script with a format as shown in the screenshot — fileStructure.png. *Important: make sure all .txt files are terminated in a line separator. This is a Tweepy authorization bug.*

This is written to accept args from the command line. So, for instance, to get all my tweets, I would type:

```
python FeedParse.py TayGriffinSmith 200
```

...where 200 is the max tweets to pull (note: 200 is the max the API will allow). This will write a JSON into the same directory as the script.