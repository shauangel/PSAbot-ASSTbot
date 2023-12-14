import requests
import config

if __name__ == "__main__":
    # url = "http://127.0.0.1:5000"

    # resp = requests.get(url+"/hello")
    # print(resp.text)

    test_sen = "Hi, just testing my APIs."
    # resp = requests.post(url=config.TOOLBOX_API_HOST + "/SO_api/get_items",
    #                     json={"urls": ["https://stackoverflow.com/questions/28461001/python-flask-cors-issue"] , "result_num":5, "page_num":0})
    # print(resp.json())

    response = requests.post(url=config.TOOLBOX_API_HOST + "/api/data_clean",
                             json={"content": test_sen}).json()
    print(response)

