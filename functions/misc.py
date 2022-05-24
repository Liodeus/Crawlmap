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
		Merge two dictionnary and only add once a duplicate

		Return a dictionnary
	"""

	dictThree = {}
	for one, two in zip(dictOne.items(), dictTwo.items()):
		elem = list(filter(lambda x: x != "", set(one[1] + two[1])))
		dictThree[one[0]] = elem

	return dictThree


def merge_parsing(list_of_urlsplit, domain, flag_nofile, exclude_extensions):
	"""
		Take a list of path as input, remove unneeded data from url

		Return a list of url
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

		Return a sorted list of unique path and their parameters
	"""

	unique_paths = {}
	unique_paths = merge_all_params(unique_paths, paths_burp)
	unique_paths = merge_all_params(unique_paths, paths_gospider)
	unique_paths = merge_all_params(unique_paths, paths_zaproxy)

	return {k: unique_paths[k] for k in sorted(unique_paths)}


def merge_all_params(unique_paths, d):
	"""
		Merge all parameters and remove duplicates

		Return unique_paths which is a dictionnary
	"""

	for key, value in d.items():
		try:
			unique_paths[key] = merge_dict(unique_paths[key], value)
		except KeyError:
			unique_paths[key] = {}
			unique_paths[key] = value
	return unique_paths


def remove_slash(url):
	try:
		data = url.split('://')
		data_split = data[1].split('/')
		data_split = [x for x in data_split if x != ""]
		url = f"{data[0]}://{'/'.join(data_split)}"
	except:
		pass

	return url


def writing_md(paths, url_domain, out_file, params):
	"""
		Write the paths as markdown into a file to import later on into another software
	"""

	print("Writing to file")
	list_done = []

	with open(out_file if out_file != None else "out_markdown.md", 'w') as f:
		f.write(f"- {url_domain}\n")
		for path, parameters in paths.items():
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

				if params:
					if d == data[-1]:
						for key, value in parameters.items(): 
							if value:
								for v in value:
									to_print = '\t' * (counter_tab) + f"- {key} - {v}"
									f.write(f"{to_print}\n")
