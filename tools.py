from crewai import Tool
import os
import shutil
import requests
import subprocess
from googleapiclient.discovery import build
from msal import ConfidentialClientApplication
import googlemaps
import yfinance as yf
from alpha_vantage.timeseries import TimeSeries
import finnhub
from pyicloud import PyiCloudService
from caldav import DAVClient
import imaplib
import smtplib
from email.mime.text import MIMEText
import openpyxl
import pandas as pd
from sqlalchemy import create_engine
import icalendar

class AgentTools:
    def __init__(self, config, keyring):
        self.config = config
        self.keyring = keyring

    def get_all_tools(self):
        return [
            Tool(name='File Organizer', func=self.file_organize, description='Organize files'),
            Tool(name='Web Research', func=self.web_research, description='Search web'),
            Tool(name='Calendar Manager', func=self.calendar_manage, description='Manage calendar'),
            Tool(name='Email Manager', func=self.email_manage, description='Manage email'),
            Tool(name='Financial Data', func=self.financial_data, description='Get financial info'),
            Tool(name='Document Handler', func=self.document_handle, description='Handle documents')
        ]

    def file_organize(self, path, criteria):
        # Example
        os.makedirs(os.path.join(path, 'organized'), exist_ok=True)
        for file in os.listdir(path):
            if criteria in file:
                shutil.move(os.path.join(path, file), os.path.join(path, 'organized', file))
        return 'Organized'

    def web_research(self, query):
        response = requests.get(f'https://www.google.com/search?q={query}')
        return response.text[:1000]  # Truncated

    def calendar_manage(self, action, details):
        mode = self.config['calendar_mode']
        if mode == 'local':
            subprocess.run(['osascript', '-e', f'tell application "Calendar" to make new event with properties {{summary:"{details["summary"]}"}} at calendar "Calendar"'])
            return 'Local event added'
        # Add other modes as in plan; abbreviated
        return 'Event managed'

    def email_manage(self, action, details):
        mode = self.config['email_mode']
        if mode == 'local':
            subprocess.run(['osascript', '-e', f'tell application "Mail" to make new outgoing message with properties {{subject:"{details["subject"]}", content:"{details["body"]}"}}'])
            return 'Local email drafted'
        # Add other modes
        return 'Email managed'

    def financial_data(self, symbol, period='real-time'):
        api = self.config['financial_api']
        if api == 'yfinance':
            ticker = yf.Ticker(symbol)
            if period != 'real-time':
                return ticker.history(period=period).to_dict()
            return ticker.info
        # Add Alpha/Finnhub
        return 'Data fetched'

    def document_handle(self, type, data):
        if type == 'spreadsheet':
            wb = openpyxl.Workbook()
            ws = wb.active
            for row in data:
                ws.append(row)
            wb.save('doc.xlsx')
            return 'Spreadsheet created'
        if type == 'database':
            engine = create_engine('sqlite:///doc.db')
            pd.DataFrame(data).to_sql('table', engine, if_exists='replace')
            return 'Database created'