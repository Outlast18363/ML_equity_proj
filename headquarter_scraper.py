import requests
from bs4 import BeautifulSoup
import csv

BASE_URL = "https://www.annualreports.com"


def get_company_details(detail_path):
    """
    Given a company's relative detail page path, fetch and parse additional company info.
    Returns a dictionary with employees, location, description, and social_media (formatted string).
    """
    detail_url = BASE_URL + detail_path
    response = requests.get(detail_url)
    if response.status_code != 200:
        print(f"Failed to fetch details for {detail_url}")
        return {}

    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract employees and location from the left_list_block02 block.
    employees = ""
    location = ""
    left_block = soup.find('div', class_='left_list_block02')
    if left_block:
        li_employees = left_block.find('li', class_='employees')
        if li_employees:
            employees = li_employees.get_text(strip=True)
        li_location = left_block.find('li', class_='location')
        if li_location:
            location = li_location.get_text(strip=True)

    # Extract company description.
    description_div = soup.find('div', class_='company_description')
    description = description_div.get_text(strip=True) if description_div else ""

    # Extract social media links and format them.
    social_media_str = ""
    social_div = soup.find('div', class_='social_media')
    if social_div:
        icons_div = social_div.find('div', class_='social_media_icons')
        if icons_div:
            links = icons_div.find_all('a')
            for idx, link in enumerate(links, start=1):
                href = link.get('href')
                social_media_str += f"Social media {idx}: {href}\n"
    social_media_str = social_media_str.strip()

    return {
        'employees': employees,
        'location': location,
        'description': description,
        'social_media': social_media_str
    }


def main():
    url = BASE_URL + "/FeaturedProgram/15"
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to retrieve the main page.")
        return

    soup = BeautifulSoup(response.content, 'html.parser')
    companies = []

    # Locate the container holding the company list.
    list_container = soup.find('div', class_='apparel_stores_company_list')
    if not list_container:
        print("Failed to locate the companies list container.")
        return

    ul = list_container.find('ul')
    if not ul:
        print("Failed to locate the companies list element.")
        return

    # Loop through all <li> elements (skip header row if present).
    for li in ul.find_all('li'):
        # Skip header rows
        if li.get('class') and "header_section" in li.get('class'):
            continue

        company = {}
        # Extract company name and the relative detail URL.
        company_name_span = li.find('span', class_='companyName')
        if company_name_span:
            a_tag = company_name_span.find('a')
            if a_tag:
                company['company_name'] = a_tag.get_text(strip=True)
                detail_path = a_tag.get('href')
                company['detail_link'] = detail_path #Store the subpage of the company

        # Extract industry and sector.
        industry_span = li.find('span', class_='industryName')
        if industry_span:
            company['industry'] = industry_span.get_text(strip=True)
        sector_span = li.find('span', class_='sectorName')
        if sector_span:
            company['sector'] = sector_span.get_text(strip=True)

        # Visit the company detail page if the link exists.
        if 'detail_link' in company:
            details = get_company_details(company['detail_link'])
            company.update(details)

        companies.append(company)
        company_searched = len(companies)
        if(company_searched % 50 == 0):
            print(f'{company_searched} companies searched')

    # Write the company data to a CSV file.
    csv_filename = "company headquarter dataset.csv"
    fieldnames = ['company_name', 'industry', 'sector', 'employees', 'location', 'description', 'social_media']
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for comp in companies:
            writer.writerow({
                'company_name': comp.get('company_name', ''),
                'industry': comp.get('industry', ''),
                'sector': comp.get('sector', ''),
                'employees': comp.get('employees', ''),
                'location': comp.get('location', ''),
                'description': comp.get('description', ''),
                'social_media': comp.get('social_media', '')
            })

    print(f"Data successfully written to '{csv_filename}'")


if __name__ == "__main__":
    main()
