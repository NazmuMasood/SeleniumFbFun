from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from Crypto.Cipher import AES
import os
import time

#Setting up options for the driver
option = Options()
option.add_argument("--disable-infobars")
option.add_argument("start-maximized")
option.add_argument("--disable-extensions")
option.add_experimental_option('excludeSwitches', ['enable-logging'])

# Pass the argument 1 to allow and 2 to block on the "Allow Notifications" pop-up
option.add_experimental_option("prefs", { 
    "profile.default_content_setting_values.notifications": 2 
})

#Creating the driver
driver = webdriver.Chrome(options=option, executable_path='chromedriver.exe')

#Loading the webpage
driver.get("https://www.facebook.com/stories/create/")
print('Webpage title: '+driver.title)

#Getting the login fields
email = driver.find_element_by_name("email")
password = driver.find_element_by_name("pass")
loginButton = driver.find_element_by_name("login")

#Preparing credentials
## !!! mention "login_info.txt" file below if you're logging in using saved credentials and encrypt.py !!! 
fpath = "login_info.txt" 
if (os.path.isfile(fpath) and os.path.getsize(fpath)>0):
    file = open(fpath)
    infos = []
    for line in file:
        line = line.strip()
        infos.append(line)
    emailAddress = infos[0]    
    key = infos[1]
    cipherstring = infos[2]
    goal = infos[3]
    cipher2 = AES.new(key.encode('utf-8'), AES.MODE_CBC, 'This is an IV456'.encode('utf-8'))
    text = bytes.fromhex(cipherstring)
    original_pass = cipher2.decrypt(text).decode().lstrip()
else:
    emailAddress = input('Enter email address or phone number: ')
    original_pass = input('Enter password: ')
    goal = ''
    while goal!='select' and goal!='unselect':
        goal = input('(select / unselect) all friends in the \'Custom\' settings?: ')
goalBool = True if goal=='select' else False

#Filling up the login fields
email.send_keys(emailAddress)
password.send_keys(original_pass)
loginButton.click()

try:
    # Navigating to the story 'Settings' button on the Create Facebook Stories page 
    settingsButtonLabel = "//div[@aria-label='settings']"
    settingsButton = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, settingsButtonLabel)))
    print("'Settings' button found!")
    settingsButton.click()

    try:
        customRadioClassName = "//*[text()='Custom']"
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, customRadioClassName))).click()
        print("'Custom' radio button found!")

        try:
            #Useful method for checking if certain text exists in the webpage
            def is_text_element_exist(text):
                try:
                    changeButtonLabel = "//div[@aria-label='{0}']".format(text)
                    WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, changeButtonLabel)))
                    return True
                except TimeoutException:
                    return False
            
            if is_text_element_exist('Select people'):
                print('Clicking \'Select people\' title')
                changeButtonLabel = "//div[@aria-label='Select people']"
                driver.find_element_by_xpath(changeButtonLabel).click()

            try:
                radioButtonClass = "//span[@class='d2edcug0 hpfvmrgz qv66sw1b c1et5uql lr9zc1uh a8c37x1j keod5gw0 nxhoafnm aigsh9s9 d3f4x2em fe6kdd0r mau55g9w c8b282yb iv3no6db jq4qci2q a3bd9o3v ekzkrbhg oo9gr5id hzawbc8m']"
                radios = WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located((By.XPATH, radioButtonClass))) 
                print("Friend list initially loaded! \n- "+str(len(radios))+" people")

                # Moving focus to the friend list from the search box
                ActionChains(driver).send_keys(Keys.TAB).perform()

                # Useful function for checking if an element has child element named 'span'
                def is_span_element_exist(elem):
                    try:
                        elem.find_element_by_tag_name('span')
                        return True
                    except NoSuchElementException:
                        return False

                # ~ ~ ~ Traversing each item in friends list and updating it by pressing 'TAB' and 'ENTER' repeatedly
                success = 'unsuccessful'
                count = 1 #len(radios)-1
                enterClicks = 0
                # firstFriendNameText = "//*[text()='{0}']".format(radios[count].text)
                # firstFriendElem = driver.find_element_by_xpath(firstFriendNameText)
                # ActionChains(driver).move_to_element(firstFriendElem).click().click().perform()
                while True:
                    currElem = driver.switch_to.active_element

                    # Current element is either 'friend list' item or 'save' button, so proceed to clicking protocols
                    span = currElem.find_element_by_tag_name('span')
                    dashes = " "
                    for i in range(len(span.text), 30):
                        dashes+='-'

                    if currElem.get_attribute('aria-checked')=='true': # Item is Selected 
                        if not goalBool: # User asked to unselect i.e. goalBool = false
                            ActionChains(driver).send_keys(Keys.ENTER).perform()
                            print(str(count)+'. '+span.text+dashes+' unselected')
                            enterClicks+=1
                        else:
                            print(str(count)+'. '+span.text+dashes+' already selected')

                    elif currElem.get_attribute('aria-checked')=='false': # Item is Unselected
                        if goalBool: # User asked to select i.e. goalBool = true
                            ActionChains(driver).send_keys(Keys.ENTER).perform()
                            print(str(count)+'. '+span.text+dashes+' selected')
                            enterClicks+=1
                        else:
                            print(str(count)+'. '+span.text+dashes+' already unselected')

                    elif currElem.get_attribute('aria-label')=='Save':
                        # ActionChains(driver).send_keys(Keys.ENTER).perform()
                        success = 'successful'
                        print('Can save settings!')
                        break

                    else:
                        print('Error loading friend list')
                        break
                    
                    ActionChains(driver).send_keys(Keys.TAB).perform()
                    count+=1
                    
                    # Next element is a 'loading section' item and doesn't have valid value, so go back so last 'friend list' item 
                    while not (is_span_element_exist(driver.switch_to.active_element)):
                        print('loading list...')
                        # print('previous element: '+currElem.find_element_by_tag_name('span').text)
                        prevFrndNameText = "//*[text()='{0}']".format(currElem.find_element_by_tag_name('span').text)
                        e = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, prevFrndNameText)))
                        ActionChains(driver).move_to_element(e).click(e).click(e).perform()
                        time.sleep(5)
                        ActionChains(driver).send_keys(Keys.TAB).perform()

                print('Updated '+str(enterClicks)+' contacts')
                print("Task Finished - "+success)

            except TimeoutException:
                print("Friend list loading error!")  
        except TimeoutException:
            print("No 'Change Button' found!")    
    except TimeoutException:
        print("No radio button named 'custom' found")    
except TimeoutException:
    print("No 'settings' button present on 'story' page")

# driver.quit()


    


