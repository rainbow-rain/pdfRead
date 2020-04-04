import pdfplumber
import os
from tqdm import tqdm
import pandas as pd

columnsTitle = ['股票代码', '年份', '经营情况讨论与分析', '开始页', '终止页', '总字数', '总句子数']
sentence_signs = ['。', '！', '？', '!', '?']
pd.DataFrame(columns=columnsTitle).to_csv("text.csv", index=False)

def walkFile(root):
	dirs = os.listdir(root)
	return dirs

def csvWriter(dataForm):
	dataframe = pd.DataFrame(dataForm, columns = columnsTitle)
	dataframe.to_csv("text.csv", mode='a', index=False, header=False, sep=',')

# 每一页正文范围
def pageContentRange(pageText):
	firstEnter = pageText.find('\n')  # 第一个\n
	# 查找page开始位置
	if pageText.find("年度报告", 0, firstEnter) or pageText.find("经营情况讨论与分析", 0, firstEnter):
		pageStartIndex = firstEnter+1

	# 查找页码位置
	numberIndex = pageText.rfind('\n', -20)
	return pageStartIndex, numberIndex

# 文件名处理
def extractSocksYear(file):
	fileName = (file.split('.')[0]).split('_',1)
	fileName = list(map(str, fileName))
	# print(fileName)
	try:
		sockName = fileName[0]+'\t'
		year = fileName[1][:4]
		# print(sockName, " ", year)
		# input()
		return sockName, year
	except:
		print(file, "文件名不合规范!")
	

def getTotalSentenceWords(pageContent):
	totalWords = 0
	totalSentence = 0
	for sign in sentence_signs:
			totalSentence += pageContent.count(sign)

	totalWords = len(pageContent)
	return totalSentence, totalWords

def readFile(path):
	# pdf: 第一节：27
	with pdfplumber.open(path) as pdf:
		# print(len(pdf.pages))
		# print((pdf.pages[17].extract_text())[-10:-5], "***")
		# print(pdf.pages[17].extract_words())
		
		pos1 = 0
		pos2 = 0
		flag = 0
		pageContent = ""
		
		for page in pdf.pages:
			# print("-------第[%d]页-------" % page.page_number)
			# print(page.extract_text())
			
			pageNumber = page.page_number
			pageText = page.extract_text()

			if not pageText:
				continue

			pageStartIndex, numberIndex = pageContentRange(pageText)

			textStr = pageText[:80]
			#for character in :
			#	textStr += character['text']

			# print(textStr,"****")
			pageStart = textStr.find("经营情况讨论与分析")
			if flag == 0 and pageStart != -1:
				# print(textStr)
				pos1 = pageNumber
				firstPageStart = pageStart+9
				flag = 1
			elif flag == 1 and textStr.find("重要事项") != -1:
				pos2 = pageNumber
				break

			if flag:
				if pageText:
					if pageNumber == pos1:
						pageStartIndex = firstPageStart
					if pageStartIndex < numberIndex:
						pageContent += pageText[pageStartIndex:numberIndex]
						# print(pageStartIndex, "*********", pageText[pageStartIndex:numberIndex])
	# print(pos1," ",pos2)
	return pos1, pos2, pageContent

def cnt_func(root):
	files = walkFile(root)
	
	fileLen = len(files)

	fileStart = 0
	fileEnd = 50

	while fileStart < fileLen:
		if fileEnd > fileLen:
			fileEnd = fileLen

		dataForm = []
		for file in tqdm(files[fileStart:fileEnd]):
			path = os.path.join(root, file)
			# print(path)

			pos1, pos2, pageContent = readFile(path)
			
				
			totalSentence, totalWords = getTotalSentenceWords(pageContent)

			sockName,year = extractSocksYear(file)

			dataForm.append([sockName, year, pageContent, pos1, pos2-1, totalWords, totalSentence])
			# print(dataForm)


		# print(dataForm)
		csvWriter(dataForm)
		# first_page = pdf.pages[1]
		# print(first_page.chars[-2])
		# print(first_page.chars[27])
		fileStart = fileEnd
		fileEnd += 50


def main():
	root = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'pdf')
	cnt_func(root)
	

if __name__ == '__main__':
	main()
