from bs4 import BeautifulSoup


def get_seo_data(content):
    soup = BeautifulSoup(content, 'html.parser')
    title = soup.title
    title = title.string if title else ''
    if len(title) >= 255:
        title = title[:252] + '...'
    h1 = soup.h1.text if soup.h1 else ''
    if len(h1) >= 255:
        h1 = h1[:252] + '...'
    description_tag = soup.find("meta", attrs={'name': "description"})
    description = description_tag['content'] if description_tag else ''
    if len(description) >= 255:
        description = description[:252] + '...'
    return title, h1, description
