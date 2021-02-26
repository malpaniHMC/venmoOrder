from bs4 import BeautifulSoup
from indianFood import checkPayments
import requests

def scraper():
        link= "https://www.beyondmenu.com/31864/upland/ashirwad-the-blessings-upland-91786.aspx?utm_source=satellite&utm_medium=menu_group#group_1502050"
        page = requests.get(link)
        soup = BeautifulSoup(page.text, 'html.parser')
        menu = {"Menu":"Prices"}
        menu["box"]= 8
        menu["box with garlic naan"]=8
        menu["vegan box"]= 8
        for item in soup.find_all('a'): 
                if(len(item)!=0):
                        menuItems= item.find_all('h4')
                        menuPrice= item.find_all('td', class_="price")
                        if(len(menuItems)!=0):
                                menu[menuItems[0].get_text().lower()]=round((float(menuPrice[0].get_text().rstrip("+ ").lstrip("$"))*1.08*1.08),2)
        
        return menu