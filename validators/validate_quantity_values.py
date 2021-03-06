import json
import redis
import pandas as pd

db = redis.Redis()


class ValidateQuantityValues:
    def __init__(self, data):
        self.name = f"base_{data['name']}"
        self.values = None

    def validate(self, values):
        data_from_doc = json.loads(db.get(self.name).decode("UTF-8"))["obj"]
        return values

    @staticmethod
    def format_data(v):
        top = []
        flatten = lambda l: [item for sublist in l for item in sublist]

        for i in v:
            result = list(i.values())
            for a in result:
                top.append(list(a.values()))

        return flatten(top)

    # def validate(self, values):
    #     self.values = values
    #     items_with_lines = self.get_values_with_lines()
    #     df = self.get_values_per_line(items_with_lines)
    #     print(df)
    #     self.values = self.order_items(df)

    def get_values(self):
        return self.values

    @staticmethod
    def order_items(df):
        aux = []
        df = df.sort_values("position_left").drop(['position_x', 'position_y', 'position_top', 'position_left'], axis=1)
        for i in range(3, len(df.index), 3):
            df_parse = df.iloc[i - 3:i].sort_values(by="type_array").drop(["type_array"], axis=1)
            aux.append(df_parse.values.tolist())
        return aux

    def get_values_with_lines(self):
        items_with_lines = []
        _ = ['part_number', 'quantitie', 'unit_price']
        for value, type__ in zip(self.values, _):
            for data in value:
                for dt in data:
                    aux = db.lrange(dt, 0, 4)[0].decode("UTF-8").split("|")
                    aux.insert(0, dt)
                    aux.append(type__)
                    items_with_lines.append(aux)
        return items_with_lines

    @staticmethod
    def get_values_per_line(items):
        name, position_x, position_y, position_top, position_left, type_array = [], [], [], [], [], []
        for item in items:
            name.append(item[0]), position_x.append(float(item[1])),
            position_y.append(float(item[2])), position_top.append(float(item[3])),
            position_left.append(float(item[4])), type_array.append(item[5]),
        data = {
            'name': name,
            'position_x': position_x,
            'position_y': position_y,
            'position_top': position_top,
            'position_left': position_left,
            'type_array': type_array
        }
        return pd.DataFrame(data)


'''''
[
    ['366400', '4.591003060340881 ', ' 2.1132007241249084 ', ' 21.292367577552795 ', ' 299.96727347373957'], 
    ['29.721,60', '6.005305051803589 ', ' 2.2954046726226807 ', ' 91.12921953201294 ', ' 365.00933110713953'], 
    ['29.721,60', '6.005305051803589 ', ' 2.2954046726226807 ', ' 91.12921953201294 ', ' 365.00933110713953'], 
    ['17.280,00', '6.01431131362915 ', ' 2.26670503616333 ', ' 14.9065762758255 ', ' 299.96673882007593'], 
    ['1,72000', '4.825198650360107 ', ' 2.2802501916885376 ', ' 81.90510272979736 ', ' 299.95532602071756']
]
'''''
