#import the necessary modules
import tweepy
import pickle
import csv
from requests_html import HTMLSession
#stats on twitter bot from dev website
consumer_key = 'CONSUMER-KEY'
consumer_secret = 'CONSUMER-SECRET'
access_token = 'ACCESS-TOKEN'
access_secret = 'ACCESS-SECRET'

#sets variable for certain stats
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)
api = tweepy.API(auth)

#initializes account
user = api.me()

#hash for tweet id and their reply text
replies = {}

#sets replied list equal to the replied.pkl file
with open('replied.pkl', 'rb') as f:
    replied = pickle.load(f)
#create a list of mentions to iterate through
mentions = api.search(q="@BaseballStatsB1")
#sets the csv file name equal to a variable
filename = 'player_info.txt'
#function to get the values needed for the url based on csv file and input text
def getValues(filename, text):
    with open(filename, encoding="mbcs") as f:
        for row in csv.reader(f):
            if row[1] == text:
                return text, row[8]
        return None, None

#checks if player is in mlb player list
def check_in_list(text):
    with open("player_info.txt" , encoding="mbcs") as f:
        for row in csv.reader(f):
            if row[1] == text:
                return text
        return None

#determines if player is a pitcher or hitter, returns position
def is_pitcher(url):
    s = HTMLSession()
    page = s.get(url)
    page.html.render(sleep=1, timeout=20)
    pos = page.html.xpath('/html/body/div[1]/div[2]/div[1]/div/div[1]/div[5]')[0].text
    return pos

#gets stats for hitters
def get_hitter_stats(url):
    s = HTMLSession()
    page = s.get(url)
    page.html.render(sleep=1, timeout=20)
    position = page.html.xpath('/html/body/div[1]/div[2]/div[1]/div/div[1]/div[5]')[0].text
    games = page.html.xpath('/html/body/div[1]/div[2]/div[3]/div/div[2]/div[3]/div/div/div/div[1]/table/tbody/tr[35]/td[4]')[0].text
    avg = page.html.xpath('/html/body/div[1]/div[2]/div[3]/div/div[2]/div[3]/div/div/div/div[1]/table/tbody/tr[35]/td[16]')[0].text
    obp = page.html.xpath('/html/body/div[1]/div[2]/div[3]/div/div[2]/div[3]/div/div/div/div[1]/table/tbody/tr[35]/td[17]')[0].text
    slg = page.html.xpath('/html/body/div[1]/div[2]/div[3]/div/div[2]/div[3]/div/div/div/div[1]/table/tbody/tr[35]/td[18]')[0].text
    hr = page.html.xpath('/html/body/div[1]/div[2]/div[3]/div/div[2]/div[3]/div/div/div/div[1]/table/tbody/tr[35]/td[6]')[0].text
    rbi = page.html.xpath('/html/body/div[1]/div[2]/div[3]/div/div[2]/div[3]/div/div/div/div[1]/table/tbody/tr[35]/td[8]')[0].text
    sb = page.html.xpath('/html/body/div[1]/div[2]/div[3]/div/div[2]/div[3]/div/div/div/div[1]/table/tbody/tr[35]/td[9]')[0].text
    fwar = page.html.xpath('/html/body/div[1]/div[2]/div[3]/div/div[2]/div[3]/div/div/div/div[1]/table/tbody/tr[35]/td[28]')[0].text

    return position, games, avg, obp, slg, hr, rbi, sb, fwar

#gets stats for pitchers
def get_pitcher_stats(url):
    s = HTMLSession()
    page = s.get(url)
    page.html.render(sleep=1, timeout=20)
    games = page.html.xpath('/html/body/div[1]/div[2]/div[3]/div/div[2]/div[3]/div/div/div/div[1]/table/tbody/tr[42]/td[7]')[0].text
    if page.html.xpath('/html/body/div[1]/div[2]/div[1]/div/div[1]/div[3]', first = True).text[-1:] == 'R':
        position = 'RHP'
    else:
        position = 'LHP'
    wins = page.html.xpath('/html/body/div[1]/div[2]/div[3]/div/div[2]/div[3]/div/div/div/div[1]/table/tbody/tr[42]/td[4]')[0].text
    losses = page.html.xpath('/html/body/div[1]/div[2]/div[3]/div/div[2]/div[3]/div/div/div/div[1]/table/tbody/tr[42]/td[5]')[0].text
    era = page.html.xpath('/html/body/div[1]/div[2]/div[3]/div/div[2]/div[3]/div/div/div/div[1]/table/tbody/tr[42]/td[21]')[0].text
    ip = page.html.xpath('/html/body/div[1]/div[2]/div[3]/div/div[2]/div[3]/div/div/div/div[1]/table/tbody/tr[42]/td[9]')[0].text
    so = page.html.xpath('/html/body/div[1]/div[2]/div[3]/div/div[3]/div[3]/div/div/div/div[1]/table/tbody/tr[42]/td[25]')[0].text
    whip = page.html.xpath('/html/body/div[1]/div[2]/div[3]/div/div[5]/div[3]/div/div/div/div[1]/table/tbody/tr[63]/td[14]')[0].text
    fwar = page.html.xpath('/html/body/div[1]/div[2]/div[3]/div/div[2]/div[3]/div/div/div/div[1]/table/tbody/tr[42]/td[24]')[0].text
    return position, games, wins, losses, era, ip, so, whip, fwar

#parses through each mention and adds the text to replies if the tweet id has not already been replied to and the player name is in the csv file
for mention in mentions:
    #gets raw player name
    mention_name = mention.text.replace('@BaseballStatsB1 ', '').lstrip().rstrip()
    #if unique tweet not been replied to before and is an mlb player
    if mention.id_str not in replied and check_in_list(mention_name) != None:
        #add necessary user id, tweet id, and mention text to the replies dict
        replies[str(mention.id)] = [mention.user.screen_name, mention_name]

for id, name in replies.items():
    playername, user_id = getValues(filename, name[1])
    if playername != None:
        new_text = playername.split()
        player_name = new_text[0] + '-' + new_text[1]
        player_url = f"https://www.fangraphs.com/players/{player_name}/{user_id}"
        pos = is_pitcher(player_url)
        if pos == 'P':
            stats = get_pitcher_stats(player_url)
            pos = stats[0]
            games = stats[1]
            wins = stats[2]
            losses = stats[3]
            era = stats[4]
            ip = stats[5]
            so = stats[6]
            whip = stats[7]
            fwar = stats[8]
            stat_line = f"{playername}, {pos}, {games} G, {wins}-{losses} W-L, {era} ERA, {ip} IP, {so} K, {whip} WHIP, {fwar} fWAR"
        else:
            stats = get_hitter_stats(player_url)
            pos = stats[0]
            games = stats[1]
            avg = stats[2]
            obp = stats[3]
            slg = stats[4]
            hr = stats[5]
            rbi = stats[6]
            sb = stats[7]
            fwar = stats[8]
            stat_line = f"{playername}, {pos}, {games} G, {avg}/{obp}/{slg} AVG/OBP/SLG, {hr} HR, {rbi} RBI, {sb} SB, {fwar} fWAR"
        status_text = '@' + name[0] + ' ' + stat_line

        api.update_status(status=status_text,in_reply_to_status_id=id)
        replied.append(id)

with open('replied.pkl', 'wb') as f:
    pickle.dump(replied, f)


