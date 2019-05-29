from optparse import OptionParser
parser = OptionParser()
parser.add_option("-d","--days")
parser.add_option("-o","--output")
(options,args)=parser.parse_args()

import urllib, json
url = 'https://thingspeak.com/channels/781520/feed.json?days='+options.days
response = urllib.urlopen(url)
data = json.loads(response.read())

import pandas as pd
df = pd.DataFrame.from_dict(data['feeds'])

#print df.tail(5)

#manipulate DataFrame
df['time']=pd.to_datetime(df['created_at'])
df['tbench'] = df['field1'].astype(float)
df['hbench'] = df['field2'].astype(float)
df['tchiller'] = df['field3'].astype(float)
df['chillerstatus'] = df['field4'].astype(float)
df['tlab'] = df['field5'].astype(float)
df['hlab'] = df['field6'].astype(float)

df.set_index('time', inplace=True) #set the index to the date column

#convert time to Rome timezone
#df.index=df.index.tz_localize('GMT')
#df.index=df.index.tz_convert('Europe/Rome')

#select only meaningful data
df=df[df.index >= '2019-05-21']

#convert date to epoch
df['timestamp']=df.index.astype('int64')/1000000000

#removes unnecessary colums
df=df.loc[:,'tbench':'timestamp']
print df.tail(5)

from root_pandas import to_root
to_root(df,options.output, key='LYBenchTemp')
