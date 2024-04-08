from bs4 import BeautifulSoup


def get_seo_data(content):
    soup = BeautifulSoup(content, 'html.parser')
    title = soup.title
    title = title.string if title else ''
    title = title[:255]
    h1 = soup.h1.text if soup.h1 else ''
    h1 = h1[:255]
    description_tag = soup.find("meta", attrs={'name': "description"})
    description = description_tag['content'] if description_tag else ''
    description = description[:255]
    return title, h1, description
