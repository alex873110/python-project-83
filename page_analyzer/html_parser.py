from bs4 import BeautifulSoup


def get_seo(content):
    content = BeautifulSoup(content, 'html.parser')
    title = content.title
    title = title.string if title else ''
    h1 = content.h1.text if content.h1 else ''
    description = content.find("meta", attrs={"name": "description"})
    description = description.get("content", None) if description else ''
    description = description if len(description) < 255 else description[:252] + '...'
    return {"title": title, "h1": h1, "description": description}
