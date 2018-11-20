#### 比较简单的一个爬虫，涉及的内容不多，适合初学者 

- code.jpg 登陆时的验证码，登陆时自动会show
- spider.py 爬虫主文件
  -  ScoreSpider() 爬虫主程序 
     - def __init__()  以我的解释方法来讲，对象的初始属性
        - self.headers 请求头 有三个 分别对应不同的请求url
        - self.student_id 学号
        - self.pwd 密码
        - self.session() 初始化session 对象
            - 为什么要用 requests.session().get(url = )的方式？ 
             （为了储存cookies 这样可以使的不同的url可以共用 cookies）
        - 、、、、等等  在 init 中 实例化对象 这样 为的是只实例化一次就可以直接使用了 
# 未完成 待续（html 已经拿到）