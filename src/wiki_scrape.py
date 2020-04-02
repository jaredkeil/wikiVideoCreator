import wikipedia

def parse_wiki(page_name):
    page = wikipedia.page(page_name)
    title = page.title
    script = page.content
    ### Here would be the place to parse script
    print("Video Title: ", title)
    return title, script