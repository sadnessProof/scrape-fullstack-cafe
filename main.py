# imports
import os
import time
import json
import shutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC


# constants
FULL_STACK_CAFFEE_LINK = 'https://www.fullstack.cafe/'
DATA_FOLDER = './Data'
TOPIC_XPATH = '//*[@id="root"]/div/div[5]/div[2]/div/div/div/div'
SECTION_XPATH = '//*[@id="root"]/div/div[5]/div[2]/div/div/nav[1]/div/div/div/button'
TOPIC_CSS_SELECTOR = 'div.p-2.topic-questions-spacer'
QUESTION_CSS_SELECTOR = 'div.my-1.px-2.py-2.rounded.hovered'
ANSWER_TAG_CSS_SELECTOR = 'div.d-block.px-2'


def wait_by_xpath(browser, xpath):
    """
    waits until a node, xpath points to, is loaded.
    if waiting time exceeds 30 seconds, then prints:
    "failed to load a node with this {xpath}"
    :param browser:
    :param xpath:
    :return:
    """
    try:
        WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.XPATH, xpath)))
    except TimeoutException:
        print(f'failed to load a node with this {xpath}')


def wait_by_css_selector(browser, css_selector):
    """
    waits until at least one node, css_selector points to, is loaded.
    if waiting time exceeds 30 seconds, then prints:
    "failed to load a node with this {css_selector}"
    :param browser:
    :param css_selector:
    :return:
    """
    try:
        WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, css_selector)))
    except TimeoutException:
        print(f'failed to load a node with this {css_selector}')


def wait_by_class_name(browser, class_name):
    """
    waits until at least one node, class_name points to, is loaded.
    if waiting time exceeds 30 seconds, then prints:
    "failed to load a node with this {class_name}"
    :param browser:
    :param css_selector:
    :return:
    """
    try:
        WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CLASS_NAME, class_name)))
    except TimeoutException:
        print(f'failed to load a node with this {class_name}')


def clear_directory(directory_address):
    """
    cleans directory on passed address
    :param directory_address:
    :return:
    """
    for file_name in os.listdir(directory_address):
        file_path = os.path.join(directory_address, file_name)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def setup_environment(dest_path):
    """
    cleans the directory if it exists on the passed address.
    if not creates new one.
    :param directory_address:
    :return:
    """
    if not os.path.exists(dest_path):
        os.mkdir(dest_path)
    else:
        clear_directory(dest_path)


def login():
    """
    opens google dialog to verify you identity.
    since the site we are scrapint uses google authentication,
    we have to log into the site manually, because
    automating log in via google authentication is quite a big headache.
    :param directory_address:
    :return:
    """
    browser = webdriver.Edge(os.getcwd() + '\\' + 'msedgedriver.exe')
    
    # get to the fullctack.cafe's home page
    browser.get(FULL_STACK_CAFFEE_LINK)
    time.sleep(40) # 40 secs to log in
    return browser


def section_topic_links(browser):
    """
    if section links are loaded on the site, this method
    extracts all the topic links and returns as a list.
    this way is much easier and faster for me.
    :param directory_address:
    :return topic_links:
    """
    topic_links = []
    wait_by_xpath(browser, TOPIC_XPATH)
    for topic in browser.find_elements_by_xpath(TOPIC_XPATH):
        topic_links.append(topic.find_element_by_xpath('./a[1]').get_attribute('href'))
    
    return topic_links

        
def get_section_elements(browser):
    """
    I was needed to find an element by xpath planty of times.
    I created a new method that contains not only the wait part,
    but an extraction part as well.
    :param directory_address:
    :return:
    """
    wait_by_xpath(browser, SECTION_XPATH)
    return browser.find_elements_by_xpath(SECTION_XPATH)


def scrape_question(browser, q, is_challenge, a_json, q_json):
    global question_enumeration
    if 'Mid' in q.text:
        q_diff = 3
    if 'Entry' in q.text:
        q_diff = 1
    if 'Junior' in q.text:
        q_diff = 2
    if 'Senior' in q.text:
        q_diff = 4
    if 'Expert' in q.text:
        q_diff = 5

    q.find_element_by_xpath('./div/div/div[1]/span').click()
    q_text = q.find_element_by_xpath('./div/div/div[1]/h2').text

    q_json.append({
        'id': question_enumeration,
        'difficulty': q_diff,
        'title': q_text,
        'isChallenge': is_challenge
    })

    wait_by_css_selector(browser,ANSWER_TAG_CSS_SELECTOR)
    a_content = browser.find_element_by_css_selector(ANSWER_TAG_CSS_SELECTOR).get_attribute('innerHTML')

    a_json.append({
        'id': question_enumeration,
        'content': a_content,
        'slug': q_text
    })

    question_enumeration += 1
    q.find_element_by_xpath('./div/div/div[1]/span').click()


# Function to remove spaces  
# and convert into camel case 
def convert(s): 
    if(len(s) == 0): 
        return
    s1 = '' 
    s1 += s[0].upper() 
    for i in range(1, len(s)): 
        if (s[i] == ' '): 
            s1 += s[i + 1].upper() 
            i += 1
        elif(s[i - 1] != ' '): 
            s1 += s[i]  
    return s1


def scrape_section(browser, section_name, topic_links):
    section_name = str(section_name).strip()
    section_folder = DATA_FOLDER+'/'+section_name
    os.mkdir(section_folder)
    # get all of the question for each topic
    for link in topic_links:
        browser.get(link)
        topic_name = link.split('/')[-1]
        
        answers_json = []
        questions_json = []

        wait_by_css_selector(browser, TOPIC_CSS_SELECTOR)
        topic_questions = browser.find_element_by_css_selector(TOPIC_CSS_SELECTOR).find_elements_by_xpath('./div')
        
        is_challenge = 0
        for question in topic_questions:

            if question.get_attribute('class') == 'my-2':
                is_challenge += 1
                pass

            wait_by_css_selector(browser, QUESTION_CSS_SELECTOR)
            if len(question.find_elements_by_css_selector(QUESTION_CSS_SELECTOR)):
                scrape_question(browser, question, is_challenge==2, answers_json, questions_json)
        
        topic_name = convert(topic_name.replace('-',' '))

        with open(f'{section_folder}/{topic_name}Answers.json', 'w') as outfile:
            json.dump(answers_json, outfile)
        
        with open(f'{section_folder}/{topic_name}Questions.json', 'w') as outfile:
            json.dump(questions_json, outfile)


def scrape_the_site(browser):
    section_names = []
    topic_links = []
    
    for section in get_section_elements(browser):
        section.click()
        section_names.append(section.text)
        topic_links.append(section_topic_links(browser))
        
    
    for i in range(0, len(section_names)):
        scrape_section(browser, section_names[i], topic_links[i])
        
    
def main():
    setup_environment(DATA_FOLDER)
    # get to the fullctack.cafe's home page
    browser = login()
    browser.get(FULL_STACK_CAFFEE_LINK)
    scrape_the_site(browser)
    browser.quit()

question_enumeration = 0
main()
