# -*- coding:utf-8 -*-
'''
Created on 2016.04.28

@author: davidpower
'''
import gspread
from oauth2client.service_account import ServiceAccountCredentials

class MGoogle(object):

	def __init__(self):
		
		json_key = 'C:/mgspread-426ba69cc685.json'
		scope = ['https://spreadsheets.google.com/feeds']

		credentials = ServiceAccountCredentials.from_json_keyfile_name(json_key, scope)

		self.gc = gspread.authorize(credentials)



sh = gc.open('mayaOil_test')
