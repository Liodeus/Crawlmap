from crawlmap.functions.misc import remove_slash
from urllib import parse
import xml.etree.ElementTree as ET
import base64


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
		dict_params = get_params_from_burp(data, verb)
		
		url_to_parse = remove_slash(url_input + verb[1])
		url = parse.urlsplit(url_to_parse)
		paths.append([url, dict_params])

	return paths


def get_params_from_burp(data, request):
	"""
		Get the parameters from a request

		Return a dictionnary of parameters
	"""

	dict_params = {
		"[GET]": [],
		"[POST]": [],
		"[UPLOAD]": []
	}

	# GET parameters
	try:
		get_data = request[1].split('?')[1]
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

	return dict_params
