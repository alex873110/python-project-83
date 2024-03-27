from bs4 import BeautifulSoup


def get_seo(content):
    soup = BeautifulSoup(content, 'html.parser')
    title = soup.title
    title = title.string if title else ''
    h1 = soup.h1.text if soup.h1 else ''
    description_tag = soup.find('meta', {name: 'description'})
    description = description_tag['content'] if description_tag else ''
    description = description if len(description) < 255 else description[:252] + '...'
    return title, h1, description
