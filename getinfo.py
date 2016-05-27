#encoding=utf-8
'''
@这个工具爬取天津大学学生在图书馆的借阅记录
'''
import sys
import urllib
import urllib2
import cookielib
import re
from bs4 import BeautifulSoup

def saveToFile(stuID):
	fileName = 'cookie.txt'
	toFile = open("finalData_1.txt","a+")
	cookie = cookielib.MozillaCookieJar(fileName)
	opener= urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))

	# 登陆并获得cookie，用来稍后去访问借阅历史页面
	loginPost = {
		'rdid':str(stuID),
		'rdPasswd':'670b14728ad9902aecba32e22fa4f6bd'
	}
	loginPost = urllib.urlencode(loginPost)
	loginURL = "http://opac.lib.tju.edu.cn/opac/reader/doLogin"
	result = opener.open(loginURL, loginPost)
	table = BeautifulSoup(result.read(),"html.parser").table
	info = table.find_all('td')
	name = info[1].find('font')
	name = name.get_text()
	print name
	cookie.save(ignore_discard=True, ignore_expires=True)

	# 找到借书记录的总页数 pages
	historyURL = 'http://opac.lib.tju.edu.cn/opac/loan/historyLoanList'
	result = opener.open(historyURL)
	patternMenu = re.compile('<div class="meneame".*?<span.*?<span class="disabled">(.*?)</span>',re.S)
	searchResult = re.search(patternMenu, result.read())
	if searchResult is None:
		return
	pages = searchResult.group(1).strip().decode('utf8')
	patternGetInt = re.compile(' (.*?) ',re.S)
	pages = re.search(patternGetInt, pages)
	pages = int(pages.group(1).strip())
	print pages,"pages"
	# 表格的每一行
	patternTr = re.compile('<tr>(.*?)</tr>',re.S)
	# 每一行的内容
	patternTdCon = re.compile('<td.*?>(.*?)</td>')
	for curPage in range(1,pages+1):
		# params 的内容用来翻页
		params = {
		'page':str(curPage),
		'rows':'10',
		'prevPage':'1',
		'hasNextPage':'true',
		'searchType':'title',
		'searchValue':'',
		'orderBy':'',
		'classno':'',
		'libcode':'',
		'batchno':'',
		'classNoName':'',
		'language':'',
		'state':'',
		'specificLibcode':'',
		'specificClassno':'',
		'starttime':'',
		'endtime':'',
		'type':'',
		'limitDays':''
		}
		params = urllib.urlencode(params)
		result = opener.open(historyURL,params)
		soup = BeautifulSoup(result.read(),"html.parser")
		# content = soup.findAll('table', class='contentTable')
		
		trs = soup.findAll('tr')
		trs = list(trs)
		del trs[0]

		for item in trs:
			tds = item.find_all('td')
			print '\n'
			print stuID
			# 内容存储
			toFile.write(str(stuID))
			toFile.write('\t')

			for itemTDS in tds:
				con = itemTDS.get_text()
				print con
				toFile.write(con)
				toFile.write('\t')
			
			toFile.write('\n')

if __name__=="__main__":
	reload(sys)
	sys.setdefaultencoding('utf-8')
	#stuIDStatus.txt文件中记录了借阅证号
	idfile = open("stuIDStatus.txt","r")
	data = idfile.readlines()
	for item in data:
		print int(item)
		saveToFile(int(item))
