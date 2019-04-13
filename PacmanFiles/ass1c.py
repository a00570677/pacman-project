# Giorgia Corrado (s1017255)
# Diego Garcia Cerdas (s1020485)

import shop  # contains FruitShop class definition


def shop_smart(order: list, shops: list) -> shop.FruitShop:
    """
    Calculate at which shop the given order is cheapest.
    :param order: (list) a list of (fruit, amount) tuples
    :param shops: (list) a list of FruitShops
    :returns: (shop.FruitShop) the shop that at which the order is cheapest
    """
    cheapest_sum = float('inf')  # Initialize cheapestSum with the biggest possible value
    cheapest_shop = None  # Keeps track of the cheapest shop
    for element in shops:  # For each element in the list of shops
        current_sum = 0  # Keeps track of the sum for the current shop
        for fruit, amount in order:  # For every fruit tuple in the order list
            current_sum += amount * element.prices[fruit]  # Add the cost for the specified amount of fruit
        if current_sum < cheapest_sum:  # if the current sum is cheaper than the previous cheapest sum
            cheapest_sum = current_sum  # update sum
            cheapest_shop = element  # update cheapest shop
    return cheapest_shop


def main():
    fruits1 = {'apples': 2.0, 'oranges': 1.0}
    fruits2 = {'apples': 1.0, 'oranges': 5.0}
    shop1 = shop.FruitShop('shop1', fruits1)
    shop2 = shop.FruitShop('shop2', fruits2)
    shops = [shop1, shop2]
    order1 = [('apples', 1.0), ('oranges', 3.0)]
    order2 = [('apples', 3.0)]
    print(f'For order {order1} the best shop is {shop_smart(order1, shops).name}.')
    print(f'For order {order2} the best shop is {shop_smart(order2, shops).name}.')


if __name__ == '__main__':
    main()
