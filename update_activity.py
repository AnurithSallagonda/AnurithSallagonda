"""Render public GitHub activity only. Never reads private repository content."""
import json,re,sys,urllib.request,datetime,calendar
from pathlib import Path
from html.parser import HTMLParser
ROOT=Path(__file__).parent
class Contributions(HTMLParser):
 def __init__(self):super().__init__();self.days={};self.target=None
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if a.get('data-date'):self.days[a.get('id')]={'date':a['data-date'],'level':int(a.get('data-level','0')),'count':0}
  if tag=='tool-tip':self.target=a.get('for')
 def handle_data(self,text):
  if self.target in self.days:
   m=re.search(r'([\d,]+) contribution',text)
   if m:self.days[self.target]['count']=int(m[1].replace(',',''))
 def handle_endtag(self,tag):
  if tag=='tool-tip':self.target=None
if '--refresh' in sys.argv:
 request=urllib.request.Request('https://github.com/users/AnurithSallagonda/contributions',headers={'User-Agent':'Anurith-profile-activity'})
 parser=Contributions();parser.feed(urllib.request.urlopen(request,timeout=45).read().decode())
 days=list(parser.days.values())
 if len(days)<300:raise RuntimeError('Incomplete public contribution response; existing cards preserved.')
 (ROOT/'activity.json').write_text(json.dumps(days),encoding='utf-8')
days=sorted([d for d in json.loads((ROOT/'activity.json').read_text()) if d['date']<=datetime.date.today().isoformat()],key=lambda d:d['date'])
def svg(content,h):return '<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="'+str(h)+'" viewBox="0 0 1000 '+str(h)+'" role="img"><style>@keyframes rise{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}.cell,.bar{animation:rise .7s both}@media(prefers-reduced-motion:reduce){*{animation:none!important}}</style><rect width="1000" height="100%" rx="18" fill="#f6f3e9"/><g font-family="Arial,sans-serif" fill="#171717">'+content+'</g></svg>'
total=sum(d['count'] for d in days);active=sum(d['count']>0 for d in days)
best=current=0
for d in days:
 current=current+1 if d['count'] else 0;best=max(best,current)
tail=days[:-1] if days and days[-1]['count']==0 else days
streak=0
for d in reversed(tail):
 if not d['count']:break
 streak+=1
first=datetime.date.fromisoformat(days[0]['date']);first-=datetime.timedelta(days=(first.weekday()+1)%7)
heat='<text x="30" y="42" font-size="23" font-weight="bold">A YEAR IN THE BUILD</text><text x="30" y="70" font-size="14">Public GitHub contributions · '+str(total)+' contributions</text>'
colors=['#e3e1d7','#fff1a3','#ffe368','#f4c918','#b98e00']
for d in days:
 date=datetime.date.fromisoformat(d['date']);diff=(date-first).days;x=30+(diff//7)*17.5;y=94+(diff%7)*18
 heat+=f'<rect class="cell" x="{x}" y="{y}" width="14" height="14" rx="3" fill="{colors[min(d["level"],4)]}" style="animation-delay:{diff*.001}s"><title>{d["date"]}: {d["count"]} contributions</title></rect>'
heat+='<text x="30" y="253" font-size="12">'+days[0]['date']+' — '+days[-1]['date']+' · No private repository details shown</text>'
(ROOT/'activity-graph.svg').write_text(svg(heat,280))
months={}
for d in days:months[d['date'][:7]]=months.get(d['date'][:7],0)+d['count']
months=list(months.items())[-12:];peak=max([n for _,n in months]+[1]);bestday=max(days,key=lambda d:d['count'])
bars=f'<text x="30" y="43" font-size="34" font-weight="bold">{total} contributions</text><text x="30" y="70" font-size="14">Real activity. Small steps, visible progress.</text>'
for i,(month,n) in enumerate(months):
 h=120*n/peak;x=32+i*48
 bars+=f'<rect class="bar" x="{x}" y="{220-h}" width="30" height="{max(h,2)}" rx="3" fill="'+('#f0c900' if n==peak else '#252525')+f'"/><text x="{x+15}" y="{210-h}" text-anchor="middle" font-size="12">{n}</text><text x="{x+15}" y="246" text-anchor="middle" font-size="11">{calendar.month_abbr[int(month[-2:])]}</text>'
for i,(value,label) in enumerate([(str(active),'active days'),(str(streak)+' days','current streak'),(str(best)+' days','longest streak'),(str(bestday['count']),'busiest day: '+bestday['date'])]):
 y=55+i*61;bars+=f'<text x="675" y="{y}" font-size="28" font-weight="bold">{value}</text><text x="675" y="{y+20}" font-size="13">{label}</text>'
(ROOT/'monthly-activity.svg').write_text(svg(bars,280))
print('Rendered verified activity:',total,'contributions,',active,'active days')
