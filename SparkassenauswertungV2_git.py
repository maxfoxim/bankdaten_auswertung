import json
import matplotlib.pyplot as plt
import pandas as pd

### Comdirect

finanzen_com=pd.read_csv("umsaetze.csv",  encoding = "unicode_escape",sep=";",quotechar='"',on_bad_lines='skip')

zweck=[]
absender=[]
for text in finanzen_com["Buchungstext"]:
     text=str(text)
     if text.find("Auftraggeber:")!=-1:
          zwi=text.replace("Auftraggeber:","")
          werte=zwi.split("Buchungstext:")
          zweck.append(werte[0])
          absender.append(werte[1])
     elif text.find("Empf�nger:")!=-1:
          zwi=text.replace("Empf�nger:","")          
          werte=zwi.split("Buchungstext:")
          zweck.append(werte[0])
          absender.append(werte[1])
     else:
          zweck.append("-")
          absender.append("-")


finanzen_com["Buchungstag"]=finanzen_com["Buchungstag"]
finanzen_com["Verwendungszweck"]=zweck
finanzen_com["Beguenstigter/Zahlungspflichtiger"]=absender
finanzen_com['Betrag']=[str(i).replace(".","") for i in finanzen_com['Umsatz in EUR']]
finanzen_com['Betrag']=[-1*(float(i.replace(",","."))) for i in finanzen_com['Betrag']]
finanzen_com=finanzen_com[finanzen_com['Betrag'] > 0]
print("COMDIRECT")
print(finanzen_com)



### Sparkasse
finanzen=pd.read_csv("20240424-umsatz-camt52v8.CSV",  encoding = "unicode_escape",sep=";",quotechar='"',on_bad_lines='skip')
finanzen.fillna("Nicht_Bestimmt")
finanzen['Betrag']=[-1*(float(i.replace(",","."))) for i in finanzen['Betrag']]
finanzen=finanzen[finanzen['Betrag'] > 0]


print("--------------------------------")
print("Sparkasse")
print(finanzen)


### Merge beider Konten
finanzen=finanzen.append(finanzen_com,ignore_index = True)
print("--------------------------------")
print("MERGE")
print(finanzen)

finanzen.to_csv('Merge_Pandas.csv', index=False) 

with open("Kategorien.json", "r") as read_file:
    Kategorien = json.load(read_file)

#Kategorien festlegen:
Kategorien_Neu=[]
index=1
doppelt=0
for zweck,sender,betrag in zip(finanzen["Verwendungszweck"],finanzen["Beguenstigter/Zahlungspflichtiger"],finanzen["Betrag"]):
     doppelt=0
     Nicht_gefunden=True
     for Kategorie in Kategorien:
          for werte in Kategorien[Kategorie]:
               sender=str(sender)
               if (zweck.find(werte)!=-1) or (sender.find(werte)!=-1) :
                    #print(index, Kategorie,"----Werte:",werte,"----Zweck:",zweck, "----Sender",sender)
                    index=index+1
                    Kategorien_Neu.append(Kategorie)
                    Nicht_gefunden=False
               
                    doppelt=doppelt+1
     #print("--------")
     if doppelt>1:
          print(doppelt,"zweck,sender",zweck,sender,Nicht_gefunden)
     if Nicht_gefunden:
          Kategorien_Neu.append("Sonstiges")
          print("Sonstiges: ",betrag,zweck,sender)

finanzen["Kategorien"]=Kategorien_Neu
plotfinanz=finanzen.groupby(['Kategorien']).sum()#.plot(kind='pie', y='Betrag',autopct='%1.0f%%')
plotfinanz_avg=finanzen.groupby(['Kategorien']).mean()#.plot(kind='pie', y='Betrag',autopct='%1.0f%%')
plotfinanz_max=finanzen.groupby(['Kategorien']).max()#.plot(kind='pie', y='Betrag',autopct='%1.0f%%')

plotfinanz["Betrag_Max"]=plotfinanz_max["Betrag"]
plotfinanz["Betrag_Avg"]=plotfinanz_avg["Betrag"]
Kategorien_Sortiert=finanzen['Kategorien'].unique()
Kategorien_Sortiert=sorted(Kategorien_Sortiert)
print("Kategorien")
plotfinanz["Kategorien"]=Kategorien_Sortiert
plotfinanz.sort_values(by="Betrag", inplace=True,ascending=False)  
print(plotfinanz)

plt.rc('axes', axisbelow=True)
#################

plt.subplots(figsize=(15, 8))
plt.grid()
index=0
text_index=0
for Kategorie,ywert,max,avg in zip(plotfinanz["Kategorien"],plotfinanz["Betrag"],plotfinanz["Betrag_Max"],plotfinanz["Betrag_Avg"]):
     plt.text(text_index-0.3,ywert+500,"Gesamt:"+str(round(ywert))+" Pro Monat:"+str(round(ywert/12)),rotation=90,verticalalignment="bottom",horizontalalignment="center")
     plt.text(text_index    ,ywert+500,"Max: "    +str(round(max)),rotation=90,verticalalignment="bottom",horizontalalignment="center")
     plt.text(text_index+0.3,ywert+500,"Mittel: " +str(round(avg)),rotation=90,verticalalignment="bottom",horizontalalignment="center")
     bottom=0
     #print("Kategorie:",Kategorie,"------------------")
     #print(finanzen[finanzen["Kategorien"] == Kategorie])
     text_index=text_index+1
     Filter=finanzen[finanzen["Kategorien"] == Kategorie]
     #print(Filter["Betrag"])
     index=0
     for Eintrag in Filter["Betrag"]:
          plt.bar(Kategorie, Eintrag,bottom=bottom)
          bottom=bottom+Eintrag
          index=index+1
     
plt.legend('', frameon=False)
plt.xticks(rotation=90)
plt.subplots_adjust(bottom=0.2,left=0.05,right=0.95)
plt.savefig("Ausgabe.png")
plt.show()