from fancy import *


client = MongoClient()
db = client.test
item_collection = db.item

l= get_links()   #返回一个网址的列表
itemlist = get_info(l) #返回一个列表，列表里是字典
item_collection.insert_many(itemlist)
