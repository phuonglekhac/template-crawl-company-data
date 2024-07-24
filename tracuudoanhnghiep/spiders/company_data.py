from typing import List
import scrapy
import scrapy.spiders


def get_next_page_url(response):
    """
    Get the URL of the next page in the pagination.

    Args:
        response (scrapy.http.Response): The response from the current page.

    Returns:
        str or None: The URL of the next page if there is one, None otherwise.
    """
    # Find all the pagination links on the page
    pagination_links = response.xpath(
        '//div[@class="content-page"]//div[@class="box_content"]/div[@class="next-page"]/a'
    )

    # Loop through the pagination links
    for index, link in enumerate(pagination_links):
        # Check if the current link is the active one
        if "active" in link.attrib.get("class", "").split():
            # If it is the last link, return None
            if index == len(pagination_links) - 1:
                return None
            # If it is not the last link, return the href of the next link
            return pagination_links[index + 1].attrib.get("href")

    # If no active link is found, return None
    return None


def extract_company_detail_urls(response: scrapy.http.Response) -> List[str]:
    """
    Extract the URLs of the company detail pages.

    Args:
        response (scrapy.http.Response): The response from the list of companies page.

    Returns:
        List[str]: The URLs of the company detail pages.
    """
    # Use a more specific XPath to directly extract the href attributes
    detail_page_hrefs = response.xpath(
        '//div[@class="content-page"]//div[@class="box_content"]/ul/li/h2/a/@href'
    ).getall()

    # Prepend the base URL to the relative paths
    detail_page_urls = [response.urljoin(href) for href in detail_page_hrefs]

    return detail_page_urls


class CompanyDataSpider(scrapy.Spider):
    """
    Spider class for extracting company data from the website.
    """

    name = "company_data"
    allowed_domains = ["tracuudoanhnghiep.vn"]
    start_urls = ["https://tracuudoanhnghiep.vn"]

    # This function is used to parse the list of companies page
    def parse(self, response):
        """
        Parses the response and extracts company detail page URLs.

        Args:
            response (scrapy.http.Response): The response from the list of companies page.
        """
        # Extract company detail page URLs from the response
        company_detail_urls = extract_company_detail_urls(response)
        for url in company_detail_urls:
            yield scrapy.Request(
                url,
                callback=self.parse_company_detail,
                headers={"Referer": response.url},
                meta={"referer": response.url},
            )
        # Consider next page
        next_page_url = get_next_page_url(response)
        if next_page_url:
            yield response.follow(
                next_page_url,
                callback=self.parse,
                headers={"Referer": response.url},
                meta={"referer": response.url},
            )

    def parse_company_detail(self, response):
        """
        Parses the response and extracts company data.

        Args:
            response (scrapy.http.Response): The response from the company detail page.
        """
        # Extract company data from the response
        company_name = response.xpath(
            '//div[@class="content-page"]//div[@class="box_content"]/h1/text()'
        )
        # ....
        # ....

        data = {
            "company_name": company_name,
            # ...
        }
        yield data
