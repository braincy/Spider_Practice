from selenium import webdriver
from lxml import html
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.header import Header
from smtplib import SMTP_SSL
from datetime import timedelta, datetime
import time
import xlwt
import xlrd


class Monitor(object):
    def __init__(self):
        self.browser = webdriver.Chrome('/Users/rain/Desktop/chromedriver')
        self.app_book = xlwt.Workbook(encoding='utf-8', style_compression=0)
        self.app_sheet = self.app_book.add_sheet('application', cell_overwrite_ok=True)
        self.game_book = xlwt.Workbook(encoding='utf-8', style_compression=0)
        self.game_sheet = self.game_book.add_sheet('game', cell_overwrite_ok=True)
        self.app_rank = self.get_application_data()
        self.game_rank = self.get_game_data()

    def get_application_data(self):
        yesterday = datetime.today() + timedelta(-1)
        excel_data = xlrd.open_workbook('app_list_' + yesterday.strftime('%Y%m%d') + '.xls')
        sheet = excel_data.sheets()[0]
        rank = dict()
        for i in range(1, 101):
            rank[sheet.cell(i, 0).value] = i
        return rank

    def get_game_data(self):
        yesterday = datetime.today() + timedelta(-1)
        excel_data = xlrd.open_workbook('game_list_' + yesterday.strftime('%Y%m%d') + '.xls')
        sheet = excel_data.sheets()[0]
        rank = dict()
        for i in range(1, 101):
            rank[sheet.cell(i, 0).value] = i
        return rank

    def start_requests(self):
        # 应用榜单
        self.browser.get('https://www.qimai.cn/rank/index/brand/free/device/iphone/country/cn/genre/5000')
        time.sleep(10)
        self.parse(self.browser.page_source, 'application')
        # 游戏榜单
        self.browser.get('https://www.qimai.cn/rank/index/brand/free/device/iphone/country/cn/genre/6014')
        time.sleep(10)
        self.parse(self.browser.page_source, 'game')
        self.browser.quit()

    def send_email(self, list_type):
        host_server = 'smtp.163.com'
        pwd = '' # 发送邮箱密码
        sender_mail = 'lca1826@163.com' # 发送邮箱
        receiver = '' # 接收邮箱
        if list_type == 'application':
            filename = 'app_list_' + time.strftime("%Y%m%d", time.localtime()) + '.xls'
            mail_title = '应用榜单数据' + time.strftime("%Y%m%d", time.localtime())
        else:
            filename = 'game_list_' + time.strftime("%Y%m%d", time.localtime()) + '.xls'
            mail_title = '游戏榜单数据' + time.strftime("%Y%m%d", time.localtime())
        msg = MIMEMultipart('mixed')
        msg["Subject"] = Header(mail_title, 'utf-8')
        msg["From"] = sender_mail
        msg["To"] = receiver
        xlsxpart = MIMEApplication(open(filename, 'rb').read())
        xlsxpart.add_header('Content-Disposition', 'attachment', filename=filename)
        msg.attach(xlsxpart)
        smtp = SMTP_SSL(host_server)
        smtp.ehlo(host_server)
        smtp.login(sender_mail, pwd)
        smtp.sendmail(sender_mail, receiver, msg.as_string())
        smtp.quit()

    def parse(self, content, list_type):
        tree = html.fromstring(content)
        element = tree.xpath('//*[@id="rank-top-list"]/div[2]/table/tbody/tr')[0]
        name_list = [el.strip() for el in element.xpath('//td[2]/div/div/a/text()')]
        category_list = element.xpath('//td[5]/div/div/p[2]/text()')
        url_list = ['https://www.qimai.cn' + el for el in element.xpath('//td[2]/div/a/@href')]
        company_list = element.xpath('//td[8]/p/text()|//td[8]/a/text()')
        icon_list = [el.attrib['src'] for el in element.xpath('//td[2]/div/a/img')]
        time_list = element.xpath('//td[7]/div/text()')
        if list_type == 'application':
            self.app_sheet.write(0, 0, '应用名称')
            self.app_sheet.write(0, 1, '应用图标')
            self.app_sheet.write(0, 2, '应用子分类')
            self.app_sheet.write(0, 3, '公司名称')
            self.app_sheet.write(0, 4, '发布时间')
            self.app_sheet.write(0, 5, '详情页地址')
            self.app_sheet.write(0, 6, '前一天排名')
            self.app_sheet.write(0, 7, '当天排名')
            self.app_sheet.write(0, 8, '排名变化的位数')
        elif list_type == 'game':
            self.game_sheet.write(0, 0, '游戏名称')
            self.game_sheet.write(0, 1, '游戏图标')
            self.game_sheet.write(0, 2, '游戏子分类')
            self.game_sheet.write(0, 3, '公司名称')
            self.game_sheet.write(0, 4, '发布时间')
            self.game_sheet.write(0, 5, '详情页地址')
            self.game_sheet.write(0, 6, '前一天排名')
            self.game_sheet.write(0, 7, '当天排名')
            self.game_sheet.write(0, 8, '排名变化的位数')
        for i in range(0, 100):
            if list_type == 'application':
                self.app_sheet.write(i + 1, 0, name_list[i])
                self.app_sheet.write(i + 1, 1, icon_list[i])
                self.app_sheet.write(i + 1, 2, category_list[i])
                self.app_sheet.write(i + 1, 3, company_list[i])
                self.app_sheet.write(i + 1, 4, time_list[i])
                self.app_sheet.write(i + 1, 5, url_list[i])
                if name_list[i] in self.app_rank:
                    self.app_sheet.write(i + 1, 6, self.app_rank[name_list[i]])
                    self.app_sheet.write(i + 1, 7, i + 1)
                    self.app_sheet.write(i + 1, 8, i + 1 - self.app_rank[name_list[i]])
                else:
                    self.app_sheet.write(i + 1, 6, '--')
                    self.app_sheet.write(i + 1, 7, '--')
                    self.app_sheet.write(i + 1, 8, '--')
            elif list_type == 'game':
                self.game_sheet.write(i + 1, 0, name_list[i])
                self.game_sheet.write(i + 1, 1, icon_list[i])
                self.game_sheet.write(i + 1, 2, category_list[i])
                self.game_sheet.write(i + 1, 3, company_list[i])
                self.game_sheet.write(i + 1, 4, time_list[i])
                self.game_sheet.write(i + 1, 5, url_list[i])
                if name_list[i] in self.game_rank:
                    self.game_sheet.write(i + 1, 6, self.game_rank[name_list[i]])
                    self.game_sheet.write(i + 1, 7, i + 1)
                    self.game_sheet.write(i + 1, 8, i + 1 - self.game_rank[name_list[i]])
                else:
                    self.game_sheet.write(i + 1, 6, '--')
                    self.game_sheet.write(i + 1, 7, '--')
                    self.game_sheet.write(i + 1, 8, '--')
        if list_type == 'application':
            self.app_book.save('app_list_' + time.strftime("%Y%m%d", time.localtime()) + '.xls')
            self.send_email('application')
        elif list_type == 'game':
            self.game_book.save('game_list_'+time.strftime("%Y%m%d", time.localtime())+'.xls')
            self.send_email('game')
        print('crawl', list_type, 'success')


if __name__ == '__main__':
    monitor = Monitor()
    monitor.start_requests()
