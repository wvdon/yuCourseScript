#!/usr/bin/env python
# coding: utf-8


import time
import requests
import re
import json

# 所需要的参数,
# 从那获得？微信扫码，进去之后按f12，打开network。找到heartbeat的请求。在请求中分别找到
user_id = 45104243
cc = "9FE88481F8F872F39C33DC5901307461"
csrftoken = "TFnYP9W2OGUh3EEMN3M25bgyR5lqG99w"
sessionid = "mufi4soizcrv8w3gtphutbds0bekq0j8"
# 刷前两门课程。
num_coures = 2
# 请求间隔时间。
sleep_time = 1.0
# 学校ID，郑大默认是2824
university_id = '2824'
##参考：https://github.com/WolfIsMyName/yuketangHelper


headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36',
    'Content-Type': 'application/json',
    'Cookie': 'csrftoken=' + csrftoken + '; sessionid=' + sessionid + '; university_id=' + university_id + '; platform_id=3',
    'x-csrftoken': csrftoken,
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'university-id': university_id,
    'xtbz': 'cloud'
}
headers_v2 = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36',
    'Content-Type': 'application/json',
    'Cookie': 'csrftoken=' + csrftoken + '; sessionid=' + sessionid + '; university_id=' + university_id + '; platform_id=3',
    'x-csrftoken': csrftoken,
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'university-id': university_id,
    'xtbz': 'ykt',
    'xt-agent': 'web'
}

# In[81]:


user_info_url = "https://www.yuketang.cn/v2/api/web/userinfo"
response = requests.get(url=user_info_url, headers=headers_v2)
str_to_dict = eval(response.text)
course_list_url = "https://www.yuketang.cn/v2/api/web/courses/list?identity=2"
response_course = requests.get(url=course_list_url, headers=headers_v2)
your_courses = []
for ins in json.loads(response_course.text)["data"]["list"]:
    # course_list = eval(ins["course"])
    your_courses.append({
        "course_name": ins["course"]["name"],
        "classroom_id": ins["classroom_id"],
        "id": ins["course"]["id"],

    })


def video_fun(video_id, classroomid, cid, skuid, u, cc, name):
    url = "https://www.yuketang.cn/video-log/heartbeat/"
    get_url = "https://www.yuketang.cn/video-log/get_video_watch_progress/?cid=" + str(cid) + "&user_id=" + str(
        user_id) + "&classroom_id=" + str(classroomid) + "&video_type=video&vtype=rate&video_id=" + str(
        video_id) + "&snapshot=1"
    # print(get_url)
    progress = requests.get(url=get_url, headers=headers_v2)

    if_completed = '0'
    try:
        if_completed = re.search(r'"completed":(.+?),', progress.text).group(1)
    except:
        print("失败:" + name + ",id:" + str(video_id) + ":" + str(classroomid) + ":" + str(cid) + ":" + str(
            skuid) + ":" + str(u))
        print(progress.text)
        print(get_url)
        return 1
        pass
    if if_completed == '1':
        print(name + "已经学习完毕，跳过")
        time.sleep(sleep_time / 2)
    else:
        video_frame = 0
        val = 0
        learning_rate = 20
        t = time.time()
        timestap = int(round(t * 1000))
        while val != "1.0" and val != '1':
            heart_data = []
            for i in range(50):
                heart_data.append(
                    {
                        "i": 5,
                        "et": "loadstart",
                        "p": "web",
                        "n": "ali-cdn.xuetangx.com",
                        "lob": "ykt",
                        "cp": video_frame,
                        "fp": 0,
                        "tp": 0,
                        "sp": 1,
                        "ts": str(timestap),
                        "u": u,
                        "uip": "",
                        "c": cid,
                        "v": int(video_id),
                        "skuid": skuid,
                        "classroomid": classroomid,
                        "cc": str(cc),
                        "d": 6000,
                        "pg": "13832258_t77g",
                        "sq": 2,
                        "t": "video"
                    }
                )
                video_frame = video_frame + learning_rate
                max_time = int((time.time() + 3600) * 1000)
                timestap = min(max_time, timestap + 1000 * 15)
            data = {"heart_data": heart_data}
            r = requests.post(url=url, headers=headers, json=data)
            progress = requests.get(url=get_url, headers=headers_v2)
            tmp_rate = re.search(r'"rate":(.+?)[,}]', progress.text)
            try:
                if (str(tmp_rate.group(1)) == str(val)):
                    print("一直相等：" + tmp_rate.group(1) + ":" + str(val))
                    # print(data)
                    val = "1.0"
                    continue
                else:
                    val = tmp_rate.group(1)
                    print(name + ">学习进度为：" + str(float(val) * 100))
                    time.sleep(sleep_time)
            except Exception as e:
                print("失败_解析:" + name + ",id:" + str(video_id))
                val = "1"
                pass


# In[85]:


def watch(video_list, skuid):
    for x in video_list:
        # print(x["classroom_id"])
        # 9013574
        classroom_id = x["classroom_id"]
        cid = x["cid"]
        # print(cid)
        if x["other_list"]:
            for i in range(0, len(x["other_list"])):
                for z in x["other_list"][i]["leaf_list"]:
                    name = z["title"]
                    vid = z["id"]
                    leaf_type = z["leaf_type"]
                    if leaf_type != 0:
                        pass
                    video_fun(vid, classroom_id, cid, skuid, user_id, cc, name)
        for v in x['all_list']:
            vid = v["id"]
            name = v["title"]
            leaf_type = v["leaf_type"]
            if leaf_type != 0:
                pass
            video_fun(vid, classroom_id, cid, skuid, user_id, cc, name)


def do_watch(super_video_list, course, skuid):
    video_url = "https://www.yuketang.cn/c27/online_courseware/xty/kls/pub_news/" + super_video_list[0][
        "courseware_id"] + "/"
    video_response = requests.get(url=video_url, headers=headers)
    video_list = []
    for ins in json.loads(video_response.text)["data"]["content_info"]:
        all_list = []
        video_list.append({
            "classroom_id": your_courses[course]["classroom_id"],
            "cid": your_courses[course]["id"],
            "video_id": ["id"],
            "all_list": ins["leaf_list"],
            "other_list": ins["section_list"]
        })
    watch(video_list, skuid)


# 为了避免有时候请求异常返回，这里循环3次。
def playScript():
    for num in range(0, 3):
        for course in range(0, num_coures):
            course_class_url = "https://www.yuketang.cn/v2/api/web/logs/learn/" + str(
                your_courses[course]["classroom_id"]) + "?actype=-1&page=0&offset=20&sort=-1"
            super_video_respone = requests.get(url=course_class_url, headers=headers_v2)
            super_video_list = []
            ins = json.loads(super_video_respone.text)["data"]["activities"][0]
            super_video_list.append({
                "courseware_id": ins["courseware_id"],
                "sku_id": ins["content"]["sku_id"]
            })

            skuid = super_video_list[0]["sku_id"]
            # cid = your_courses[course]["id"]
            # video_id,classroomid,cid,skuid,u,cc,
            do_watch(super_video_list, course, skuid)


if __name__ == '__main__':
    playScript()