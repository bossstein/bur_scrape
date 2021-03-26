from google_play_scraper import reviews
import re
import os

scrape_result_cache = dict()

class AppScraper:

	def __init__(self, app_url, market_tag, lang_tag, regex_strings):
		self.app_url = app_url
		self.market_tag = market_tag
		self.lang_tag = lang_tag
		self.regex_strings = regex_strings
		self.init_dir = os.getcwd()
		self.patterns = dict()
		self.result = dict()
		self.files = dict()

	def scrape(self):
		self.get_scrape_result()
		self.mkdir()
		self.print_header()
		self.extract_reviews()
		self.add_all_regex_patterns()
		self.search_for_each_pattern()
		self.output_result()
		os.chdir(self.init_dir)

	def get_scrape_result(self):
		if (self.market_tag, self.lang_tag) in scrape_result_cache:
			self.scrape_result = scrape_result_cache[(self.market_tag, self.lang_tag)]
		else: 
			self.init_scrape_site()
			self.remaining_scrape_site()
			scrape_result_cache[(self.market_tag, self.lang_tag)] = self.scrape_result

	def dir_path(self):
		return os.path.join(os.getcwd(),self.lang_tag + "_" + self.market_tag)

	def mkdir(self):
		self.new_path = self.dir_path()
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
				lang=self.lang_tag, # defaults to 'en'
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
		if self.scrape_result \
		and self.scrape_result[-1] \
		and self.scrape_result[-1]['content'] \
		and self.scrape_result[-1]['content'][0:30]:
			print("scraping... " + self.len_str() + "\t== " + self.scrape_result[-1]['content'][0:30])
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
		for s in self.regex_strings:
			self.add_pattern(s)

	def search_for_each_pattern(self):
		for s, p in self.patterns.items():
			self.result[s] = 0
			self.files[s] = open( os.path.join(self.new_path, s[:20] + ".txt"), 'w+' )
			self.process_all_reviews_for_pattern(s,p)

	def process_all_reviews_for_pattern(self, pattern_string, pattern_regex):
		for r in self.reviews:
			if not r or not pattern_regex.search(str(r)):
				continue
			self.result[pattern_string] += 1
			self.files[pattern_string].write( r + '\n' )

	def output_result(self):
		out_file = open( os.path.join(self.new_path, self.market_tag + ".txt"), 'w+' )
		out_file.write("Length = " + str(len(self.scrape_result)) + "\n")
		for search_string, count in self.result.items():
			out_string = "Search pattern * " + search_string + " * returned result of : " + str(count)
			print(out_string)
			out_file.write( out_string + '\n' )
			self.files[search_string].close()
			print("")
		out_file.close()

class ThreeStarScraper(AppScraper):
	def extract_reviews(self):
		self.reviews = [ e["content"] for e in self.scrape_result if e["score"] < 4 ]
	def dir_path(self):
		return os.path.join(os.getcwd(),self.lang_tag + "_" + self.market_tag + "_three_star")

de_regex_strings = ["[tT]ablet|[iI][pP]ad"
	,"[cC]oin|[cC]ashback|[gG]utschein"
	,"[lL]ist|[sS]peichern|[eE]inkaufszettel|[lL]ieblings|[fF]avorit"
	,"[bB]riefkast"
	,"[Aa]ldi|[Pp]enny|[Nn]etto|[Kk]aufland|[sS]aturn| [Ff]ehlen| [fF]ehlt"
	,"[wW]erbung"
	,"[sS]tandort|[nN][aä]he|[sS]t[äa]dt|[pP]ostleitzahl"
	,"[pP]apier|[uU]mwelt|nachhaltig"
	,"[kK]arte"
	,"[Zz]oom"
	,"offline"
	,"[Cc]orona|[Ll]ockdown"]

fr_regex_strings = ["[nN]otifications"
	,"[Pp]apier|[ÉeéE]colo|[Pp]lan[èe]te"
	,"[bB]o[iî]te|[Cc]ourrier|courriel"
	," en avan"
	,"[Cc]artes?"
	,"[àa] jour"
	,"local|[0-9 ]km|code postal"
	,"[Zz]oom|[Aa]grandi"
	,"[Cc]onfinement|[Cc]orona"
	,"[Ll]istes? des? courses?|[Ll]istes? d?'?achats?|[Ff]avori|[sS]auve"
	,"[Bb]ons? (de)? réduction|[Cc]oupon"
	,"[Mm]anqu"
	,"[Tt]ablette"
	,"offline"
	,"[tT]rop (de)? pubs?|[Tt]rop (de )?publicit[ée]s?|[Bb]ourr[ée]e?s? (de )?pubs?|[Bb]ourr[ée]e?s? (de )?publicit[ée]s?|[Bb]lind[ée]e?s? (de )?pubs?|[Bb]lind[ée]e?s? (de )?publicit[ée]s?|[Cc]ombl[ée]e?s? (des? )?pubs?|[Cc]omblee?s? (des? )?publiticit[ée]s?|pub [àa] (la)? pub|[Rr]emplie?s? (de )?pubs?|[Rr]emplie?s? (de )?publicit[ée]s|pubs? vid[ée]o|pop up"]

it_regex_strings = ["[sS]alv[ao]|preferiti|[lL]ista della spesa"
	,"[Cc]arte |fedelt[àa]|[tT]esser"
	,"[Aa]ggiorna|in ritardo|puntual"
	,"[Cc]artace|[cC]assetta"
	,"[Zz]oom|ingrandi"
	,"[Cc]ashback|[Cc]oupon|[Bb]uoni sconto|[Bb]uono sconto"
	,"[Ii]nterattiv"
	,"[Aa]mbiente|carta |giornalini|spreco|spreca |sprechi|sprecare"
	,"[Mm]ancant|ignorat|manca |mancano"
	,"[Nn]otifiche"
	,"cancella|rimouv|scadut"
	,"offline"
	,"ritaglio|ritaglia|forbici"
	,"anteprim|anticip"
	,"[Ff]iltr|ordina per|ordino per|ordinare per"
	,"[Rr]egione|[Pp]rovincia|[rR]oma|[Ll]ocal|[pP]osizione|distanza|zona|chilometr|vicin|due passi da"
	,"[tT]ablet"
	,"[Pp]andemia|[Vv]irus|[Cc]orona|[Ll]ockdown"
	,"[Pp]ubblicit[aà]"]


def de_scrape(app_url, market_tag):
	a = AppScraper(app_url, market_tag, 'de', de_regex_strings)
	a.scrape()
	a = ThreeStarScraper(app_url, market_tag, 'de', de_regex_strings)
	a.scrape()

def fr_scrape(app_url, market_tag):
	a = AppScraper(app_url, market_tag, 'fr', fr_regex_strings)
	a.scrape()
	a = ThreeStarScraper(app_url, market_tag, 'fr', fr_regex_strings)
	a.scrape()

def it_scrape(app_url, market_tag):
	a = AppScraper(app_url, market_tag, 'it', it_regex_strings)
	a.scrape()
	a = ThreeStarScraper(app_url, market_tag, 'it', it_regex_strings)
	a.scrape()

de_scrape('com.marktguru.mg2.de', 'marktguru')
de_scrape('com.bonial.kaufda', 'kaufda')
de_scrape('de.meinprospekt.android', 'meinprospekt')
de_scrape('de.prospektangebote.app', 'kingbee_de')
de_scrape('com.actuelleprospekte', 'aktuelle_prospekte')
de_scrape('com.gamebegins.alleprospekte', 'alle_prospekte_angebote')
de_scrape('de.weekli.WeekliAndroid', 'weekli')
de_scrape('com.rzmobile.aktuellemainprospekte', 'prospekte_angebote')
de_scrape('de.youpickit.androidapp', 'einkaufen_prospekte_angebote_coupons')
de_scrape('com.wunderkauf.android', 'wunderkauf')
de_scrape('com.sales.deals.weekly.ads.offers', 'listonic_fr')
de_scrape('com.geomobile.tiendeo', 'tiendeo_de')
de_scrape('sk.kimbinogreen.kimbino', 'kimbino_de')
de_scrape('de.discounto', 'discount')
de_scrape('hu.p_app.angebot', 'prospekt_angebot_de')
de_scrape('de.marktjagd.android', 'marktjagd')


fr_scrape('fr.promocatalogues.app', 'kingbee_fr')
fr_scrape('fr.bonial.android', 'bonial')
fr_scrape('com.cataloguepromotionsprospectus', 'catalogues_promo_et_prospectus')
fr_scrape('com.CataloguesActuelFr', 'catalogue_actuel')
fr_scrape('com.geomobile.tiendeo', 'tiendeo_fr')
fr_scrape('com.actuel.catalogue', 'promotions_catalogue')
fr_scrape('com.sales.deals.weekly.ads.offers', 'listonic_fr')
fr_scrape('info.funnyfoodpromofr', 'catalogue_promo_valioman')
fr_scrape('it.doveconviene.android', 'shopfully')
fr_scrape('sk.kimbinogreen.kimbino', 'kimbino_fr')

it_scrape('it.promoqui.android', 'promoqui')
it_scrape('com.webfacile.volantinofacile', 'volantino_facile')
it_scrape('it.doveconviene.android', 'dove_conviene')
it_scrape('com.nextre.mobile.CentroVolantini', 'centro_volantini')
it_scrape('com.geomobile.tiendeo', 'tiendeo_it')
it_scrape('it.offertevolantini.app', 'kingbee_it')
it_scrape('com.sales.deals.weekly.ads.offers', 'listonic_it')
it_scrape('sk.kimbinogreen.kimbino', 'kimbino')
it_scrape('it.trovaprezzi.android', 'trovaprezzi')

