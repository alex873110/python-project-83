from bs4 import BeautifulSoup


def get_seo(content):
    data = BeautifulSoup(content, 'html.parser')
    title = data.title
    title = title.string if title else ''
    h1 = data.h1.text if content.h1 else ''
    description_tag = data.find("meta", attrs={"name": "description"})
    description = description_tag["content"] if description_tag else ''
    description = description if len(description) < 255 else description[:252] + '...'
    return {"title": title, "h1": h1, 'description': description}
