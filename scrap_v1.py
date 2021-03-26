from google_play_scraper import reviews_all
import re

scrape_result = reviews_all(
    'com.marktguru.mg2.de',
    lang='de', # defaults to 'en'
    country='us', # defaults to 'us'
)

print("-----------")
print(" Marktguru ")
print("-----------")
print("")
print("Length = " + str(len(scrape_result)))
print("")

reviews = [ e["content"] for e in scrape_result ]

patterns = dict()

def add_pattern(s):
	patterns[s] = re.compile(s)

add_pattern("[tT]ablet|[iI][pP]ad")
add_pattern("[cC]oin|[cC]ashback|[gG]utschein")
add_pattern("[lL]ist|[sS]peichern")
add_pattern("[bB]riefkast")
add_pattern("[lL]ieblings|[fF]avorit")
add_pattern("[Aa]ldi|[Pp]enny|[Nn]etto|[Kk]aufland|[sS]aturn|[Ff]ehlen|[fF]ehlt")
add_pattern("[wW]erbung")
add_pattern("[sS]tandort|[nN]ahe|[sS]tadt|[pP]ostleitzahl")
add_pattern("[pP]apier|[uU]mwelt")

result = dict()
files = dict()

for s, p in patterns.items():
	result[s] = 0
	files[s] = open( s + ".txt", 'w' )
	for r in reviews:
		if p.search(r):
			result[s] += 1
			files[s].write(r+'\n')


for search_string, count in result.items():
	print("Search pattern * " + search_string + " * returned result of : " + str(count))
	files[search_string].close()
	print("")
