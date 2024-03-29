import re
import requests
import subprocess
import time
import pprint
from lxml import etree


class FictionDownloader():

    def __init__(self) -> None:
        self.save_path = '~/Documents/'

        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (X11; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0',
        }

        self.search_headers = {
            'Host':
                'www.baidu.com',
            'User-Agent':
                'Mozilla/5.0 (X11; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0',
            'Accept':
                '*/*',
            'Accept-Language':
                'en-US,en;q=0.5',
            'X-Requested-With':
                'XMLHttpRequest',
            'Connection':
                'keep-alive',
            'Referer':
                'https://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&rsv_idx=1&tn=baidu&wd=%E9%BE%99%E7%AC%A6%20%E4%B8%8B%E8%BD%BD&oq=%25E9%25BE%2599%25E7%25AC%25A6%2520%25E4%25B8%258B%25E8%25BD%25BD&rsv_pq=c73a3e87000254a8&rsv_t=26423%2BjJJBDy%2FhH%2FCJU9hAmuMbKbCIkbnr%2BUIQK3aBRt71xJRlUnOtP5iqE&rqlang=cn&rsv_dl=tb&rsv_enter=0&rsv_btype=t',
            'is_referer':
                'https://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&rsv_idx=1&tn=baidu&wd=%E9%BE%99%E7%AC%A6%20%E4%B8%8B%E8%BD%BD&oq=requsets%2520https&rsv_pq=b793ec400001142b&rsv_t=566bNOXLrpw6uc1PZ8Olwt8M16V728piElQluc2o6knPadylZtUOVdbYZyI&rqlang=cn',
        }

        self.search_url = 'https://www.baidu.com/s?ie=utf-8&mod=1&isid=6A8BCCA443C96435&ie=utf-8&f=8&rsv_bp=1&rsv_idx=1&tn=baidu&wd={}&oq=%25E9%25BE%2599%25E7%25AC%25A6%2520%25E4%25B8%258B%25E8%25BD%25BD&rsv_pq=c73a3e87000254a8&rsv_t=26423%2BjJJBDy%2FhH%2FCJU9hAmuMbKbCIkbnr%2BUIQK3aBRt71xJRlUnOtP5iqE&rqlang=cn&rsv_dl=tb&rsv_enter=0&rsv_btype=t&bs=%E9%BE%99%E7%AC%A6%20%E4%B8%8B%E8%BD%BD&rsv_sid=undefined&_ss=1&clist=&hsug=&f4s=1&csor=0&_cr1=31293'

    def get_response(self, url, headers):
        return requests.get(
            url,
            headers=headers,
        ).content

    def search_by_fcition_name(self, name: str):
        self.name = name

        search_response = requests.get(
            self.search_url.format(self.name),
            headers=self.search_headers,
        ).content.decode()

        search_tree = etree.HTML(search_response)
        response_names = search_tree.xpath(
            '/html/body/div[2]/div[13]/div[3]/div/h3/a')
        response_urls = search_tree.xpath(
            '/html/body/div[2]/div[13]/div[3]/div/h3/a/@href')

        result = []
        index = 0
        for i in response_names:
            i = etree.tostring(i, xml_declaration=True,
                               encoding='utf-8').decode()
            name_search_result = re.search(r'>(.*?)</a>',i)
            name = name_search_result[1].replace('<em>', '').replace(
                '</em>', '') if name_search_result else '[no title]'
            search_list = re.search(r'href=\"(.*?)\"', i)
            url = search_list[1] if search_list else '[no url]'
            # print(index, name, url)
            print(
                f'    {index} - {name.replace("-", "").replace("_", "")} : {url}'
            )
            index += 1
            result.append((name, url))
        return result

    def parse_baidu_link_url(self, url):
        p = subprocess.Popen(f'php ./parse_baidu_link.php "{url}"',
                             shell=True,
                             stdout=subprocess.PIPE)
        stdout, stderr = p.communicate()
        if stdout:
            data = stdout.rstrip()
        else:
            data = None
        if stderr:
            err = stderr.rstrip()
        else:
            err = None
        return data, err, p.returncode

    def get_fiction_page(self, web_name: str, url: str):
        _url = self.parse_baidu_link_url(url)
        if _url[0]:
            _url = re.search(r'(http.*?)\"', _url[0].decode())[1]
            print(f'===> True url: {_url}')
            self.fiction_url = _url
        else:
            print("can't parse url, will quit.")
            exit(1)

        print('\nStart requset url', end='')
        resp = None
        for i in range(3):
            try:
                resp = self.get_response(_url, self.headers)
                print(' [ok]\n')
                print(type(resp))
                break
            except Exception as e:
                print(f'\rFaild, try {i + 1} time.', end='')
                time.sleep(10)
                continue
        if resp:
            return web_name, resp
        else:
            exit(1)

    def parse_page_get_donwload_url(self, name: str, resp):
        print(f'Parse page is {name}:')
        # resp = str(resp, encoding='utf-8')
        pprint.pprint(resp)

        if '键盘小说网' in name:
            resp = str(resp, encoding='utf-8')
            ret = re.findall(r'<a.*?onClick=\"(.*?)\".*?下载.*?</a>', resp, re.M)
            url = re.search(r"(http://.*?)\'", ret[0])[1]
            print(f'===> Got download url: {url}')
            return url
        elif '蚂蚁电子书' in name:
            resp = str(resp, encoding='utf-8')
            ret = re.findall(r'<a.*?href=\"(.*?)\".*?下载.*?</a>', resp, re.M)
            url = ret[0]
            print(f'===> Got download url: {url}')
            return url
        elif '纵横中文网' in name:
            print('The site not allowed download')
            exit(0)
        elif '笔下文学' in name:
            resp = str(resp)
            bookid = re.search(r'(bookid=\d+)', resp, re.M)[1]
            txtkey = re.search(r'(&txtkey=[a-z|0-9]+)', resp, re.M)[1]
            sourc_url = re.search(r'(http://.*?)\/', self.fiction_url)[1]
            # print(sourc_url, bookid, txtkey)
            url = ('http://m.bxwx666.org' + '/download.sapx?' + bookid +
                   txtkey)
            print(f'===> Got download url: {url}')
            return url
        else:

            pass
            exit(1)
        # # TODO: process logic not complete <20-10-20, yourname> #

    def downloader(self, url):
        print('\n Start download:')
        sum = 0
        resp_stream = requests.get(url, headers=self.headers, stream=True)
        total_size = int(resp_stream.headers['content-length'])
        with open(self.name + '.txt', 'wb') as f:
            for chunk in resp_stream.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    sum += len(chunk)
                    print('\r    downloaded: [{}{}] {}'.format(int(sum / total_size * 100) * '#',
                                                               int((1 - sum/total_size) * 100) * '*',
                                                               sum), end='')
        print("\nDownload over")

    def main(self):
        fiction_name = input('input you want to download fcition name:')
        r = self.search_by_fcition_name(fiction_name)
        _in = input('\nplease input the number:')
        if _in == 'q':
            exit(0)
        else:
            while True:
                try:
                    num = int(_in)
                    break
                except Exception as e:
                    continue
        name, resp = self.get_fiction_page(r[num][0], r[num][1])
        download_url = self.parse_page_get_donwload_url(name, resp)
        self.downloader(download_url)


if __name__ == '__main__':
    fd = FictionDownloader()
    fd.main()
