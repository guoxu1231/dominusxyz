__author__ = 'shawguo'

import sys
import string
import requests


class WifiPost:
    """
        install required module: requests:
            sudo -i
            exprot <http/https proxy>
            easy_install requests
    """

    def __init__(self):
        pass

    """
        usage: python2.7 get_wifi_password.py <sso_username> <password>
    """

    @staticmethod
    def get_wifi_password():

        if not len(sys.argv) == 3:
            print "Script Usage: python2.7 get_wifi_password.py <sso_username> <password>"
            return

        print "Script Parameters: %s %s" % (sys.argv[1], '\n')

        # post form sso/auth_cred_submit
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)' \
                          'Chrome/41.0.2272.89 Safari/537.36',
            'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'login.oracle.com',
            'Origin': 'https://login.oracle.com',
            'Referer': 'https://login.oracle.com/mysso/signon.jsp'
        }

        payload = {'v': 'v1.4',
                   'request_id': '-3507582284120941298',
                   'OAM_REQ': 'VERSION_4~bAOlSSvItMYRm%2fGmwDXakrTm0htlAu3BKRAYkldrC8E4hQhVWCZq7mmt6MBb9nYlY397247vuCdht1OKEwG%2fa%2fZ%2b2hd' \
                              'xAb75PkXh%2bzy%2foPFJzBs3iRLTFwSgOklw7JXctVF9yQcIBhcQ%2fAqfJTp1R57P2eKzsy6%2biGH6zV3a7cqxSnrE49Yd%2f2DUszFC2PE%2b2UK%2fb' \
                              'yhPBD5WiWH1k9Cr1%2b1VTiFlh35DQoUkSj%2byIJdFz4cR29XZDYahaxen7m5CRJN5gbb8L%2feweMvOLBt%2bXQATy5XISmuRLUa2L6rcrUp7RyJTtZLjxEHk' \
                              '%2fMRXi53fdckuBLlhpDdXJ%2bFrWfIGwoAa6qGRbcy5%2fsUR0T49piZSdlBWjn1DkdSQzsrxnuYGHno%2fPUGiLqqkkx87ZhrdS9i2gIG%2bepo%2fsKzZjPKT' \
                              '8yO0lYnKVYuXIM7Lre8YI6jiKfUDYax7dZ7ByxjzNpphfkgvalwAMXKITEHliOVMGBBYaykjZQLjAH5OMU3j%2bssnlHNCnvPMvF6T46i1Mhk1C0udbbXuF4oxTW' \
                              '16zTCBpwLVDLJatoJpxF6rAIxaZa5I90czFnLPEfv2DeqULrPh1bMMgB6zNnl8u9TbZsBtohxj4ASFw%2bKamvqPVnWc%2bL9D5JbT%2fa6mql6e1NAflWhtokP8k' \
                              'hQR2koaItTrX%2bN0FRcsjEV8xG%2b75Z6zxcaRgxzOOI8TnPfY1FzpD6NfeJBpPO5%2fm36xVk4mHg8F2kGAIaUKUvHFT48ZlICE6yTUSubHCaGcm50H7reyOoDN7l' \
                              'G9GNwSkhMLSlZl3Z%2fQvTNgjPY52xnJZAZBqi7sm6tEP0jusZ7hkxQ3nqQU2afC9mtqi5f2zQp87qScBwhtgjKEt7%2fFgyjHrsBvp1UMurCLbI%2fqyP%2fGYxukSIQ' \
                              'wUOmL%2bLjM%2f%2bKuq04T2tcVo%2fJ%2fMRBBvsBBSs3x0bK2P%2fn8%2ffECFSipxs0VoqE%2bdGdLVxjMfwmBD1gGDtVpeqKU6Kj1YyfY%2bdye0KcMHj%2b68ZJI%' \
                              '2fXnJvyqlyPuosje31MFz3Eu5GiUAXQOpLKVChvK7LBRqLw47OPlFcaaaEBjPPCqSGYjQ3d4gdetFxHU3THxgLeob33d06jsqPyhx%2fagrpZ2mHREP8GXuC5iLzeL8%2' \
                              'bjq8wqnj%2flSd0SPdXzUpi2KiIHNmzBdCmGE7u2WNulSQOVw7sBXh0HKQ7gTEzFa2VRD7ZdgmLJ0zUw5mwmS7O%2fthRyGh0DShdXj8VF12W95is4%2bkhdq%2fYeP0cgNB' \
                              '7PTOjWY7CYpy3dk%2fNHMzPceU7%2fJV5amrIJYvzXU0x3MpsEV5mx%2fwjWZuS8GzopL03iPtbP7iqBLSW9DiYn3RvWR2ckGE%2foauBUCm%2bqCQ2KLKt063yUjNPozB45cw' \
                              'lMAo%2fiJn9w5lswRglkELVo%2fBBgy9Px%2bDTgp2zcb8rGNsvRLpszuj%2fRcENmyhtjXayhFZ%2ffJH%2bpIZohI7mNJUekli1FCObC7rkihAGywWL%2fmo89l11GoBzEZig' \
                              'gpu7gcnedB09Yc%2baqmiqMlrEgixFkQ0I%2br6H5QcEx16lxJULrOIvUMAXe7wV4VNLGVipgYs282umft%2f3dlAWviV4OUW9uCsdNmO2dniSOqicXzk%2fJ13m9DWeX5TcnkF' \
                              '1nC%2f4zX%2f8A6l3O1HEVKIIcp31dIU56bVuFyfL7WZRpMP4sxx5fRgnBnt75Pv6IhmW%2bt%2bTeDLj09BrbMCx2zefGMvMHinLjxHBQqr0Wl9%2fZ6u5PKsn2oDnNaHKhlx5' \
                              's0c3g7w97ZQg%2frTvQMfIykkdJ9XF6KjVbzMa%2fmXUMM6z0LrD7fNKulID1Qa3ytmASGZYNuk3w4%3d',
                   'site2pstoretoken': 'v1.4~7A14C962~6A81D4828A66A8FAB5E72C8C7AC6D89A152203F16B05BC6449E2E7D276133F6348511CC2A6A06AE828233AFB7B6A3128245A3A14ED8DB84AB' \
                                       'F0809AC04FB392E2E781AEEE587644772E7114D4A97115C49C8E7DFFAD5E21EA602670F06CA3F7E1914C3B22648E22C99345D2F6B614ADD7F8A480F9120F3B155D3256DC8081262AABE83C' \
                                       '652A37ACD6D90451D30726449731FEC0D6FC650932260F148C3F0DDEA7346EDF42275E0C8F928AD7A6854CA65F1FECD932376469A63E34292A4CC37BF664C227138E0BB66',
                   'ssousername': sys.argv[1],
                   'password': sys.argv[2]
        }
        # redirect to osso_login_success
        r = requests.post("https://login.oracle.com/oam/server/sso/auth_cred_submit", data=payload, headers=headers,
                          allow_redirects=True)
        print r.url + "\n"
        # redirect to captcha/files/airespace_pwd_apac.txt
        r = requests.get(r.url)
        print r.url + "\n"

        if 'captcha/files/airespace_pwd_apac.txt' in r.url:  # successful redirect

            for line in string.split(r.text, '\n'):  # extract password from response
                if 'Password:' in line:
                    password = string.strip(string.lstrip(line, 'Password:'))
                    print "Wifi Password:%s%s" % (password, '\n')

            print r.text

            # write to /tmp/intranet_wifi.txt
            open('/tmp/intranet_wifi.txt','w').write(password)
            return password

        else:
            print 'Error'


def main():
    return WifiPost.get_wifi_password()

    # longStr = "This is a very long string " \
    # "that I wrote to help somebody " \
    # "who had a question about " \
    # "writing long strings in Python"
    # d = 'hell'
    # print longStr


if __name__ == "__main__":
    main()