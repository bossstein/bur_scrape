from google_play_scraper import reviews
import re
import os

class AppScraper:

	def __init__(self, app_url, market_tag):
		self.app_url = app_url
		self.market_tag = market_tag
		self.init_dir = os.getcwd()
		self.patterns = dict()
		self.result = dict()
		self.files = dict()

	def scrape(self):
		self.init_scrape_site()
		self.remaining_scrape_site()
		self.mkdir()
		self.print_header()
		self.extract_reviews()
		self.add_all_regex_patterns()
		self.search_for_each_pattern()
		self.output_result()
		os.chdir(self.init_dir)

	def mkdir(self):
		self.new_path = os.path.join(os.getcwd(),self.market_tag)
		if not self.scrape_result:
			return
		os.mkdir(self.new_path)
		os.chdir(self.new_path)

	def init_scrape_site(self):
		print("scraping... " + self.market_tag )
		self.scrape_result = []
		self.cont_token = None
		try:
			self.scrape_result, self.cont_token = reviews(
				self.app_url,
				lang='de', # defaults to 'en'
				count=200
			)
		except:
			print(self.market_tag + " FAILED!! ")
			return
		self.fail_count = 0

	def remaining_scrape_site(self):
		while self.cont_token.token and self.fail_count < 6:
			self.scrape_iter()
		print("success with final count... " + self.len_str())

	def scrape_iter(self):
		print("scraping... " + self.len_str() + "\t\t== " + self.scrape_result[-1]['content'][0:30])
		clean_token = self.cont_token
		try:
			new_reviews, self.cont_token = reviews(
				self.app_url,
				continuation_token = self.cont_token
			)
			self.fail_count = 0
			self.scrape_result += new_reviews
		except:
			self.fail_count += 1
			self.cont_token = clean_token
			print("fail number " + str(self.fail_count) + " count " + self.len_str())

	def len_str(self):
		return str(len(self.scrape_result))

	def print_header(self):
		print("")
		print("Length = " + str(len(self.scrape_result)))
		print("")

	def extract_reviews(self):
		self.reviews = [ e["content"] for e in self.scrape_result ]

	def add_pattern(self, s):
		self.patterns[s] = re.compile(s)

	def add_all_regex_patterns(self):
		self.add_pattern("[tT]ablet|[iI][pP]ad")
		self.add_pattern("[cC]oin|[cC]ashback|[gG]utschein")
		self.add_pattern("[lL]ist|[sS]peichern")
		self.add_pattern("[bB]riefkast")
		self.add_pattern("[lL]ieblings|[fF]avorit")
		self.add_pattern("[Aa]ldi|[Pp]enny|[Nn]etto|[Kk]aufland|[sS]aturn|[Ff]ehlen|[fF]ehlt")
		self.add_pattern("[wW]erbung")
		self.add_pattern("[sS]tandort|[nN]ahe|[sS]tadt|[pP]ostleitzahl")
		self.add_pattern("[pP]apier|[uU]mwelt")

	def search_for_each_pattern(self):
		for s, p in self.patterns.items():
			self.result[s] = 0
			self.files[s] = open( os.path.join(self.new_path, s + ".txt"), 'w+' )
			self.process_all_reviews_for_pattern(s,p)

	def process_all_reviews_for_pattern(self, pattern_string, pattern_regex):
		for r in self.reviews:
			if not pattern_regex.search(r):
				continue
			self.result[pattern_string] += 1
			self.files[pattern_string].write( r + '\n' )

	def output_result(self):
		out_file = open( os.path.join(self.new_path, self.market_tag + ".txt"), 'w+' )
		for search_string, count in self.result.items():
			out_string = "Search pattern * " + search_string + " * returned result of : " + str(count)
			print(out_string)
			out_file.write( out_string + '\n' )
			self.files[search_string].close()
			print("")
		out_file.close()

a = AppScraper('com.marktguru.mg2.de', 'marktguru')
a.scrape()
