from bs4 import BeautifulSoup


def get_seo(content):
    content = BeautifulSoup(content, 'html.parser')
    title = content.title
    title = title.string if title else None
    h1 = content.h1.text if content.h1 else None
    description = content.find("meta", attrs={"name": "description"})
    description = description.get("content", None) if description else None
    return {"title": title, "h1": h1, "description": description}
