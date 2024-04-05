from youtube_search import YoutubeSearch

def youtube_search(query):
    yt = YoutubeSearch(query, max_results=20)
    return yt.to_dict()


