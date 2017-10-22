# -*- coding: utf-8 -*-
"""
Created on Sat Sep 23 20:38:49 2017

@author: Hao Yuan hyuan95@outlook.com
"""

import bs4 as bs
import urllib3
import certifi
import pyexcel
import time

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
        self.companyList.append(Company)

    def getCompanyNames(self):
        l = []
        if (len(self.companyList) != 0):
            for company in self.companyList:
                l.append(company.name)
        return l
    
    def getCompany(self, name):
        ind = self.getCompanyNames().index(name)
        return self.companyList[ind]



    def merged(self,interestedPositions):
        table = []
        headers = ["CompanyName", "H1BTotalFiled", "City", "State"]
        for intpos in interestedPositions:
                headers.append("{}Filed".format(intpos))
        for company in self.companyList:
            record = []
            h1btotalfiled = 0
            record.append(company.name)
            record.append(company.city)
            record.append(company.state)
            for intpos in interestedPositions:
                if (intpos != ""):
                    if (intpos in company.jobtitle_totalfiled_dict.keys()):
                        record.append(company.jobtitle_totalfiled_dict[intpos])
                        h1btotalfiled += int(company.jobtitle_totalfiled_dict[intpos])
                    else:
                        record.append(0)

            record.insert(1, str(h1btotalfiled))
            table.append(record)
        table.insert(0,headers)
        return table
    
def Main():
    http = urllib3.PoolManager(cert_reqs = 'CERT_REQUIRED', 
                           ca_certs = certifi.where())
    finished = False
    interestedPositions = []
    years = ["2013", "2014", "2015", "2016", "2016"]
    filename = "H1bCompanyScreening.xls"
    contents = {}

    while not finished:
        intpos = input("Please input your interested position and hit enter. One position per line.Replace white space with -\n")
        if (" " in intpos):
            print("Invalid inputs, please replace white space with - \n")
        else:
            interestedPositions.append(intpos)
        if ((intpos) == ''):
            break

    for year in years:
        yearshort = int(year) - 2000
        db = H1bCompanyDatabase(year)
        for intpos in interestedPositions:
            time.sleep(2)
            url = 'https://redbus2us.com/h1b-visa-sponsors/index.php?searchText=&searchCity=&searchYear={}&action=search&searchJobTitle={}'.format(int(yearshort), intpos)
            original = http.request('Get', url)
            soup = bs.BeautifulSoup(original.data, 'lxml')
            table = soup.find('table')
            names = {}
            if (table != None):
                table_rows = table.find_all('tr')
                table_rows.pop(0)
                for tr in table_rows:
                    td = tr.find_all('td')
                    row = [i.text for i in td]
                    name = row[0]
                    count = row[1]
                    city = row[2]
                    state = row[3]
                    if (name not in db.getCompanyNames()):
                        company = Company(name,city,state)
                        company.addJobTitleTotalFiled(intpos,count)
                        db.addCompany(company)
                    else:
                        db.getCompany(name).addJobTitleTotalFiled(intpos,count)
        mergedtable = db.merged(interestedPositions)
        contents[year] = mergedtable
    book = pyexcel.get_book(bookdict=contents)
    book.save_as(filename)

Main()