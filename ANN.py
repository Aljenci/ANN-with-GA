from random import uniform, randint

class Node:

    def __init__(self, input, bias):

        self.input = input
        self.bias = bias
        self.output = 0.0
        self.threeshold = 1.0
        self.weight = [uniform(-1.0, 1.0) for e in input]

    def calculate(self):

        if all(isinstance(n, Node) for n in self.input):
            net = sum([self.input[i].output*self.weight[i] for i in range(len(self.input))]) + self.bias
        else:
            net = sum(self.input) + self.bias
        self.output = net >= self.threeshold

    def set_weight(self, w):
        self.weight = w
        
    def get_num_inputs(self):
        return len(self.input)

class ANN:

    def __init__(self, n_in, n_out, hidden_layers):

        self.layer = [[Node([1.0], 1.0) for n in range(n_in)]]
        for i in range(len(hidden_layers)):
            self.layer.append([Node(self.layer[-1], 0.0) for j in range(hidden_layers[i])])
        self.layer.append([Node(self.layer[-1], 0.0) for j in range(n_out)])

    def get_output(self):

        return [node.output for node in self.layer[-1]]

    def set_input(self, input):

        for i in range(len(self.layer[0])):
            self.layer[0][i].input = input[i]
        self.recalculate()

    def recalculate(self):

        for layer in self.layer[1:-1]:
            for node in layer:
                node.calculate()
    
    def set_weight(self, weight):
        actual_weight_index = 0
        for i in range(1,len(self.layer)):
            layer = self.layer[i]
            for node in layer:
                node.set_weight(weight[actual_weight_index:actual_weight_index+node.get_num_inputs()])
                actual_weight_index = actual_weight_index + node.get_num_inputs()

class Chromosome:
    def __init__(self, size, mutation_probability = 10, data = []):
        if data == []:
            self.data = [uniform(0.0, 1.0) for i in range(size)]
        else:
            self.data = data

        self.mutation_probability = mutation_probability

        self.life_time = 0

    def crossover(self, other):
        child1 = []
        child2 = []
        for i in range(len(self.data)):
            if randint(0, 100) < 50:
                child1.append(self.data[i])
                child2.append(other.data[i])
            else:
                child2.append(self.data[i])
                child1.append(other.data[i])
        return child1, child2

    def mutation(self):
        while randint(0, 100) <= self.mutation_probability:
            index = randint(0,len(self.data)-1)
            self.data[index] = self.data[index] + uniform(-1.0, 1.0)

    def adaptability(self, test_case):
        ann = ANN(6, 15, [6, 6])
        ann.set_weight(self.data)
        score_list = []
        for case in test_case:
            list_input = [bool(0b100 & case[0]), bool(0b010 & case[0]), bool(0b001 & case[0]), bool(0b100 & case[1]), bool(0b010 & case[1]), bool(0b001 & case[1])]
            #result_bin = [bool(0b1000 & case[2]), bool(0b0100 & case[2]), bool(0b0010 & case[2]), bool(0b0001 & case[2])]
            ann.set_input(list_input)
            list_output = ann.get_output()
            #comparation = [result_bin[i] == list_output[i] for i in range(4)]
            #score = sum(comparation) * 100 / 4
            #score = sum(comparation) == 4
            score = list_output[case[2]]
            score_list.append(score)
        return sum(score_list)

class GA:
    def __init__(self, test_case, max_generations = 1000, init_population_size = 5, max_population_size = 20, max_life_time = 5):
        self.test_case = test_case
        self.max_generations = max_generations
        self.max_life_time = max_life_time
        self.max_population_size = max_population_size
        self.population = [Chromosome(6*6 + 6*6 + 6*14) for i in range(init_population_size)]
        self.best = self.population[0].data
        self.best_equal_count = 0

    def step(self):
        self.sort()
        if self.best == self.get_best().data:
            self.best_equal_count += 1
        else:
            self.best_equal_count = 0
            self.best = self.get_best().data
        self.crossover()
        self.mutation()
        for i in self.population:
            if i.life_time > self.max_life_time:
                self.population.remove(i)
            else:
                i.life_time += 1

    def sort(self):
        self.population = [p for (a, p) in reversed(sorted(zip(self.adaptability(), self.population)))]
        self.population = self.population[:self.max_population_size]

    def crossover(self):
        for i in range(0, len(self.population)-4, 2):
            child1_data, child2_data = self.population[i].crossover(self.population[i+1])
            child1 = Chromosome(6*6 + 6*6 + 6*14, data = child1_data)
            child1.mutation()
            child2 = Chromosome(6*6 + 6*6 + 6*14, data = child2_data)
            child2.mutation()
            self.population.append(child1)
            self.population.append(child2)

    def adaptability(self):
        return [i.adaptability(self.test_case) for i in self.population]

    def mutation(self):
        for i in self.population:
            i.mutation()

    def get_best(self):
        return [p for (a, p) in sorted(zip(self.adaptability(), self.population))][0]
        
def main():
    test_case = [[randint(0,7), randint(0,7), 0] for i in range(100)]
    for i in range(len(test_case)):
        test_case[i][2] = test_case[i][0] + test_case[i][1]
    ga = GA(test_case)
    
    iteration = 0
    while ga.best_equal_count < 99 and iteration < ga.max_generations:
        ga.step()
        best = ga.get_best()
        print "--\nBest id: ", sum(best.data)
        print "Best score: ", best.adaptability(test_case)
        iteration = iteration + 1

if __name__ == "__main__":
    main()