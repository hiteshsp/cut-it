from pynamodb.models import Model
from pynamodb.attributes import NumberAttribute, UnicodeAttribute
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection


class ShortURLIndex(GlobalSecondaryIndex):
    class Meta:
        read_capacity_units = 1
        write_capacity_units = 1
        projection = AllProjection()
    short_url = UnicodeAttribute(default=0, hash_key=True)


class URLModel(Model):
    class Meta:
        table_name = 'flask-datastore'
        region='eu-north-1'
        write_capacity_units = 1
        read_capacity_units = 1
    long_url = UnicodeAttribute(hash_key=True)
    created_time = UnicodeAttribute(range_key=True)
    hits = NumberAttribute(default=0)
    short_url_index = ShortURLIndex()
    short_url = UnicodeAttribute()
    last_accessed = UnicodeAttribute()


test_obj = URLModel()


# item = test_obj.get('http://google.com', '1582444849')
# print(item.short_url)

# if not test_obj.exists():
#     test_obj.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)



# for item in test_obj.short_url_index.query('0'):
#     print("Item queried from index: {0}".format(item))


