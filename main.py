import pandas as pd
from openpyxl import load_workbook

users_wb = load_workbook('data/TEST.xlsm')
ws = users_wb['BBDD']
users_db = pd.DataFrame(ws.values)


users_db.drop(list(range(0,3)),axis=0,inplace=True)
#users_db.set_index(0,inplace=True)
users_db.dropna(axis=1,inplace=True,how='all')
users_db.dropna(axis=0,inplace=True,how='all')
users_db.reset_index(drop=True,inplace=True)
users_db.columns = users_db.iloc[0]
users_db = users_db[1:]
#users_db.set_index(0,inplace=True)

#users_db.drop([0],axis=1,inplace=True)
#users_db = pd.read_excel('data/TEST.xlsm',sheet_name='BBDD',header=3,index_col=2)
print(users_db)
print(users_db.info())
