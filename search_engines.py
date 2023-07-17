import webbrowser

haram_allowed = False

def open_chrome_tab(url):
    #import webbrowser

    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chrome_path))
    webbrowser.get('chrome').open_new_tab(url)

def search_spotify(search_term):
    search_term = search_term.replace(' ', '%20')
    # https://open.spotify.com/search/brian%20green
    url = f'https://open.spotify.com/search/{search_term}'
    open_chrome_tab(url)

def search_google(search_term):
    search_term = search_term.replace(' ', '+')
    url = f'https://www.google.com/search?q={search_term}'
    open_chrome_tab(url)

def search_google_site(search_term, site):
    search_term = search_term.replace(' ', '+')
    url = f'https://www.google.com/search?q={search_term}+site%3A{site}'
    open_chrome_tab(url)

def search_google_img(search_term):
    search_term = search_term.replace(' ', '+')
    url = f'https://www.google.com/search?tbm=isch&q={search_term}'
    open_chrome_tab(url)

def search_youtube(search_term):
    search_term = search_term.replace(' ', '+')
    url = f'https://www.youtube.com/results?search_query={search_term}'
    open_chrome_tab(url)

def youtubedl(url):
    """
    can replace this with yt-dlp: https://github.com/yt-dlp/yt-dlp
    example code:
        link = 'youtube.com/watch?v=deeznuts'  # video link
        path = f'{vid_folder}/{time.time()}.mp4'  # output path
        subprocess.run([
            'yt-dlp',
            link,
            '--output',
            path
        ])
    """
    url = url.replace('youtube.com', 'youtubepp.com')
    open_chrome_tab(url)

def urban_dictionary(search_term):
    search_term = search_term.replace(' ', '%20')
    url = f'https://www.urbandictionary.com/define.php?term={search_term}'
    open_chrome_tab(url)

def do_search(engine, term, site=None):
    mapping = {
        'google': search_google,
        'youtube': search_youtube,
        'google site': search_google_site,
        'spotify': search_spotify,
        'google img': search_google_img,
        'youtubedl': youtubedl,
        'urban': urban_dictionary,
    }
    func = mapping[engine]
    if engine == 'google site':
        func(term, site)
    else:
        func(term)

