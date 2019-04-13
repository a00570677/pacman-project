# Giorgia Corrado (s1017255)
# Diego Garcia Cerdas (s1020485)

import shop


def shop_loop(fruit: str):
    """
    Prints the same output as running `python shop.py` when called as "shop_loop('apples')".
    A for-loop is used for iterating over shops.
    This function does not have a return value.
    :param fruit: (str) name of a fruit
    """

    shop_names = ['Aldi', 'Albert Heijn']
    shop_prices = [{'apples': 1.00, 'oranges': 1.50, 'pears': 1.75},
                   {'kiwis': 6.00, 'apples': 4.50, 'peaches': 8.75}]
    for index in range(len(shop_names)):  # for each index in the lists
        new_shop = shop.FruitShop(shop_names[index], shop_prices[index])  # create new shop with name and price at index
        if fruit in new_shop.prices:  # if the fruit is a key in the shop's price dictionary
            cost = new_shop.prices[fruit]  # obtain the cost from the price dictionary
            print(f'{fruit.title()} cost €{cost:.2f} at {new_shop.name}.')
        else:
            print(f"Sorry, we don't have {fruit}.")


if __name__ == '__main__':
    shop_loop('apples')
