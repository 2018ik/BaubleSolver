threes = 1
fours = 3
fives = 8
all_nums = {}
def nums(threes, fours, fives, sum):
    if (threes, fours, fives) not in all_nums:
        all_nums[(threes, fours, fives)] = sum
        if (threes > 0):
            nums(threes-1, fours, fives, sum+3)
        if (fours > 0):
            nums(threes, fours-1, fives, sum+4)
        if (fives > 0):
            nums(threes, fours, fives-1, sum+5)
nums(threes, fours, fives, 0)
print(sorted(list(set(all_nums.values()))))

