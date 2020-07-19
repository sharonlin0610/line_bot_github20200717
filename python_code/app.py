# coding: utf-8

# In[ ]:


"""
整體功能描述
"""

# In[ ]:


'''
Application 主架構
'''
# 載入json處理套件
import json

# 引用Web Server套件
from flask import Flask, request, abort, render_template, redirect, url_for
# 從linebot 套件包裡引用 LineBotApi 與 WebhookHandler 類別
from linebot import (
    LineBotApi, WebhookHandler
)
# 引用無效簽章錯誤
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import TemplateSendMessage, ButtonsTemplate, PostbackTemplateAction

import redis
from mysql_redis import *

# 載入基礎設定檔
secretFileContentJson = json.load(open("./line_secret_key", 'r', encoding='utf8'))
server_url = secretFileContentJson.get("server_url")

# 設定Server啟用細節
app = Flask(__name__, static_url_path="/素材", static_folder="./素材/")

# 設定變數 寫入資料庫mysql

user_id = ''
display_name = ''
uid = ''
household_key = 0

# 生成實體物件
line_bot_api = LineBotApi(secretFileContentJson.get("channel_access_token"))
handler = WebhookHandler(secretFileContentJson.get("secret_key"))


# 啟動server對外接口，使Line能丟消息進來
@app.route("/", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


# --------首頁--------
@app.route('/home')
def homepage():
    return render_template('home.html')


# --------登入--------
@app.route('/home/loginurl', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(uid, username, password)
        try:
            if login_check(uid, username, password):
                return redirect(url_for('success', username=request.form.get('username')))
        except:
            if login_check(uid, username, password):
                return redirect(url_for('success', username=request.form.get('username')))
        else:
            return '<center><h1>查無帳號，將導到註冊頁面....' \
                   '    <br>' \
                   '<meta http-equiv="refresh" content="5;url=https://smart-diamond.herokuapp.com/home/signon" />' \
                   '</h1></center>'
    return render_template('login.html')


# --------check --------
def login_check(checkuserid, username, password):
    """登入帳號密碼檢核"""
    # result
    result = check_mysql()
    if (checkuserid, username, password) in result:
        print("登入成功")
        return True
    else:
        print("登入失敗")
        return False


def check_mysql():
    redis_key = "check_mysql"
    sql_str = "SELECT user_id, account, password FROM line_smart"
    result = get_select(redis_key, sql_str, False)
    return result


@app.route('/home/loginurl/sucess/<username>', methods=['GET', 'POST'])
def success(username):
    return render_template('sucess.html', username=username)


#  PostbackTemplateAction 點擊選項後，
#  除了文字會顯示在聊天室中，
#  還回傳data中的資料，可
#  此類透過 Postback event 處理。
button_template_message = ButtonsTemplate(
    thumbnail_image_url="https://imgur.com/yBY9SKy.jpg",
    title='喚醒Smart！',
    text='點選喚醒並開始使用Smart！',
    ratio="1.51:1",
    image_size="cover",
    actions=[
        PostbackTemplateAction(
            label='叫醒Smart!!',
            text='smart甦醒，點選新的圖文選單！',
            data='menu=rich_menu_0'
        )
    ]
)

button_template_message1 = ButtonsTemplate(
    thumbnail_image_url="https://imgur.com/yBY9SKy.jpg",
    title='喚醒Smart！',
    text='點選喚醒並開始使用Smart！\n請點選圖文選單進行操作！',
    ratio="1.51:1",
    image_size="cover",
    actions=[
        PostbackTemplateAction(
            label='登入Smart!',
            text='登入Smart!',
            data='menu=rich_menu_0'
        )
    ]
)
button_template_message2 = ButtonsTemplate(
    thumbnail_image_url="https://imgur.com/xSvLikq.jpg",
    title='登入 /註冊 SMart',
    text='請點選下方進行互動式對答',
    ratio="1.51:1",
    image_size="cover",
    actions=[
        PostbackTemplateAction(
            label="我要登入SMart",
            text="登入SMart",
            data="folder=我要登入"
        ),
        PostbackTemplateAction(
            label='我要註冊SMart會員',
            text='註冊SMart',
            data='folder=註冊'
        ),
        PostbackTemplateAction(
            label='認識SMart',
            text='認識SMart',
            data='folder=探索'
        )
    ]
)


# --------註冊帳號密碼--------
@app.route('/home/signon', methods=['GET', 'POST'])
def getnewmember():
    if request.method == 'POST':
        new_name = request.form.get('newusername')
        new_password = request.form.get('newpassword')
        if login_check(uid, new_name, new_password) is False:
            if put_into_mysql(user_id, display_name, new_name, new_password):
                print('done')
                line_bot_api.push_message(uid,
                                          TemplateSendMessage(alt_text="test", template=button_template_message))
                return '<center><h1>註冊成功！系統跳轉中.....請稍等' \
                       '將導到首頁，用戶可關閉視窗繼續操作。' \
                       '    <br>' \
                       '<meta http-equiv="refresh" content="5;url=https://smart-diamond.herokuapp.com/home" />' \
                       '</h1></center>'
            else:
                return render_template('registrate.html')
        else:
            line_bot_api.push_message(uid,
                                      TemplateSendMessage(alt_text="confirm", template=button_template_message1))
            return '<center><h1>咦～使用者Line註冊過了唷！' \
                   '<br>可以直接關閉視窗點選登入!' \
                   '系統跳轉中.....請稍等' \
                   '<meta http-equiv="refresh" content="5;url=https://smart-diamond.herokuapp.com/home" />' \
                   '</h1></center>'
    return render_template('registrate.html')


# ----------會員註冊更新資料庫----------
def put_into_mysql(line_uid, display_nm, new_name, new_password):
    db, cursor = connect_sqldb()

    cursor.execute('INSERT INTO line_smart(user_id, display, account, password)' 'VALUES(%s, %s,%s, %s)',
                   (line_uid, display_nm, new_name, new_password))
    cursor.close()
    return True


# ----------會員歷史資料-----------
@app.route('/home/login/showdata')
def showdata():
    redis_key = "trans-history-" + str(household_key)
    sql_str = "SELECT date_time, household_key, product_chnm, product_price, total_qty " \
              + "FROM MemberImmediateTaking_KSQL_History WHERE household_key = {};".format(household_key)
    data = get_select(redis_key, sql_str, False)
    total_price = 0
    for a in data:
        total_price += int(a[3])
    return render_template("showhistory.html", username=display_name, value=data, total=total_price)


# -- ----------會員即時購物車--------------
@app.route('/home/login/showcar')
def showcar():
    redis_key = "trans-tmp-" + str(household_key)
    sql_str = "SELECT " \
              + "STR_TO_DATE(trans_date,'%Y%m%d%'), product_chnm, ROUND(total_qty,0) AS totalnumber, " \
              + "product_price, ROUND(total_price,0) " \
              + "FROM PStage.MemberImmediateTaking_KSQL " \
              + "WHERE household_key = {};".format(household_key)
    data = get_select(redis_key, sql_str, False)
    total_price = 0
    for a in data:
        total_price += int(a[4])
    return render_template("showcar.html", username=display_name, value=data, total=total_price)


# --------推薦商品--------
# 'product_recommendinfo )

@app.route('/home/login/SMartrecommendation')
def recommendation():
    sql_str = "SELECT product_chnm FROM PStage.MemberImmediateTaking_KSQL " \
              + "WHERE MemberImmediateTaking_KSQL.household_key = {};".format(household_key)
    redis_key = "trans-tmp-" + str(household_key)
    product = get_select(redis_key, sql_str, use_redis=False)
    product = [p[0] for p in product]
    data = ()
    if len(product) != 0:
        for p in product:
            redis_key = "recommendation-by-" + p
            sql_str = "SELECT product_name_A, product_name_B, recommendinfo FROM PStage.product_recommendinfo " \
                      + "WHERE product_recommendinfo.product_name_A = '{}' ".format(p) \
                      + "OR product_recommendinfo.product_name_B = '{}';".format(p)
            tmp = get_select(redis_key, sql_str)
            if tmp[0] in data:
                continue
            else:
                data = data + tmp
    else:
        pass
    return render_template("itemrecommendation.html", username=display_name, value=data)


# --------個人推薦--------
# "Diamod 抓 USERID 抓五個 product_recommendinfo 目前三個 只顯示最右邊訊息 寫一個fun 如果有oreo 及件)

@app.route('/home/login/pseronalcars')  # #####################
def personal_recommend():
    season = "Fall"
    sql_str = "SELECT PRODUCT " \
              + "FROM PStage.Diamond_Recommend_Result " \
              + "WHERE USERID = {} AND Season ='{}';".format(household_key, season)
    redis_key = "personal-recommendation-" + str(household_key) + "-" + season
    data = get_select(redis_key, sql_str)

    return render_template("recommendation.html", username=display_name, value=data)


# --------個人QR code--------
@app.route('/home/login/qrcode')
def personal_qr_code():
    redis_key = "QR-code-" + str(household_key)
    sql_str = "SELECT QR_code FROM PStage.line_smart WHERE PStage.line_smart.user_id ='{}';".format(uid)
    data = get_select(redis_key, sql_str)
    if data == ():
        return '<h1>請會員稍等幾天，系統在認證已形成QR code! 謝謝您的諒解與體諒！</h1>'
    else:
        return render_template("qrcode.html", username=display_name, picurl=data)


# In[ ]:


'''
消息判斷器
讀取指定的json檔案後，把json解析成不同格式的SendMessage
讀取檔案，
把內容轉換成json
將json轉換成消息
放回array中，並把array傳出。
'''

# 引用會用到的套件
from linebot.models import (
    ImagemapSendMessage, TextSendMessage, ImageSendMessage, LocationSendMessage, FlexSendMessage,
    VideoSendMessage, StickerSendMessage, AudioSendMessage
)

from linebot.models.template import *
from linebot.models import *


def detect_json_array_to_new_message_array(file_name):
    # 開啟檔案，轉成json
    with open(file_name) as f:
        json_array = json.load(f)

    # 解析json
    return_array = []
    for jsonObject in json_array:

        # 讀取其用來判斷的元件
        message_type = jsonObject.get('type')

        # 轉換
        if message_type == 'text':
            return_array.append(TextSendMessage.new_from_json_dict(jsonObject))
        elif message_type == 'imagemap':
            return_array.append(ImagemapSendMessage.new_from_json_dict(jsonObject))
        elif message_type == 'template':
            return_array.append(TemplateSendMessage.new_from_json_dict(jsonObject))
        elif message_type == 'image':
            return_array.append(ImageSendMessage.new_from_json_dict(jsonObject))
        elif message_type == 'sticker':
            return_array.append(StickerSendMessage.new_from_json_dict(jsonObject))
        elif message_type == 'audio':
            return_array.append(AudioSendMessage.new_from_json_dict(jsonObject))
        elif message_type == 'location':
            return_array.append(LocationSendMessage.new_from_json_dict(jsonObject))
        elif message_type == 'flex':
            return_array.append(FlexSendMessage.new_from_json_dict(jsonObject))
        elif message_type == 'video':
            return_array.append(VideoSendMessage.new_from_json_dict(jsonObject))

            # 回傳
    return return_array


# In[ ]:


'''
handler處理關注消息
用戶關注時，讀取 素材 -> 關注 -> reply.json
將其轉換成可寄發的消息，傳回給Line
'''

# 引用套件
from linebot.models import (
    FollowEvent
)


# 關注事件處理
@handler.add(FollowEvent)
def process_follow_event(event):
    # 取出消息內User的資料
    profile = line_bot_api.get_profile(event.source.user_id)
    print(profile)

    # 取出userid, displayname 丟回全域變數
    profile_dic = vars(profile)
    global user_id, display_name
    display_name = profile_dic.get('display_name')
    user_id = profile_dic.get('user_id')

    # 讀取並轉換
    reply_json_path = "素材/關注/reply.json"
    result_message_array = detect_json_array_to_new_message_array(reply_json_path)

    # 消息發送
    line_bot_api.reply_message(
        event.reply_token,
        result_message_array
    )


# In[ ]:


def show_user_info(line_uid):

    redis_key = "user-info-" + line_uid
    sql_str = "SELECT account, password FROM line_smart WHERE user_id = '{}';".format(line_uid)
    result = get_select(redis_key, sql_str)[0]
    return result




def uid_to_household_key(line_uid):
    sql_str = "SELECT household_key FROM line_smart WHERE user_id = '{}';".format(line_uid)
    redis_key = "household_key-" + line_uid
    result = get_select(redis_key, sql_str)[0][0]
    return result


'''
handler處理文字消息
收到用戶回應的文字消息，
按文字消息內容，往素材資料夾中，找尋以該內容命名的資料夾，讀取裡面的reply.json
轉譯json後，將消息回傳給用戶
'''

# 引用套件
from linebot.models import (
    MessageEvent, TextMessage
)


# 文字消息處理
@handler.add(MessageEvent, message=TextMessage)
def process_text_message(event):
    msg = event.message.text
    # 取出消息內User的資料
    profile = line_bot_api.get_profile(event.source.user_id)
    print(profile)

    # 取出userid, displayname 丟回全域變數
    profile_dic = vars(profile)

    # 取出uid, display_name 丟回全域變數
    profile_dic = vars(profile)
    global uid, display_name, household_key
    display_name = profile_dic.get('display_name')
    uid = profile_dic.get('user_id')
    household_key = uid_to_household_key(uid)

    if msg == "你好" or msg == "哈嘍":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="你好～歡迎加入SMart! 請多多使用圖形選單唷！"))
    elif msg in ('查詢付費', '流程', '結帳', '註冊', '查詢'):
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請點選選點'關於APP'"))
    elif msg == '已經申請了':
        result = show_user_info(uid)
        print(result)
        if result is None:
            line_bot_api.reply_message(event.reply_token, [TextSendMessage(text="找不到會員，請再試一次，或點選我要註冊SMart會員"),
                                                           TemplateSendMessage(alt_text="confirm",
                                                                               template=button_template_message2)])
        else:
            line_bot_api.reply_message(event.reply_token,
                                       [TextSendMessage(text='登入成功,您的帳號是 {}, 密碼是 {} '.format(result[0], result[1])),
                                        TemplateSendMessage(alt_text="confirm", template=button_template_message1)])
            # line_bot_api.reply_message(event.reply_token, TextSendMessage(
            #     text='登入成功,您的帳號是 {}, 密碼是 {} '.format(result[0], result[1])))
    else:
        pass

        # 讀取本地檔案，並轉譯成消息
    reply_json_path = "素材/" + event.message.text + "/reply.json"
    result_message_array = detect_json_array_to_new_message_array(reply_json_path)

    # 發送
    line_bot_api.reply_message(
        event.reply_token,
        result_message_array
    )


# In[ ]:


'''
handler處理Postback Event
載入功能選單與啟動特殊功能
解析postback的data，並按照data欄位判斷處理
現有三個欄位
menu, folder, tag
若folder欄位有值，則
    讀取其reply.json，轉譯成消息，並發送
若menu欄位有值，則
    讀取其rich_menu_id，並取得用戶id，將用戶與選單綁定
    讀取其reply.json，轉譯成消息，並發送
'''
from linebot.models import (
    PostbackEvent
)

from urllib.parse import parse_qs


@handler.add(PostbackEvent)
def process_postback_event(event):
    query_string_dict = parse_qs(event.postback.data)

    print(query_string_dict)
    if 'folder' in query_string_dict:
        reply_json_path = '素材/' + query_string_dict.get('folder')[0] + "/reply.json"
        result_message_array = detect_json_array_to_new_message_array(reply_json_path)

        line_bot_api.reply_message(
            event.reply_token,
            result_message_array
        )
    elif 'menu' in query_string_dict:

        link_rich_menu_id = open("素材/" + query_string_dict.get('menu')[0] + '/rich_menu_id', 'r').read()
        line_bot_api.link_rich_menu_to_user(event.source.user_id, link_rich_menu_id)

        reply_json_path = '素材/' + query_string_dict.get('menu')[0] + "/reply.json"
        result_message_array = detect_json_array_to_new_message_array(reply_json_path)

        line_bot_api.reply_message(
            event.reply_token,
            result_message_array
        )


# In[ ]:


'''
Application 運行（開發版）
'''
# if __name__ == "__main__":
#     app.run(host='0.0.0.0')


# In[ ]:


'''
Application 運行（heroku版）
'''

import os

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=os.environ['PORT'])
