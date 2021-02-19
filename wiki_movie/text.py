STOPWORDS = {'\n', '\t', 'e.g.', '[sic]', '[...]', 'i.e.', }
EXCLUDED_SECTIONS = {'See also', 'References', 'Further reading', 'External links', 'Formats and track listings',
                     'Credits and personnel', 'Charts', 'Certifications', 'Release history'}


def generate_section_dictionaries_list(page):
    """
    page (wikipediaapia.WikipediaPage)
    """
    script = [{'title': page.title, 'level': 0, 'text': remove_stopwords(page.summary)}]
    flush_sections(script, page.sections)
    return script


def flush_sections(script, sections, level=0):
    """
    Recurse through page levels (sections, subsections) and clean the text, modifying script in place.

    script (list)
    sections (list) -- list of WikipediaPageSections
    level (int)
    """
    for s in sections:
        if s.title in EXCLUDED_SECTIONS:
            print('excluding', s.title)
            continue
        else:
            script.append({'title': s.title, 'level': level + 1, 'text': remove_stopwords(s.text)})
            flush_sections(script, s.sections, level + 1)


def remove_stopwords(text):
    for x in STOPWORDS:
        text = text.replace(x, '')
    return text
