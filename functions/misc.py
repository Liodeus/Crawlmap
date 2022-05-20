from urllib import parse


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


def merge_dict(dictOne, dictTwo):
	"""
		TODO
	"""

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

	for key, value in paths_gospider.items():
		if (key, value) not in unique_paths:
			unique_paths.append((key, value))

	for key, value in paths_zaproxy.items():
		if (key, value) not in unique_paths:
			unique_paths.append((key, value))

	return sorted(unique_paths, key=lambda x: x[0])


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
