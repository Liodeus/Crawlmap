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
	except FileNotFoundError:
		print(f"Error can't parse your file : {burp_file_path}")
		print("It must be in xml format, go to [https://github.com/Liodeus/Crawlmap], to see an example.")
		exit()

	for type_tag in root.findall("item/request"):
		value = type_tag.text
		try:
			data = base64.b64decode(value).decode("utf-8").split('\r\n')
		except:
			continue
		
		url = parse.urlsplit(url_input + data[0].split()[1])
		paths.append(url)
	
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


def merge_parsing(list_of_urlsplit, domain, flag_nofile, exclude_extensions):
	"""
		Take a list of path as input, remove unneeded data from url

		Return a sorted list of url
	"""
	paths = []
	for url in list_of_urlsplit:
		if url.netloc == domain:
			if flag_nofile:
				path = url.path.split('.')[0]
				data = path.split('/')
				path = '/'.join(data[:-1])
			else:
				path = url.path

				# Remove exclude extensions
				data = path.split('.')
				if len(data) > 1:
					if data[-1] in exclude_extensions:
						path = '/'.join(path.split('/')[:-1])
				
			# url = f"{url.scheme}://{url.netloc}{path}"
			url = f"{url.netloc}{path}"

			# Add a '/' at the end if not already there
			if url[-1] != '/':
				url = url + '/'

			if url not in paths:
				paths.append(url)

	return sorted(paths)


def merge_all_paths(paths_burp, paths_gospider, paths_zaproxy):
	"""
		Merge results from burp and gospider and remove duplicates

		Return a sorted list of unique path
	"""
	unique_paths = []

	for burp in paths_burp:
		if burp not in unique_paths:
			unique_paths.append(burp)

	for gospider in paths_gospider:
		if gospider not in unique_paths:
			unique_paths.append(gospider)

	for zaproxy in paths_zaproxy:
		if zaproxy not in unique_paths:
			unique_paths.append(zaproxy)

	return sorted(unique_paths)


def writing_md(paths, url_domain, out_file):
	"""
		Write the paths as markdown into a file to import later on into another software
	"""
	print("Writing to file")
	list_done = []

	with open(out_file if out_file != None else "out_markdown.md", 'w') as f:
		f.write(f"- {url_domain}\n")
		for path in paths:
			url = parse.urlsplit(path)
			data = url.path.split('/')[1:-1]

			counter_tab = 1
			for d in data:
				to_print = '\t' * counter_tab + f"- {d}"
				to_exclude = ''.join(data[0:counter_tab]) + d

				if to_exclude not in list_done:
					f.write(f"{to_print}\n")
					list_done.append(to_exclude)
				counter_tab += 1
