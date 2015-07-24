from __future__ import print_function

import re
try:
    from urllib import quote
except ImportError:
    from urllib.parse import quote

from url import check_valid_url, get_url


def generate_script(header_dict, details_dict, searchString=None):
    """Generate the ruby script for the passed request.

    :param dict header_dict: Header dictionary containing fields like 'Host','User-Agent'.
    :param dict details_dict: Request specific details like body and method for the request.
    :param str searchString: String to search for in the response to the request. By default remains None.

    :raises ValueError: When Url is Invalid

    :return: A combined string of generated code
    :rtype:`str`
    """
    method = details_dict['method'].strip()
    url = get_url(header_dict['Host'], details_dict['pre_scheme'])
    path = details_dict['path']

    if path != "":
        url += path

    encoding_list = ['HEAD', 'OPTIONS', 'GET']

    if details_dict['data'] and (details_dict['method'].strip() in encoding_list):
        encoded_data = quote(details_dict['data'], '')
        url = url + encoded_data

    if not check_valid_url(url):
        raise ValueError("Invalid URL")

    skeleton_code = """
require 'net/http'
require 'uri'

uri = URI('%s')""" % (url)

    if method == "GET":
        skeleton_code += """
req = Net::HTTP::Get.new(uri.request_uri)
%s %s %s
response = http.request(req)""" % (generate_request_headers(header_dict),
                                   generate_proxy_code(details_dict), generate_https_code(url))
    elif method == "POST":
        body = details_dict['data']
        skeleton_code += """
req = Net::HTTP::Post.new(uri.request_uri)
%s
req.body = '%s'\n %s %s
response = http.request(req)
""" % (generate_request_headers(header_dict), generate_body_code(body),
            generate_proxy_code(details_dict), generate_https_code(url))

    if searchString:
        skeleton_code += """
puts 'Response #{response.code} #{response.message}:'

begin
    require 'colorize'
rescue LoadError
    puts "search option will need colorize to work properly"
    puts "You can install it by gem install colorize"
end

matched = response.body.match /%s/

original = response.body
if matched then
    for i in 0..matched.length
        original.gsub! /#{matched[i]}/, "#{matched[i]}".green
    end
end
puts original
""" % (searchString)
    else:
        skeleton_code += """
puts "Response #{response.code} #{response.message}:
          #{response.body}"
"""

    return skeleton_code


def generate_request_headers(header_dict):
    """Place the request headers in ruby script from header dictionary.

    :param dict header_dict: Header dictionary containing fields like 'Host','User-Agent'.

    :return: A string of ruby code which places headers in the request.
    :rtype:`str`
    """
    skeleton = ""
    for key, value in header_dict.items():
        skeleton += """req['%s'] = '%s' \n""" % (str(key), str(value))

    return skeleton


def generate_https_code(url):
    """Checks if url is 'https' and returns appropriate ruby code.

    :param str url: Url for the request

    :return: A string of ruby code
    :rtype:`str`
    """
    if url.startswith('https'):
        return "\nhttp.use_ssl=true"
    else:
        return ""


def generate_proxy_code(details_dict):
    """Checks if proxy is provided and returns appropriate ruby code.

    :param dict details_dict: Dictionary of request details containing proxy specific information.

    :raises IndexError: When proxy provided is invalid

    :return: A string of ruby code
    :rtype:`str`
    """
    if 'proxy' in details_dict:
        try:
            proxy_host, proxy_port = details_dict['proxy'].split(':')
            return """
proxy_host, proxy_port = '%s', '%s'
http = Net::HTTP.new(uri.hostname, nil, proxy_host, proxy_port)
""" % (proxy_host.strip(), proxy_port.strip())
        except IndexError:
            raise IndexError("Proxy provided is invalid.")
    else:
        return """
http = Net::HTTP.new(uri.hostname, uri.port)
"""


def generate_body_code(body):
    """Generate string for body part of the request.

    :param str body:Passed body of the request

    :return: A formatted string of body code
    :rtype:`str`

    """
    # Escape single quotes , double quotes are good here
    body = re.sub(r"'", "\\'", body)
    return str(body)
