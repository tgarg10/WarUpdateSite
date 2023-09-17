from django.shortcuts import render
import praw
import numpy as np
import datetime
import requests

reddit = praw.Reddit(client_id='piQ8B4HiGXCVXg-vVzI6Qg',
                     client_secret='0D2dgM6-f8qMKpTO3tPHiwR4Uxw3mg',
                     user_agent = 'PrawScraping1')

r_ukraine = reddit.subreddit('ukraine')
r_UkraineWarReports = reddit.subreddit('UkraineWarReports')

# Trigger Words
#### Help
help_trigger_words = ['help', 'volunteer'] 

# Trigger Flairs
#### War Updates
updates_trigger_flairs1 = ['Government', 'WAR', 'News']
updates_trigger_flairs2 = ['Military', 'New update']
#### Posts 
posts_trigger_flairs1 = ['Media']
posts_trigger_flairs2 = ['Discussion', 'Bombing', 'Civilians', 'Video']

def home(request):
    refugees_num = 0
    migration_countries = np.empty((0,2))
    r = requests.get("https://data2.unhcr.org/population/get/sublocation?widget_id=283575&sv_id=54&population_group=5459,5460&forcesublocation=0&fromDate=1900-01-01")
    countries_list = r.json()["data"]
    for country in countries_list:
        refugees_num += int(country['individuals'])
        migration_countries = np.append(migration_countries, np.array([[country['geomaster_name'], f"{int(country['individuals']):,}"]]), axis=0)
    
    refugees_num = f'{refugees_num:,}'                  # comma seperation
    start_date = datetime.datetime(2022, 2, 23)         # war start date
    current_date = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    days = (current_date - start_date).days
    if current_date.hour < 8:
        days -= 1 # map doesn't update before GMT 8
    return render(request, 'home.html', {'day': days, 'refugees_num': refugees_num, 'migration_countries': migration_countries})

def trending(request):
    if request.method == "POST" and request.POST.get("search_text") != "":
        search_text = request.POST.get("search_text")
        urls = Trending(search_text)
    else:
        urls = Trending()
        
    return render(request, 'trending.html', {'urls': urls})

def updates(request):
    if request.method == "POST" and request.POST.get("search_text") != "":
        search_text = request.POST.get("search_text")
        urls = Updates(search_text)
    else:
        urls = Updates()
    return render(request, 'updates.html', {'urls': urls})

def posts(request):
    if request.method == "POST" and request.POST.get("search_text") != "":
        search_text = request.POST.get("search_text")
        urls = Posts(search_text)
    else:
        urls = Posts()
    return render(request, 'posts.html', {'urls': urls})

def volunteerhelp(request):
    if request.method == "POST" and request.POST.get("search_text") != "":
        search_text = request.POST.get("search_text")
        urls = Help(search_text)
    else:
        urls = Help()
    return render(request, 'help.html', {'urls': urls})


def Trending(Search = None, limit_1 = 20, limit_2=5):
    trending_links = np.array([])
    
    hot_r_ukraine = r_ukraine.hot(limit=limit_1) # top 40 Reddit Posts r/Ukraine
    hot_r_UkraineWarReports = r_UkraineWarReports.hot(limit=limit_2) # top 10 Reddit Posts r/UkraineWarReports

    if Search is None:
        for post in hot_r_ukraine:
            trending_links = np.append(trending_links, post.permalink)
            
        for post in hot_r_UkraineWarReports:
            trending_links = np.append(trending_links, post.permalink)

    else:
        Search = Search.lower().split()
        for post in hot_r_ukraine:
            if any(search_word in post.title.lower() or search_word in post.selftext.lower() for search_word in Search):
                trending_links = np.append(trending_links, post.permalink)    
        for post in hot_r_UkraineWarReports:
            if any(search_word in post.title.lower() or search_word in post.selftext.lower() for search_word in Search):
                trending_links = np.append(trending_links, post.permalink)    
    np.random.shuffle(trending_links)
    return trending_links

def Updates(Search=None, limit_1 = 80, limit_2=40):
    # War Updates
    updates_links = np.array([])

    updates_r_ukraine = r_ukraine.hot(limit=limit_1)
    updates_r_UkraineWarReports = r_UkraineWarReports.hot(limit=limit_2)
    
    if Search is None:
        for post in updates_r_ukraine:
            if (post.link_flair_text is not None) and any(flair in post.link_flair_text for flair in updates_trigger_flairs1):
                updates_links = np.append(updates_links, post.permalink)
          
        for post in updates_r_UkraineWarReports:
            if (post.link_flair_text is not None) and any(flair in post.link_flair_text for flair in updates_trigger_flairs2):
                updates_links = np.append(updates_links, post.permalink)
    else:
        Search = Search.lower().split()
        for post in updates_r_ukraine:
            if (post.link_flair_text is not None) and any(flair in post.link_flair_text for flair in updates_trigger_flairs1) and (any(search_word in post.title.lower() or search_word in post.selftext.lower() for search_word in Search)):
                updates_links = np.append(updates_links, post.permalink)
    
        for post in updates_r_UkraineWarReports:
            if (post.link_flair_text is not None) and any(flair in post.link_flair_text for flair in updates_trigger_flairs2) and (any(search_word in post.title.lower() or search_word in post.selftext.lower() for search_word in Search)):
                updates_links = np.append(updates_links, post.permalink)
                
    np.random.shuffle(updates_links)
    return updates_links

def Posts(Search = None, limit_1 = 80, limit_2=40):
    posts_links = np.array([])

    posts_r_ukraine = r_ukraine.hot(limit=limit_1)
    posts_r_UkraineWarReports = r_UkraineWarReports.hot(limit=limit_2)

    if Search is None:
        for post in posts_r_ukraine:
            if (post.link_flair_text is not None) and any(flair in post.link_flair_text for flair in posts_trigger_flairs1):
                posts_links = np.append(posts_links, post.permalink)
          
        for post in posts_r_UkraineWarReports:
            if (post.link_flair_text is not None) and any(flair in post.link_flair_text for flair in posts_trigger_flairs2):
                posts_links = np.append(posts_links, post.permalink)

    else:
        Search = Search.lower().split()
        for post in posts_r_ukraine:
            if (post.link_flair_text is not None) and any(flair in post.link_flair_text for flair in posts_trigger_flairs1) and (any(search_word in post.title.lower() or search_word in post.selftext.lower() for search_word in Search)):
                posts_links = np.append(posts_links, post.permalink)
          
        for post in posts_r_UkraineWarReports:
            if (post.link_flair_text is not None) and any(flair in post.link_flair_text for flair in posts_trigger_flairs2) and (any(search_word in post.title.lower() or search_word in post.selftext.lower() for search_word in Search)):
                posts_links = np.append(posts_links, post.permalink)
                
    np.random.shuffle(posts_links)
    return posts_links

def Help(Search = None, limit_1 = 200, limit_2=100):
    # find more at r/ukrainevolunteers/
    help_links = np.array([])

    help_r_ukraine = r_ukraine.new(limit=limit_1)
    help_r_UkraineWarReports = r_UkraineWarReports.new(limit=limit_2)
    
    if Search is None:
        for post in help_r_ukraine:
            if any(word in post.title for word in help_trigger_words):
                help_links = np.append(help_links, post.permalink)
          
        for post in help_r_UkraineWarReports:
            if any(word in post.title for word in help_trigger_words):
                help_links = np.append(help_links, post.permalink)

    else:
        Search = Search.lower().split()
        for post in help_r_ukraine:
            if any(word in post.title for word in help_trigger_words) and (any(search_word in post.title.lower() or search_word in post.selftext.lower() for search_word in Search)):
                help_links = np.append(help_links, post.permalink)
          
        for post in help_r_UkraineWarReports:
            if any(word in post.title for word in help_trigger_words) and (any(search_word in post.title.lower() or search_word in post.selftext.lower() for search_word in Search)):
                help_links = np.append(help_links, post.permalink)
                
    return help_links