import random
import matplotlib.pyplot as plt
 
random_numbers = [] 
for _ in range(10):
    random_number = random.randint(1, 10) 
    random_numbers.append(random_number)    
print(random_numbers) 
x = [random_numbers[0],random_numbers[1],random_numbers[2],random_numbers[3],random_numbers[4],random_numbers[5],random_numbers[6],random_numbers[7],random_numbers[8],random_numbers[9]] 
y = [1,2,3,4,5,6,7,8,9,10] 
plt.plot(x, y) 
plt.xlabel('x - axis') 
plt.ylabel('y - axis') 
plt.title('Live Data Stream') 
plt.show()

