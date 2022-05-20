from urllib import parse

import xml.etree.ElementTree as ET
import base64
import json


def banner():
	"""
		Print the banner
	"""
	banner = '''
 _____                    _                       
/  __ \                  | |                      
| /  \/_ __ __ ___      _| |_ __ ___   __ _ _ __  
| |   | '__/ _` \ \ /\ / / | '_ ` _ \ / _` | '_ \ 
| \__/\ | | (_| |\ V  V /| | | | | | | (_| | |_) |
 \____/_|  \__,_| \_/\_/ |_|_| |_| |_|\__,_| .__/ 
                                           | |    
                                           |_|
                                           	By Liodeus
	'''
	print(banner)


def parsing_burp(burp_file_path, exclude_extensions, url_input):
	"""
		Parse the XML from the BurpSuite output

		Return a list of path and the url
	"""
	print("[Parsing Burpsuite file]")
	paths = []

	try:
		root = ET.parse(burp_file_path).getroot()
	except:
		print(f"\tError can't parse your file : {burp_file_path}")
		print("\tIt must be in xml format, go to [https://github.com/Liodeus/Crawlmap/wiki/Burp-Suite], to see an example.")
		exit()

	for type_tag in root.findall("item/request"):
		value = type_tag.text
		try:
			data = base64.b64decode(value).decode("utf-8")
		except:
			continue

		verb = data.split('\r\n')[0].split()
		dict_params = {
			"[GET]": [],
			"[POST]": [],
			"[UPLOAD]": []
		}

		# GET parameters
		try:
			get_data = verb[1].split('?')[1]
			for element in get_data.split('&'):
				dict_params["[GET]"].append(element.split('=')[0])
		except IndexError:
			pass

		# Upload form
		if "multipart/form-data" in data:
			data = data.split('\r\n')
			for element in data:
				if "Content-Disposition: form-data; name=" in element:
					upload_form_param = element.split(';')[1].split('=')[1][1:-1]
					dict_params["[UPLOAD]"].append(upload_form_param)

		# ONLY POST PARAMS ? (maybe PATCH, UPDATE or else, to try)
		try:
			post_params = data.split('\r\n')[-1].split('&')
			if len(post_params) > 1:
				for element in post_params:
					dict_params["[POST]"].append(element.split('=')[0])
		except:
			pass
		
		url = parse.urlsplit(url_input + verb[1])
		paths.append([url, dict_params])

	return paths


def parsing_gospider(gospider_file_path, exclude_extensions):
	"""
		Parse the JSON from the Gospider output

		Return a list of path
	"""
	print("[Parsing Gospider file]")
	paths = []

	try:
		with open(gospider_file_path) as f:
			for line in f:
				try:
					data = json.loads(line)
					type_data = data["type"]

					if type_data == "linkfinder":
						url_to_parse = data["source"]
					else:
						url_to_parse = data["output"]
				except json.decoder.JSONDecodeError:
					pass

				url = parse.urlsplit(url_to_parse)
				paths.append(url)
	except FileNotFoundError:
		print(f"Error can't parse your file : {gospider_file_path}")
		print("It must be in json format, go to [https://github.com/Liodeus/Crawlmap], to see some examples.")
		exit()
	
	return paths


def parsing_zaproxy(zaproxy_file_path, exclude_extensions):
	"""
		Parse the txt from the zaproxy output

		Return a list of path
	"""
	print("[Parsing zaproxy file]")
	paths = []

	try:
		with open(zaproxy_file_path) as f:
			for line in f:
				url = parse.urlsplit(line)
				paths.append(url)
	except FileNotFoundError:
		print(f"Error can't parse your file : {zaproxy_file_path}")
		print("It must be in txt format, go to [https://github.com/Liodeus/Crawlmap], to see some examples.")
		exit()
	
	return paths


def merge_dict(dictOne, dictTwo):
	dictThree = {}
	for one, two in zip(dictOne.items(), dictTwo.items()):
		elem = list(filter(lambda x: x != "", set(one[1] + two[1])))
		dictThree[one[0]] = elem

	return dictThree


def merge_parsing(list_of_urlsplit, domain, flag_nofile, exclude_extensions):
	"""
		Take a list of path as input, remove unneeded data from url

		Return a sorted list of url
	"""
	paths = {}
	for url_split in list_of_urlsplit:
		if url_split[0].netloc == domain:
			if flag_nofile:
				path = url_split[0].path.split('.')[0]
				data = path.split('/')
				path = '/'.join(data[:-1])
			else:
				path = url_split[0].path

				# Remove exclude extensions
				data = path.split('.')
				if len(data) > 1:
					if data[-1] in exclude_extensions:
						path = '/'.join(path.split('/')[:-1])
				
			url = f"{url_split[0].netloc}{path}"

			# Add a '/' at the end if not already there
			if url[-1] != '/':
				url = url + '/'

			try:
				paths[url] = merge_dict(paths[url], url_split[1])
			except KeyError:
				paths[url] = {}
				paths[url] = url_split[1]

	return paths


def merge_all_paths(paths_burp, paths_gospider, paths_zaproxy):
	"""
		Merge results from burp and gospider and remove duplicates

		Return a sorted list of unique path
	"""
	unique_paths = []

	for key, value in paths_burp.items():
		if (key, value) not in unique_paths:
			unique_paths.append((key, value))
		# if burp not in unique_paths:
			# unique_paths.append(burp)

	# for gospider in paths_gospider:
	# 	if gospider not in unique_paths:
	# 		unique_paths.append(gospider)

	# for zaproxy in paths_zaproxy:
	# 	if zaproxy not in unique_paths:
	# 		unique_paths.append(zaproxy)

	return sorted(unique_paths)


def writing_md(paths, url_domain, out_file, params):
	"""
		Write the paths as markdown into a file to import later on into another software
	"""
	print("Writing to file")
	list_done = []

	with open(out_file if out_file != None else "out_markdown.md", 'w') as f:
		f.write(f"- {url_domain}\n")
		for path in paths:
			url = parse.urlsplit(path[0])
			data = url.path.split('/')[1:-1]

			counter_tab = 1
			for d in data:
				to_print = '\t' * counter_tab + f"- {d}"
				to_exclude = ''.join(data[0:counter_tab]) + d

				if to_exclude not in list_done:
					f.write(f"{to_print}\n")
					list_done.append(to_exclude)
				counter_tab += 1

				if params:
					if d == data[-1]:
						for key, value in path[1].items(): 
							if value:
								for v in value:
									to_print = '\t' * (counter_tab) + f"- {key} - {v}"
									f.write(f"{to_print}\n")

