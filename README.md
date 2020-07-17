下載完，docker 啟動，並下載設定相關檔案，即可以操作屬於自己的Line_chatbot

[1,2,3,4,5 步驟同一個 開啟ngrok後，在開啟一夜終端機]

1. git clone {輸入github下載端} 
   

2. 用外部網頁打開 linux ip :8887 打開代表有通 

   然後，請自行在line_secret_key檔案 輸入自己的line_channel key (channel, user, token) 有三個

   最後一行伺服器還不用輸入。

3. 接著請下載Linux 版本的 （在VM 打開網頁 輸入ngrok Linux download 下載Linux版本)

	這時候下載會的得到 {connect your account} 的一長串碼 請複製，接下來會需要。

4. cd 到下載的ngrok 目錄， 然後 unzip ngrok-stable-linux-amd64.zip，出現ngrok 

	複製到python_code裡面 cp ngrok /home/user1/line_bot_github20200717/python_code

5. 切換到主目錄 cd /home/user1/line_bot_github20200717/python_code剛剛得到的 	

	 {connect your account} 的一長串碼 請複製 ./ngrok authtoken {放這裡}

	 會登入成功，接著要切換時區已打通通道（可做可不做，建議做，因為有時候ngrok會不穩）

	 ./ngrok http 5000 -region au

	 啟動後請複製 https://xxxxxxxxxxx.au.ngrok.io (https那行，更改到line_secert_key檔的最後一行) 請留 xxxxxxxxxxx.au.ngrok.io 複製過去就好

	 最後會變這樣
	 {         
		  "channel_access_token":"自己linebot的channel_access_token",
		  "secret_key":"自己linebot的secret_key",
		  "self_user_id":"自己linebot的self_user_id",
		  "rich_menu_id":["","",""],
		  "server_url":"xxxxxxxxxxx.au.ngrok.io"   
	 }

	#rich_menu_id 另外用

	# line-bot 網頁 webhood 請輸入完整的 https://xxxxxxxxxxx.au.ngrok.io/ （不用加callback)

[新的終端機]

6. docker-compose up -d 啟動docker

7. docker exec -it python bash 進入python 容器裡  (使用網頁版jupyter更改比較快)

8. vim app.py 最後一行駐解掉 heroku   打開ngrok的 
	Application 運行（開發版）

	'''
	if __name__ == "__main__":
    	app.run(host='0.0.0.0')

    儲存 exit

9.  docker-compose down 關閉容器

10. 再啟動  docker-compose up -d

	 
11.	進入python container > docker exec -it python bash

	cat app.py 查看app.py cat app.py 有沒有更新 
	沒有的話，請 docker-compose restart 重試

12. 在終端機 輸入 python app.py (執行執行檔) (容器裡進行)
