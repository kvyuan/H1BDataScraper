# -*- coding: utf-8 -*-
"""
Created on Sat Sep 23 20:38:49 2017

@author: haoy
"""

import pandas as pd
import bs4 as bs
import urllib3
import certifi
import xlsxwriter


#print(soup.title.string)
#print(soup.title.text)
#print(soup.find_all('p'))#paragraph tag
#for paragraph in soup.find_all('p'):
    #print(paragraph.string)
    #print(paragraph.text)
#print(soup.get_text()) #print all contents
#for url in soup.find_all('a'):
    #print(url)
    #print(url.get('href'))

#body = soup.body
#for paragraph in body.find_all('p'):
    #print(paragraph.text)

#for div in soup.find_all('div'):
 #   print(div.text)
 
#for div in soup.find_all('div', class_='body'):
     #print(div.text)

class Company:
    def __init__(self,name,city,state):
        self.name = name
        self.jobtitle_totalfiled_dict = {}
        self.city = city
        self.state = state
        
    def addJobTitleTotalFiled(self, jobTitle, quantity):
        if (jobTitle not in self.jobtitle_totalfiled_dict):
            self.jobtitle_totalfiled_dict[jobTitle] = quantity
        else:
            self.jobtitle_totalfiled_dict[jobTitle] += quantity


class H1bCompanyDatabase:
    def __init__(self,name):
        self.name = name
        self.companyList = []
        self.companyListSize = 0
    
    def addCompany(self, Company):
        self.companyList.add(Company)
    
    def getCompany(self, Company):
        return self.companyList[self.companyList.index(Company)]
    
    def merged(self,interestedPositions):
        table = []
        headers = ["CompanyName", "H1BTotalFiled", "City", "State"]
        record = []
        for company in self.companyList:
            h1btotalfiled = 0
            record.append(company.name)
            record.append(company.city)
            record.append(company.state)
            for intpos in interestedPositions:
                if (interestedPositions.index(company) == len(interestedPositions) - 1):
                    headers.append(intpos)
                    headers.append("{}Filed".format(intpos))
                record.append(intpos)
                record.append(company.jobtitle_totalfiled_dict[intpos])
                h1btotalfiled += int(company.jobtitle_totalfiled_dict[intpos])
            record.insert(1, str(h1btotalfiled))
        table.append(record)
        table.insert(0,headers)
        return table
    
def Main():
    http = urllib3.PoolManager(cert_reqs = 'CERT_REQUIRED', 
                           ca_certs = certifi.where())
    workbook = xlsxwriter.Workbook('H1BSponsorWorkbook.xlsx')
    

    finished = False
    interestedPositions = []
    years = []
    while not finished:
        intpos = input("Please input your interested position and hit enter. One position per line.Replace white space with -")
        if ((intpos) == ''):
            break
        interestedPositions.append(intpos)
    while not finished:
        year = input("Please input your interested year and hit enter. One position per line")
        if ((year) == ''):
            break
        years.append(year)
    for year in years:
        db = H1bCompanyDatabase(year)
        for intpos in interestedPositions: 
            url = 'https://redbus2us.com/h1b-visa-sponsors/index.php?searchText=&searchCity=&searchYear={}&action=search&searchJobTitle={}'.format(year, intpos)
            #url = 'https://redbus2us.com/h1b-visa-sponsors/cuna-mutual-group/16/search/?searchText=&searchCity=&searchYear={year}&action=search&searchJobTitle={intpos}'.format(year, intpos)
            original = http.request('Get', url)
            soup = bs.BeautifulSoup(original.data, 'lxml')
            table = soup.find('table')
            table_rows = table.find_all('tr')
            for tr in table_rows:
                td = tr.find_all('td')
                row = [i.text for i in td]
                name = row[0]
                count = row[1]
                city = row[2]
                state = row[3]
                if (interestedPositions.index(intpos) == 0):    
                    company = Company(name,city,state)
                    company.addJobTitleTotalFiled(intpos,count)
                else:
                    db.getCompany(name).addJobTitleTotalFiled(intpos,count)
        worksheet = workbook.add_worksheet(year)
        mergedtable = db.merged(interestedPositions)
        for row in mergedtable:
            worksheet.write_row(row)
                
                
                
            

Main()
    

        
    
    