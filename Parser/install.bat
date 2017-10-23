@echo off
chcp 1251>nul
@echo off > input.txt
echo 1193 > org.txt
echo 5 > hirsch.txt
python-3.6.1-amd64.exe
pip install requests
pip install bs4
pip install BeautifulSoup4
pip install xlwt