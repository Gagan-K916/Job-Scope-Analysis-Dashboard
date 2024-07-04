from selenium import webdriver
from bs4 import BeautifulSoup

import math
import csv

from time import sleep

target_companies = [
    # 211,#corporate
    213,#Foreign MNC
    217,#Indian MNC
    62,#Startup
    ]

base_url = 'https://www.naukri.com/companies-hiring-in-india'
options = webdriver.EdgeOptions()
options.add_argument("--disable-logging")
options.add_argument('--log-level=3')

driver = webdriver.Edge(options = options)

def getPageNumber(soup):
    no_of_companies = int(soup.find('h2', class_ = 'main-3 subhead').text.split(" ")[1])
    return no_of_companies, math.ceil(no_of_companies/48)

def getCompanyURLs(soup):
    hrefs = []
    for title in soup.find_all('a', class_ = 'titleAnchor'):
        if title.attrs.get('href'):
            hrefs.append(title.attrs.get('href'))
    return hrefs

def getCompanyType(company_code):
    if company_code == 211:
        return "Corporate"
    elif company_code == 213:
        return "Foreign MNC"
    elif company_code == 217:
        return "Indian MNC"
    elif company_code == 62:
        return "Startup"

with open("../company.csv", 'w',newline = '') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow([
        'Company Name',
        'Rating',
        'No_of_Reviews',
        'No_of_Followers',
        'Tags',
        'Type',
        'Year Founded',
        'Company Size',
        'HQ Location'
        'Website',
        'Company Type'
    ])
    for target_company in target_companies:
        print(f"\n------------------------------------------\n\nScraping {getCompanyType(target_company)} details from Naukri.com ... ")

        url = f"{base_url}?pageNo=1&qcbusinessSize={target_company}"
        print(url)
        driver.get(url)
        sleep(2)#2

        listings_soup = BeautifulSoup(driver.page_source, 'html.parser')

        no_of_companies, no_of_pages = getPageNumber(listings_soup)
        print(f"\nFound a total of {no_of_companies} posts of type'{getCompanyType(target_company)}' i.e {no_of_pages} pages of companies.")
        count = 0

        for no in range(1, no_of_pages+1):
            print(f"Scraping page no {no}. Total Rows Scraped {count}...")
            page_url = f"{base_url}?pageNo={no}&qcbusinessSize={target_company}"

            driver.get(page_url)
            sleep(1.5)#2
            
            page_soup = BeautifulSoup(driver.page_source, 'html.parser')

            hrefs = getCompanyURLs(page_soup)

            for link in hrefs:
                temp_url = 'https://www.naukri.com'+link
                driver.get(temp_url.replace('tab=jobs&',''))
                
                sleep(1.5)

                post_soup = BeautifulSoup(driver.page_source, 'html.parser')

                if post_soup.find('div', class_ = 'heading-line') != None:
                    company_name = post_soup.find('div', class_ = 'heading-line').h1.text
                else:
                    company_name = None

                if post_soup.find('span', class_ = 'typ-14Bold')!=None:
                    rating = post_soup.find('span', class_ = 'typ-14Bold').text
                else:
                    rating = None

                if post_soup.find('span', class_ = 'reviews typ-14Medium')!=None:
                    reviews = post_soup.find('span', class_ = 'reviews typ-14Medium').text
                else:
                    reviews = None
                
                tags = [] 
                if post_soup.find('div', class_ = 'chips typ-14Medium')!=None:
                    for tag in post_soup.find_all('div', class_='chips typ-14Medium'):
                        tags.append(tag.text)
                    tags = ", ".join(tags)
                    # tags = ", ".join([i.text for i in post_soup.find('div', class_='company-info-tags')])
                else:
                    tags = None       


                if post_soup.find('span', class_ = 'followers typ-14Regular')!=None:
                    followers = post_soup.find('span', class_ = 'followers typ-14Regular').text
                else:
                    followers = 0

                Type = None
                yearFounded = None
                companySize = None
                website = None
                hqLocation = None
                
                if post_soup.find('tr', class_ = 'info-item')!=None:
                    for info in post_soup.find_all('tr', class_='info-item'):
                        if 'Type' in info.text:
                            Type = info.text.replace('Type:', '')
                        elif 'Founded' in info.text:
                            yearFounded = info.text.replace('Founded:', '')
                        elif 'Company Size' in info.text:
                            companySize = info.text.replace('Company Size:', '')
                        elif 'Website' in info.text:
                            website = info.text.replace('Website:', '')
                        elif 'Headquarters' in info.text:
                            hqLocation = info.text.replace('Headquarters:', '')
                    
                    # tags = ", ".join([i.text for i in post_soup.find('div', class_='company-info-tags')])
                else:
                    pass

                
                writer.writerow([ company_name, rating, reviews,followers, tags, Type, yearFounded, companySize, hqLocation, website, getCompanyType(target_company)])
                        
                count += 1
