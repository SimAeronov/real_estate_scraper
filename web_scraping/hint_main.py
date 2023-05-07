from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.chrome.options import Options

from bs4 import BeautifulSoup
from retry import retry

############## HERE DATA SCRAPING STARTS ##############

# Config Chrome Driver
def config_driver(chrome_driver_path):
    ser = Service(chrome_driver_path)

    options = Options()
    options.page_load_strategy = 'none'
    driver = webdriver.Chrome(service=ser, options=options)

    return driver

@retry(exceptions=IndexError, tries=5, delay=1)
def scrape_data_from_site(driver, link_to_site):
    """
    Provided with Chrome Driver and a Link to a website returns scraped data for that site

    :param driver: Chrome Driver
    :param link_to_site: String "Link-To-Site"
    :return: [Lists containing scraped data, Link to next site]
    """
    driver.get(link_to_site)

    # Wait until first html image has loaded and get all data before cookies overlay. 3 works best!
    WebDriverWait(driver, 5).until(expected_conditions.presence_of_element_located((By.TAG_NAME, "img")))
    html_text = driver.page_source

    # Load saved html into a new BeautifulSoup object and get all data separately
    soup = BeautifulSoup(html_text, "html.parser")

    List_of_titles = soup.find_all(name="a", class_="lnk2")
    List_of_prices = soup.find_all(name="div", class_="price")

    # Organize Data and save to dict "List_collected_info"
    List_collected_info = []
    for element_titles_index in range(len(List_of_prices)):
        List_collected_info.append({"location": List_of_titles[element_titles_index].text,
                                    "price": List_of_prices[element_titles_index].text.replace(" EUR ", "").replace(" ",
                                                                                                                    ""),
                                    "link": List_of_titles[element_titles_index]["href"].replace("//", ""),
                                    "info": List_of_prices[element_titles_index].parent.parent.parent.find_all(
                                        name='tr')[3].text})

    # Find max number of pages and edit link +1 page until page = maxPage
    List_of_pages = soup.find_all(name="a", class_="pageNumbers")

    # Next I get the current page number, compare it to the current max number of pages.
    # If Current page < Max page, page += 1, else break
    index_page_substring = link_to_site.rfind("=")
    current_page_number = int(link_to_site[index_page_substring + 1:])

    if List_of_pages[-1].text == "Напред":
        max_page_number = int(List_of_pages[-2].text)
    elif List_of_pages[-1].text == "Назад":
        return List_collected_info, link_to_site
    else:
        max_page_number = int(List_of_pages[-1].text)

    if current_page_number <= max_page_number + 1:
        link_to_site = link_to_site[:index_page_substring + 1] + str(current_page_number + 1)
    print(f"current = {current_page_number}, max = {max_page_number}")
    # Note! There is another RETURN statement above for when I reach the real end of the pages "Напред" turns to "Назад"
    return List_collected_info, link_to_site


# HERE DATA SCRAPING ENDS, COULD ADD SORTING HERE

# Sorting was done in a different file, I might combine it

# WORK ON INPUTING DATA TO GOOGLE FORM NOW

def insert_form_data(chrome_driver_path, List_collected_info):
    ser = Service(chrome_driver_path)
    link_to_form = "https://docs.google.com/forms/d/e/1FAIpQLScPJTamqS0mkowc5KaAaIFqPwlNtKf4apK6hRH-eQ31T" \
                   "_fydw/viewform?usp=sf_link"

    op = webdriver.ChromeOptions().experimental_options
    driver = webdriver.Chrome(service=ser, options=op)
    driver.get(link_to_form)

    # Enter data "Location, Price, Link" inside Google Form [text boxes] which were found by their type of "text"
    current_data_number_count = 1  # Can remove this, used only for visualization
    for element_collected_data in List_collected_info:

        # Here I first wait a bit for the page to load (sometimes it crashes when it takes more time to load as active)
        WebDriverWait(driver, 10).until(
            expected_conditions.presence_of_element_located((By.XPATH, "//input[@type='text']")))
        driver.implicitly_wait(3)
        List_of_inputs = driver.find_elements(By.XPATH, "//input[@type='text']")
        List_of_inputs[0].send_keys(element_collected_data["location"])
        List_of_inputs[1].send_keys(element_collected_data["price"])
        List_of_inputs[2].send_keys(element_collected_data["link"])
        List_of_inputs[3].send_keys(element_collected_data["info"])

        # First I click on "Submit Answer" then I click on "Submit new Answer"
        WebDriverWait(driver, 10).until(expected_conditions.visibility_of_element_located((By.XPATH,
                                                                                           "//*[text()='Изпращане']"))).click()
        # Here I first wait a bit for the page to load (sometimes it crashes when it takes more time to load)
        driver.implicitly_wait(1)
        WebDriverWait(driver, 10).until(
            expected_conditions.visibility_of_element_located((By.XPATH, "//*[text()='Изпращане на "
                                                                         "друг отговор']"))).click()
        if current_data_number_count % 50 == 0:
            print(f"Current data entry: {current_data_number_count}")
        current_data_number_count += 1


def iterate_collect_data_from_site(chrome_driver_path, link_to_site):
    """
    Iterate every page of the provided website, collect data for every page, return that data

    :param chrome_driver_path: String "Path-To-Chrome-Driver
    :param link_to_site:  String "Link-To-Site"
    :return: List of Pandas.Dataframes of collected data
    """
    List_collected_info = []
    driver = config_driver(chrome_driver_path)
    while True:

        List_collected_info_new, link_to_site_new = scrape_data_from_site(driver, link_to_site)
        if link_to_site_new == link_to_site:
            print(f"Breking for {link_to_site_new} == {link_to_site}")
            driver.close()
            break
        print(f"New Page Available {link_to_site_new}")
        print(f"Numb of collected articles {len(List_collected_info_new)}")
        max_numb_of_reiteration = 0
        while len(List_collected_info_new) == 0 or max_numb_of_reiteration > 5:
            max_numb_of_reiteration += 1
            print("Warning, Web Page is being reiterated")
            List_collected_info_new, link_to_site_new = scrape_data_from_site(driver, link_to_site)
            print(f"Numb of collected articles {len(List_collected_info_new)}")
        link_to_site = link_to_site_new
        List_collected_info.extend(List_collected_info_new)
        print(f"Size of Data is: {len(List_collected_info)} \n")
    return List_collected_info


# This function is already too complex for what it is doing. I won't be using it too often but it is good to have it
def save_or_Load_html_data(path_to_file, data_to_save="None"):
    """
    Provide path to a .txt file, if second argument is provided as List of Pandas.Dataframe containing data, that data
    will be saved to the .txt file. If NOT second argument is provided the function will RETURN Pandas.Dataframe
    containing data stored inside that .txt file

    :param path_to_file: String "Link-To-Site"
    :param data_to_save: Nothing or List of Pandas.Dataframe containing data
    :return: List of Pandas.Dataframe containing data or Nothing
    """

    if data_to_save == "None":
        data_to_save = []
        with open(path_to_file, 'r', encoding="utf-8") as file_of_collected_data:
            try:
                # Split each line into key:value pair, split each pair into key and value, cleanup data, return List
                for line_of_collected_data in file_of_collected_data:
                    # Note [start:end] Might need to be edited for different data, no need to make it more complex
                    data_read_from_file = line_of_collected_data[1:-7]
                    if "\"" in data_read_from_file:
                        data_read_from_file = data_read_from_file.replace("\"", "\'")
                    data_read_from_file = data_read_from_file.split(r"', '")
                    read_data_dict = {}
                    for data_pair in data_read_from_file:
                        (data_key, data_value) = data_pair.split(r"': '")
                        if r'\n\n' in data_value:
                            data_value = data_value.replace(r"\n\n", "")
                        read_data_dict[data_key.replace("'", "")] = data_value.replace("'", "")
                    # add current item to the list
                    data_to_save.append(read_data_dict)
            except ValueError:
                print("Error while reading from file, Make sure you have replaced \" with \' and the start-end of "
                      "string [line_of_collected_data] is correct")
        print(f"Data was read from {path_to_file} with length of: {len(data_to_save)}")
        return data_to_save
    else:
        with open(path_to_file, 'w', encoding="utf-8") as file_of_collected_data:
            for line_of_collected_data in data_to_save:
                # write each item on a new line
                file_of_collected_data.write("%s\n" % line_of_collected_data)
            print(f"Data was saved to {path_to_file}")


# Execute code from here
path_chrome_driver = r"..\ChromeDriver\chromedriver.exe"
# Link for Houses in Gabrovo Municipality: https://www.imot.bg/pcgi/imot.cgi?act=3&slink=8l6t0f&f1=1
site_Link = r"https://www.imot.bg/pcgi/imot.cgi?act=3&slink=94h5jq&f1=1"


# retrieve data from each page of the provided link. If return of new link == old link, end of site reached
List_collected_data = iterate_collect_data_from_site(path_chrome_driver, site_Link)

# Load or Save data to .txt file
# Don't forget to replace " -> ' in .txt file and check start-end of [line_of_collected_data]
# Save
save_or_Load_html_data("Backup_html_data.txt", List_collected_data)
# Load
# List_collected_data = save_or_Load_html_data("Backup_html_data.txt")

# Load Google Forms and input all collected data
insert_form_data(path_chrome_driver, List_collected_data)
