
# curlgm
将 gearman client 包装起来,不再需要自己为每一个服务写一个client
你只需要使用一个 url 仅此而已

## 使用方法
1. 先赋执行权限
chmod u+x curlgm

2. 再放入你的环境变量中(非必须)
在 .bashrc(或者.zshrc) 中增加 export 
记得 source 一下使之生效

3. 执行
curlgm url (没有放入环境变量的情况下需要加上路径: ./curlgm url )
curlgm [-i -t][-c headerfile] [-f inputfile] url
-c(--conf) 指定 header 文件中应当是一个json字符串能够直接 json load 如果发生错误将使用自动header
-i(--info) 显示拼接的 request
-t(--test) 只拼接request 不发送，通常与 -i 一同使用
-f(--file) (未完成)指定执行文件，文件中每一行应当是一个 url 程序将依次发送

curlgm -i url         //打印信息并且发送request
curlgm -it url        //只为了测试拼接的request是否正确
curlgm -i -f filepath //为文件中每一行url 执行 且打印信息

#### url 规则
http://192.168.1.201:4730/worker_name;para=p,m,c;pack_in=0?groupname=local&filaname=1.doc&&"mvalue"&&{"cvalue":1}
------|----------------|-----------|--------------------|------------------------------------------------------|
http     workIP          workername      params                query

#### 参数说明
workIP: no description
workname: no description
params: 程序参数 用;分割参数
    现支持：para   pack_in   pack_out

query: request的值
    用 && 分割第一层参数key,与para中的值对应(参见例子)
    用 &  分割第二层参数key
    用 =  分割键值对: key=value
    其中 key 支持 string 以及 int 以及 float
    其中 value 支持 string 以及 int 以及 float 以及 json串


#### 例子:
curlgm -i 'http://192.168.1.201:4730/ecv_parser_new;para=p,m,c?groupname=local&filename=/data/chenchen/Alldoc/Alldoc/1.doc&rettype=json&&""&&{"csample":12}'

will build request like this:
---------
your gearman request:
IP= 192.168.1.201:4730
worker=ecv_parser_new
header={'user_ip': '192.168.1.201', 'user_name': 'chenchen', 'product_name': 'curlgm'}
request={'p': {u'groupname': u'local', u'rettype': u'json', u'filename': u'/data/chenchen/Alldoc/Alldoc/1.doc'}, 'c': {u'csample': 12}, 'm': u''}
params={'para': ['p', 'm', 'c']}
---------



## 注意事项
1. 避免在 params 部分出现 ; 和 = 因为他们是作为分隔符号用的

2. 在 query 部分如果出现 & 或者 = 号那么，可以使用转义 \& 这样不会被认为是分隔符，
当被双引号 "" 包裹住的内容会原封不动，里面的 & 和 = 不需要转义
当被 {} 或者 [] 包裹住的内容会直接 json loads

3. 默认所有的 123 数字都为 int 如果要使之变成 string 请变成 "123"
默认所有的 12.3 数字都为 float 如果要使之变成 string 请变成 "12.3"

