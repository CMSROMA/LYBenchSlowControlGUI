from optparse import OptionParser
parser = OptionParser()
parser.add_option("-d","--days")
parser.add_option("-s","--start")
parser.add_option("-e","--end")
parser.add_option("-o","--output")
(options,args)=parser.parse_args()

import urllib, json
if (options.start is None or options.end is None):
    url = 'https://thingspeak.com/channels/1083264/feed.json?days='+options.days
else:
    url = 'https://thingspeak.com/channels/1083264/feed.json?start='+options.start+'&'+'end='+options.end

response = urllib.urlopen(url)
data = json.loads(response.read())

import pandas as pd
df = pd.DataFrame.from_dict(data['feeds'])

#print df.tail(5)

#manipulate DataFrame
df['time']=pd.to_datetime(df['created_at'])
df['tbench'] = df['field1'].astype(float)
df['hbench'] = df['field3'].astype(float)
df['tlab'] = df['field2'].astype(float)

df.set_index('time', inplace=True) #set the index to the date column

#convert time to Rome timezone
#df.index=df.index.tz_localize('GMT')
#df.index=df.index.tz_convert('Europe/Rome')

#select only meaningful data
df=df[df.index >= '2020-06-17']

#convert date to epoch
df['timestamp']=df.index.astype('int64')/1000000000

#removes unnecessary colums
df=df.loc[:,'tbench':'timestamp']

print df.head(5)
print "......."
print df.tail(5)

from root_pandas import to_root
to_root(df,options.output, key='LYBenchTemp')
