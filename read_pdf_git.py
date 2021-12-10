#heaclear
from os import sep
import pandas as pd
import matplotlib.pyplot as plt
from openpyxl.workbook import Workbook
from datetime import datetime, date
import errno
import PyPDF2
import re

# initialiation
transfers = []
match = []

datapath = "Dir of the pdf"

try:
    with open(datapath, "rb") as pdf:
        file = PyPDF2.PdfFileReader(pdf)
        nb_pages = file.getNumPages()
        
        for page in range(0,nb_pages):
            pageObj = file.getPage(page)
            page = file.getPageLayout()
            dirtyline = pageObj.extractText()

            regex = r'(Lastschrift|Dauerauftrag|Ueberweisung|Gutschrift/Dauerauftrag)(.+?)(-*\d+,\d{2}|-*\d{0,1}\.*\d{3},\d{2})(\d{2}\.\d{2}\.\d{4})+'
            matches = re.findall(regex,dirtyline)
            
            for match in matches:
                cats  = ["art", "anlass", "betrag", "datum"]
                dictoflist = dict(zip(cats ,match))
                transfers.append(dictoflist)
                  
except IOError as exc:
    if exc.errno != errno.EISDIR: # Do not fail if a directory is found, just ignore it.
        raise # Propagate other kinds of IOError.
 
# work on the read data
df = pd.DataFrame(transfers)

df["datum"] = pd.to_datetime(df["datum"],format="%d.%m.%Y")
df["datum"]=df['datum'].dt.date

df["art"] = df["art"].astype('category')
df["anlass"] = df["anlass"].astype('string')


df["betrag"] = df["betrag"].str.replace(".","")
df["betrag"] = df["betrag"].str.replace(",",".")
df["betrag"] = df["betrag"].astype('float')

month_first = df.loc[1,"datum"].month
month_last = df.loc[len(df.datum)-1,"datum"].month

# visualise the data
df_grouped = df.groupby("anlass").sum()
print(df_grouped)

df.plot("datum","betrag", kind="line")
plt.subplots_adjust(bottom=0.2)
plt.xticks(rotation = -45)
plt.autoscale()

df_grouped.plot(kind="bar", align="center")
plt.subplots_adjust(bottom=0.5)
plt.autoscale()
plt.show()
