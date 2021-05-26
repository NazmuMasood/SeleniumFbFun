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
driver = webdriver.Chrome(options=option, executable_path='../chromedriver.exe')

#Loading the webpage
driver.get("https://www.facebook.com/stories/create/")
print(driver.title)

#Getting the login fields
email = driver.find_element_by_name("email")
password = driver.find_element_by_name("pass")
loginButton = driver.find_element_by_name("login")

#Initializing password from ciphered-hash
fpath = "info.txt"
if (os.path.isfile(fpath) and os.path.getsize(fpath)>0):
    file = open(fpath)
    infos = []
    for line in file:
        line = line.strip()
        infos.append(line)
    emailAddress = infos[0]    
    key = infos[1]
    cipherstring = infos[2]
    cipher2 = AES.new(key.encode('utf-8'), AES.MODE_CBC, 'This is an IV456'.encode('utf-8'))
    text = bytes.fromhex(cipherstring)
    original_pass = cipher2.decrypt(text).decode().lstrip()
else:
    emailAddress = input('Enter email address or phone number: \n')
    original_pass = input('Enter password: \n')

#Filling the login fields
email.send_keys(emailAddress)
password.send_keys(original_pass)
loginButton.click()

try:
    settingsButtonLabel = "//div[@aria-label='settings']"
    settingsButton = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, settingsButtonLabel)))
    print("Settings button found!")
    settingsButton.click()

    try:
        customRadioClassName = "//*[text()='Custom']"
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, customRadioClassName))).click()
        print("'Custom' radio button found!")

        try:
            #Useful method for checking if certain text exists in the webpage
            def is_text_element_exist(text):
                try:
                    changeToDiffMode = "//*[text()='{0}']".format(text)
                    WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, changeToDiffMode)))
                    return True
                except TimeoutException:
                    return False
            
            if is_text_element_exist('Change story privacy'):
                print('clicking change button')
                changeButtonLabel = "//div[@aria-label='Change']"
                driver.find_element_by_xpath(changeButtonLabel).click()

            try:
                selectPeopleText = "//*[text()='Select people']"
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, selectPeopleText)))
                print("'Select people' found!")

                try:
                    radioButtonClass = "//span[@class='d2edcug0 hpfvmrgz qv66sw1b c1et5uql rrkovp55 a8c37x1j keod5gw0 nxhoafnm aigsh9s9 d3f4x2em fe6kdd0r mau55g9w c8b282yb iv3no6db jq4qci2q a3bd9o3v ekzkrbhg oo9gr5id hzawbc8m']"
                    radios = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, radioButtonClass))) 
                    print("Friend list initially loaded! \n- "+str(len(radios))+" people")

                    # Finding the first 'friend name' on the list and clicking it
                    count = 0
                    firstFriendNameText = "//*[text()='{0}']".format(radios[count].text)
                    driver.find_element_by_xpath(firstFriendNameText).click()
                    dashes = " "
                    for i in range(len(radios[count].text), 30):
                        dashes+='-'
                    print(str(count)+'. '+radios[count].text+dashes+' deselected')

                    # Accessing the rest of the list by pressing 'TAB' and 'ENTER'
                    success = 'unsuccessful'
                    while True:
                        prevElemText = driver.switch_to.active_element.find_element_by_tag_name('span').text
                        # print('prevElem: '+prevElemText)
                        ActionChains(driver).send_keys(Keys.TAB).perform()
                        activeElem = driver.switch_to.active_element
                        count+=1

                        def is_span_element_exist(activeElem):
                            try:
                                activeElem.find_element_by_tag_name('span')
                                return True
                            except NoSuchElementException:
                                return False

                        if (is_span_element_exist(activeElem)):
                            span = activeElem.find_element_by_tag_name('span')
                            dashes = " "
                            for i in range(len(span.text), 30):
                                dashes+='-'
                            # print(str(count)+'. '+span.text if span.text!='Save' else span.text)
                            if activeElem.get_attribute('aria-checked')=='true':
                                ActionChains(driver).send_keys(Keys.ENTER).perform()
                                print(str(count)+'. '+span.text+dashes+' deselected')
                                continue
                            elif activeElem.get_attribute('aria-checked')=='false':
                                print(str(count)+'. '+span.text+dashes+' already deselected')
                                continue
                            elif activeElem.get_attribute('aria-label')=='Save':
                                # ActionChains(driver).send_keys(Keys.ENTER).perform()
                                success = 'successful'
                                print('Saved settings!')
                                break
                            else:
                                print('Error loading friend list')
                                break
                        else:
                            print('loading list...')
                            time.sleep(6)
                            prevFrndNameText = "//*[text()='{0}']".format(prevElemText)
                            e = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, prevFrndNameText)))
                            ActionChains(driver).move_to_element(e).click(e).click(e).perform()
                            currentElem = driver.switch_to.active_element.find_element_by_tag_name('span').text
                            print('previous element: '+currentElem)
                            count-=1

                    # for count, span in enumerate(radios):
                    #     print(str(count)+". '"+span.text+"'")
                    
                    #     friendNameText = "//*[text()='{0}']".format(span.text)
                    #     # e = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, friendNameText)))
                    #     # e.click()

                    #     # actions = ActionChains(driver)
                    #     # actions.move_to_element(element).perform()
                    #     # time.sleep(1)
                    #     # element.click()
                    #     # elem = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, friendNameText)))
                        

                    print("Task Finished - "+success)

                except TimeoutException:
                    print("Radio button list error!")  
            except TimeoutException:
                print("No 'Select people' found!")   
        except TimeoutException:
            print("No 'Change Button' found!")    
    except TimeoutException:
        print("No radio button named 'custom' found")    
except TimeoutException:
    print("No 'settings' button present on 'story' page")

# time.sleep(60)
# driver.quit()


    


