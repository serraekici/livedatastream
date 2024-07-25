import random
import matplotlib.pyplot as plt
 
random_numbers = [] 
x = []
for _ in range(10):
    random_number = random.randint(1, 10) 
    random_numbers.append(random_number)    
print(random_numbers)  
for random_number in random_numbers:
    x.append(random_number)
 
y = [1,2,3,4,5,6,7,8,9,10] 
plt.plot(x, y) 
plt.xlabel('x - axis') 
plt.ylabel('y - axis') 
plt.title('Live Data Stream') 
plt.show()


