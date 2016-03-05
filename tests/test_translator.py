import os
import unittest

import mock

from http_request_translator import translator
from .utils import load_args


class TestTranslator(unittest.TestCase):

    ###
    # translator.parse_raw_request
    ###
    def test_parse_raw_request_http_version_with_path(self):
        for i in range(0, 10):
            for j in range(0, 10):
                raw_request = "GET /robots.txt HTTP/%d.%d\n"\
                              "Host: foo.bar" % (i, j)
                self.assertEqual(
                    translator.parse_raw_request(raw_request),
                    (
                        ['Host: foo.bar'],
                        {
                            'protocol': 'HTTP',
                            'pre_scheme': '',
                            'Host': 'foo.bar',
                            'version': '%d.%d' % (i, j),
                            'path': '/robots.txt',
                            'method': 'GET',
                            'data': ''
                        }
                    ),
                    'Invalid parsing of HTTP/%d.%d request!' % (i, j))

    def test_parse_raw_request_http_version_invalid(self):
        raw_request = "GET /\n"\
                      "Host: foo.bar"
        self.assertEqual(
            translator.parse_raw_request(raw_request),
            (
                ['Host: foo.bar'],
                {
                    'protocol': '',
                    'pre_scheme': '',
                    'Host': 'foo.bar',
                    'version': '',
                    'path': '',
                    'method': 'GET',
                    'data': ''
                }
            ),
            'Invalid parsing of request!')
        raw_request = "GET / HTTP//1.b\n"\
                      "Host: foo.bar"
        self.assertEqual(
            translator.parse_raw_request(raw_request),
            (
                ['Host: foo.bar'],
                {
                    'protocol': 'HTTP',
                    'pre_scheme': '',
                    'Host': 'foo.bar',
                    'version': '/1.b',
                    'path': '/',
                    'method': 'GET',
                    'data': ''
                }
            ),
            'Invalid parsing of HTTP//1.b request!')

    def test_parse_raw_request_http_with_parameter(self):
        raw_request = "GET /?foo=bar HTTP/1.1\n"\
                      "Host: foo.bar"
        self.assertEqual(
            translator.parse_raw_request(raw_request),
            (
                ['Host: foo.bar'],
                {
                    'protocol': 'HTTP',
                    'pre_scheme': '',
                    'Host': 'foo.bar',
                    'version': '1.1',
                    'path': '/?foo=bar',
                    'method': 'GET',
                    'data': ''
                }
            ),
            'Invalid parsing of request with parameter in path!')

    def test_parse_raw_request_http_with_comment(self):
        raw_request = "GET /#foo=bar HTTP/1.1\n"\
                      "Host: foo.bar"
        self.assertEqual(
            translator.parse_raw_request(raw_request),
            (
                ['Host: foo.bar'],
                {
                    'protocol': 'HTTP',
                    'pre_scheme': '',
                    'Host': 'foo.bar',
                    'version': '1.1',
                    'path': '/#foo=bar',
                    'method': 'GET',
                    'data': ''
                }
            ),
            'Invalid parsing of request with comment in path!')

    def test_parse_raw_request_http_with_coma(self):
        raw_request = "GET /;foo=bar HTTP/1.1\n"\
                      "Host: foo.bar"
        self.assertEqual(
            translator.parse_raw_request(raw_request),
            (
                ['Host: foo.bar'],
                {
                    'protocol': 'HTTP',
                    'pre_scheme': '',
                    'Host': 'foo.bar',
                    'version': '1.1',
                    'path': '/;foo=bar',
                    'method': 'GET',
                    'data': ''
                }
            ),
            'Invalid parsing of request with coma in path!')

    def test_parse_raw_request_https_domain_no_port(self):
        raw_request = "GET https://google.com/robots.txt HTTP/1.1\n"\
                      "Host: google.com"
        self.assertEqual(
            translator.parse_raw_request(raw_request),
            (
                ['Host: google.com'],
                {
                    'protocol': 'HTTP',
                    'pre_scheme': 'https://',
                    'Host': 'google.com',
                    'version': '1.1',
                    'path': '/robots.txt',
                    'method': 'GET',
                    'data': ''
                }
            ),
            'Invalid parsing of HTTP request with domain host!')

    def test_parse_raw_request_https_domain_port(self):
        raw_request = "GET https://google.com:31337/robots.txt HTTP/1.1\n"\
                      "Host: google.com:31337"
        self.assertEqual(
            translator.parse_raw_request(raw_request),
            (
                ['Host: google.com:31337'],
                {
                    'protocol': 'HTTP',
                    'pre_scheme': 'https://',
                    'Host': 'google.com:31337',
                    'version': '1.1',
                    'path': '/robots.txt',
                    'method': 'GET',
                    'data': ''
                }
            ),
            'Invalid parsing of HTTP request with domain host and custom port!')

    def test_parse_raw_request_https_ipv4_no_port(self):
        raw_request = "GET https://127.0.0.1/robots.txt HTTP/1.1\n"\
                      "Host: 127.0.0.1"
        self.assertEqual(
            translator.parse_raw_request(raw_request),
            (
                ['Host: 127.0.0.1'],
                {
                    'protocol': 'HTTP',
                    'pre_scheme': 'https://',
                    'Host': '127.0.0.1',
                    'version': '1.1',
                    'path': '/robots.txt',
                    'method': 'GET',
                    'data': ''
                }
            ),
            'Invalid parsing of HTTP request with IPv4 host!')

    def test_parse_raw_request_https_ipv4_port(self):
        raw_request = "GET https://127.0.0.1:31337/robots.txt HTTP/1.1\n"\
                      "Host: 127.0.0.1:31337"
        self.assertEqual(
            translator.parse_raw_request(raw_request),
            (
                ['Host: 127.0.0.1:31337'],
                {
                    'protocol': 'HTTP',
                    'pre_scheme': 'https://',
                    'Host': '127.0.0.1:31337',
                    'version': '1.1',
                    'path': '/robots.txt',
                    'method': 'GET',
                    'data': ''
                }
            ),
            'Invalid parsing of HTTP request with IPv4 host and custom port!')

    def test_parse_raw_request_https_ipv6_no_port(self):
        raw_request = "GET https://[::1]/robots.txt HTTP/1.1\n"\
                      "Host: [::1]"
        self.assertEqual(
            translator.parse_raw_request(raw_request),
            (
                ['Host: [::1]'],
                {
                    'protocol': 'HTTP',
                    'pre_scheme': 'https://',
                    'Host': '[::1]',
                    'version': '1.1',
                    'path': '/robots.txt',
                    'method': 'GET',
                    'data': ''
                }
            ),
            'Invalid parsing of HTTP request with IPv6 host!')

    def test_parse_raw_request_https_ipv6_port(self):
        raw_request = "GET https://[::1]:31337/robots.txt HTTP/1.1\n"\
                      "Host: [::1]:31337"
        self.assertEqual(
            translator.parse_raw_request(raw_request),
            (
                ['Host: [::1]:31337'],
                {
                    'protocol': 'HTTP',
                    'pre_scheme': 'https://',
                    'Host': '[::1]:31337',
                    'version': '1.1',
                    'path': '/robots.txt',
                    'method': 'GET',
                    'data': ''
                }
            ),
            'Invalid parsing of HTTP request with IPv6 host and custom port!')

    def test_parse_raw_request_multiple_host_header(self):
        raw_request = "GET https://foo.bar HTTP/1.1\n"\
                      "Host: foo.bar\n"\
                      "HoSt: foo.bar\n"\
                      "HOST: foo.bar \n"\
                      "host: foo.bar\n"\
                      "host:     foo.bar\n"
        self.assertEqual(
            translator.parse_raw_request(raw_request),
            (
                [
                    'Host: foo.bar',
                    'HoSt: foo.bar',
                    'HOST: foo.bar ',
                    'host: foo.bar',
                    'host:     foo.bar',
                ],
                {
                    'protocol': 'HTTP',
                    'pre_scheme': 'https://',
                    'Host': 'foo.bar',
                    'version': '1.1',
                    'path': '',
                    'method': 'GET',
                    'data': ''
                }
            ),
            'Invalid parsing of HTTP request with multiple Host headers!')

    def test_parse_raw_request_invalid_header(self):
        raw_request = "GET https://foo.bar HTTP/1.1\n"\
                      "Host"
        with self.assertRaises(ValueError):
            translator.parse_raw_request(raw_request)

    def test_parse_raw_request_no_path(self):
        raw_request = "GET\n"\
                      "Host: foo.bar"
        with self.assertRaises(ValueError):
            translator.parse_raw_request(raw_request)

    def test_process_arguments_with_no_arguments(self):
        args = load_args()

        with self.assertRaises(SystemExit) as exc:
            translator.process_arguments(args)

        self.assertEqual(exc.exception.code, -1)

    def test_process_arguments_with_interactive_mode(self):
        args = load_args(language=["bash"], interactive=True)

        with self.assertRaises(SystemExit) as exc:
            with mock.patch('http_request_translator.translator.take_headers', side_effect=KeyboardInterrupt):
                translator.process_arguments(args)

        self.assertEqual(exc.exception.code, 0)

    def test_process_arguments_with_request(self):
        request_data = """GET  HTTP/1.1\nHost: google.com\nCache-Control: no-cache"""
        args = load_args(language=["bash"], request=request_data)

        self.assertEqual(type(translator.process_arguments(args)), type({}))

    def test_process_arguments_with_file(self):
        request_data = """GET  HTTP/1.1\nHost: google.com\nCache-Control: no-cache"""
        with open('temp', 'w+') as f:
            f.write(request_data)

        args = load_args(language=["bash"], file='temp')

        self.assertEqual(type(translator.process_arguments(args)), type({}))
        os.remove('temp')

    def test_process_arguments_with_no_language(self):
        request_data = """GET  HTTP/1.1\nHost: google.com\nCache-Control: no-cache"""
        args = load_args(request=request_data)

        self.assertEqual(type(translator.process_arguments(args)), type({}))

    def test_process_arguments_with_multiple_language(self):
        request_data = """GET  HTTP/1.1\nHost: google.com\nCache-Control: no-cache"""
        args = load_args(language=["bash", "php", "python"], request=request_data)

        self.assertEqual(type(translator.process_arguments(args)), type({}))

    def test_process_arguments_with_wrong_language(self):
        request_data = """GET  HTTP/1.1\nHost: google.com\nCache-Control: no-cache"""
        args = load_args(language=["lua"], request=request_data)

        with self.assertRaises(ValueError):
            translator.process_arguments(args)

    def test_process_arguments_with_data(self):
        request_data = """GET  HTTP/1.1\nHost: google.com\nCache-Control: no-cache"""
        args = load_args(language=["bash"], data="sample=1", request=request_data)

        self.assertEqual(type(translator.process_arguments(args)), type({}))

    def test_process_arguments_with_proxy_with_scheme(self):
        request_data = """GET  HTTP/1.1\nHost: google.com\nCache-Control: no-cache"""
        args = load_args(language=["bash"], proxy="http://someproxy.com", request=request_data)

        self.assertEqual(type(translator.process_arguments(args)), type({}))

    def test_process_arguments_with_proxy_without_scheme_without_port(self):
        request_data = """GET  HTTP/1.1\nHost: google.com\nCache-Control: no-cache"""
        args = load_args(language=["bash"], proxy="127.0.0.1", request=request_data)

        self.assertEqual(type(translator.process_arguments(args)), type({}))

    def test_process_arguments_with_proxy_without_scheme_with_port(self):
        request_data = """GET  HTTP/1.1\nHost: google.com\nCache-Control: no-cache"""
        args = load_args(language=["bash"], proxy="127.0.0.1:1337", request=request_data)

        self.assertEqual(type(translator.process_arguments(args)), type({}))

    def test_process_arguments_with_invalid_proxy_without_scheme(self):
        request_data = """GET  HTTP/1.1\nHost: google.com\nCache-Control: no-cache"""
        args = load_args(language=["bash"], proxy="127.0.0.", request=request_data)

        with self.assertRaises(ValueError):
            translator.process_arguments(args)

    def test_process_arguments_with_invalid_proxy_with_scheme(self):
        request_data = """GET  HTTP/1.1\nHost: google.com\nCache-Control: no-cache"""
        args = load_args(language=["bash"], proxy="http://127.0.0.", request=request_data)

        with self.assertRaises(ValueError):
            translator.process_arguments(args)

    def test_process_arguments_with_no_data_and_method_post(self):
        request_data = """POST  HTTP/1.1\nHost: google.com"""
        args = load_args(request=request_data)

        with self.assertRaises(SystemExit) as exc:
            translator.process_arguments(args)

        self.assertEqual(exc.exception.code, -1)


if __name__ == '__main__':
    unittest.main()
