from urllib import parse

import xml.etree.ElementTree as ET
import argparse
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


def parsing_burp(burp_file_path, exclude_extensions):
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
		print("It must be a xml file, go to [https://github.com/Liodeus/Crawlmap], to see an example.")
		exit()

	url_domain = root.findall("item/url")[0].text

	if url_domain[-1] == '/':
		url_domain = url_domain[:-1]

	for type_tag in root.findall("item/request"):
		value = type_tag.text
		try:
			data = base64.b64decode(value).decode("utf-8").split('\r\n')
		except:
			continue
		
		url = parse.urlsplit(url_domain + data[0].split()[1])
		paths.append(url)
	
	return paths, url_domain


def parsing_gospider(gospider_file_path, exclude_extensions):
	"""
		Parse the JSON from the Gospider output

		Return a list of path
	"""
	print("[Parsing Gospider file]")
	paths = []

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
	
	return paths


def merge_parsing(list_of_urlsplit, domain, flag_nofile):
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
				
			url = f"{url.scheme}://{url.netloc}{path}"

			# Add a '/' at the end if not already there
			if url[-1] != '/':
				url = url + '/'

			if url not in paths:
				paths.append(url)

	return sorted(paths)


def merge_burp_gospider(paths_burp, paths_gospider):
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


if __name__ == '__main__':
	banner()

	parser = argparse.ArgumentParser()
	parser.add_argument("-b", "--burp", required=True, help="Output from BurSuite (xml)", type=str)
	parser.add_argument("-g", "--gospider", help="Output from Gospider (json)", type=str)
	parser.add_argument("-o", "--out", help="Output file", type=str)
	parser.add_argument("--exclude", help="Exclude extensions (Example : \"png,svg,css,ico\")", type=str, default="")
	parser.add_argument("--nofiles", help="Don't print files, only folders", action="store_true", default=False)
	args = parser.parse_args()

	# Getting user input
	burp = args.burp
	gospider = args.gospider
	out_file = args.out
	exclude_extensions = [x.lower() for x in args.exclude.split(',')]

	# Launch the parsing of output file(s)
	paths_burp, url_domain = parsing_burp(burp, exclude_extensions)
	domain = url_domain.split('//')[1]
	paths_burp = merge_parsing(paths_burp, domain, args.nofiles)

	if gospider :
		paths_gospider = parsing_gospider(gospider, exclude_extensions)
		paths_gospider = merge_parsing(paths_gospider, domain, args.nofiles)
		merge_paths = merge_burp_gospider(paths_burp, paths_gospider)

		writing_md(merge_paths, url_domain, out_file)
	else:
		writing_md(paths_burp, url_domain, out_file)
