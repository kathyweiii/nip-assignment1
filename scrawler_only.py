import requests
from bs4 import BeautifulSoup
import time
import streamlit as st
from snownlp import SnowNLP


def get_title(date, asked_number, asked_push_num = 0):
    url = '/bbs/Gossiping/index.html'
    page_data = []
    n = 0

    while(n < asked_number):
        r = requests.get(str('https://www.ptt.cc'+url), cookies={'over18':'1'})
        soup = BeautifulSoup(r.text,"html.parser")

        # 取得上一頁的url
        page_div = soup.find('div','btn-group btn-group-paging')
        prev_url = page_div.find_all('a')[1]['href']
        
        div_rent = soup.find_all('div', 'r-ent')   

        for d in div_rent:
            if(n<asked_number):
                if d.find('a'):
                    # date_in_date = d.find('div','date').text.strip() == date
                    # print(date_in_date)
                    # if date_in_date: #只取url那頁的那天的文章
                    title = d.find('a').get_text()
                    date = d.find('div','date').text.strip()

                    push_count = d.find('div', 'nrec').text
                    push_num = 0
                    if push_count: # 確認有推文數
                        try:
                            push_num = int(push_count)
                        except ValueError:
                            # 若轉換失敗，可能是'爆'或 'X1', 'X2', ...
                            # 若不是, 不做任何事，push_num 保持為 0
                            if push_count == '爆':
                                push_num = 00
                            elif push_count.startswith('X'):
                                push_num = 99

                    if(push_num > asked_push_num):
                        page_data.append(
                            title
                            # 'date': date,
                            # 'push_num': push_num
                        )
                        n += 1

        url = prev_url 

    return page_data
            
# if __name__ == '__main__':

today = time.strftime("%m/%d").lstrip('0')

st.title('PTT 八卦版 貼文數搜尋引擎') 
# menu = ['Sentiment Analysis', 'NLP Pipeline']
# choice = st.sidebar.selectbox('Menu', menu)


st.write('可以得知最新的文章心情！')

with st.form(key='nlpForm'):
    asked_num =  st.slider('欲搜尋之篇數', 0, 100, 5,5)
    asked_push_num = st.slider('只顯示多少推文數以上之文章',0 ,99, 10,10)
    
    submit_button = st.form_submit_button(label='Analyze')

    if submit_button:
        with st.spinner('Wait for it...'):
            titles = get_title(today, asked_num, asked_push_num)
            values = []
            for t in titles:
                values.append(SnowNLP(t).sentiments)
            ave = sum(values) / len(titles)
        st.success('Done!')
        # st.info('Result')
        st.write('平均情感分數 = {:.2f}'.format(ave))
        if ave > 0.6:
            st.markdown('ptt最近是正向的 :smiley: ')
            st.balloons()
        elif (ave > 0.4) and (ave <= 0.6):
            st.markdown('ptt最近是中立 😐 ')
        else: 
            st.markdown('ptt最近是負面的 :angry: ')
            st.snow()
        for i in range(len(titles)):
            st.write('{} : sentiment={:.2f}'.format(titles[i], values[i]))


    
    # print(get_title(today,30,5))
    # print("\n")
    # print(len(get_pageinfo(today, 30,5)))