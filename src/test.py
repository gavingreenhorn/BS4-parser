def scrape_article_for_status(url):
    print(url)
    soup = BeautifulSoup(
        get_response(session, urljoin(PEPS_URL, url)).text,
        features='lxml',
        parse_only=SoupStrainer('dl', class_='field-list')
    )
    print(soup)
    status_tag = soup.find('dt', text=re.compile('Status'))
    if status_tag:
        print(status_tag)
        return status_tag.find_next_sibling().text