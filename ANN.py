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

    def set_bias(self, b):
        self.bias = b
        
    def get_num_inputs(self):
        return len(self.input)

class ANN:

    def __init__(self, n_in, n_out, hidden_layers):

        self.layer = [[Node([1.0], 0.0) for n in range(n_in)]]
        for i in range(len(hidden_layers)):
            self.layer.append([Node(self.layer[-1], uniform(-1.0, 1.0)) for j in range(hidden_layers[i])])
        self.layer.append([Node(self.layer[-1], uniform(-1.0, 1.0)) for j in range(n_out)])

    def get_output(self):

        out_list = [node.output for node in self.layer[-1]]
        return out_list

    def set_input(self, input):

        for i in range(len(self.layer[0])):
            node = self.layer[0][i]
            node.input = input[i]

    def recalculate(self):

        for layer in self.layer:
            for node in layer:
                node.calculate()
    
    def set_weight(self, weight):
        actual_weight_index = 0
        for i in range(1,len(self.layer)):
            layer = self.layer[i]
            for node in layer:
                node.set_bias(weight[actual_weight_index])
                actual_weight_index = actual_weight_index + 1
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
        ann = ANN(6, 15, [4, 4])
        ann.set_weight(self.data)
        score_list = []
        for case in test_case:
            list_input = [[bool(0b100 & case[0])], [bool(0b010 & case[0])], [bool(0b001 & case[0])], [bool(0b100 & case[1])], [bool(0b010 & case[1])], [bool(0b001 & case[1])]]
            #result_bin = [bool(0b1000 & case[2]), bool(0b0100 & case[2]), bool(0b0010 & case[2]), bool(0b0001 & case[2])]
            ann.set_input(list_input)
            ann.recalculate()
            list_output = ann.get_output()
            #comparation = [result_bin[i] == list_output[i] for i in range(4)]
            #score = sum(comparation) * 100 / 4
            #score = sum(comparation) == 4
            score = [1 if not i else -1 for i in list_output]
            score[case[2]] = -score[case[2]]
            score = (sum(score) + 15) / float(30)
            score_list.append(score)
        return sum(score_list) / len(score_list)

class GA:
    def __init__(self, test_case, max_generations = 1000, init_population_size = 5, max_population_size = 20, max_life_time = 5):
        self.test_case = test_case
        self.max_generations = max_generations
        self.max_life_time = max_life_time
        self.max_population_size = max_population_size
        self.population = [Chromosome(6*4 + 4*4 + 4*15 + 6+15+4+4) for i in range(init_population_size)]
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
        self.population = [(a, p) for (a, p) in reversed(sorted(zip(self.adaptability(), self.population)))]
        #print [a for (a, p) in self.population]
        self.population = [p for (a, p) in self.population]
        self.population = self.population[:self.max_population_size]

    def crossover(self):
        for i in range(0, len(self.population)-4, 2):
            child1_data, child2_data = self.population[i].crossover(self.population[i+1])
            child1 = Chromosome(6*4 + 4*4 + 4*15 + 6+15+4+4, data = child1_data)
            child1.mutation()
            child2 = Chromosome(6*4 + 4*4 + 4*15 + 6+15+4+4, data = child2_data)
            child2.mutation()
            self.population.append(child1)
            self.population.append(child2)

    def adaptability(self):
        return [i.adaptability(self.test_case) for i in self.population]

    def mutation(self):
        for i in self.population:
            i.mutation()

    def get_best(self):
        return [p for (a, p) in reversed(sorted(zip(self.adaptability(), self.population)))][0]
        
def main():
    test_case = [[randint(0,7), randint(0,7), 0] for i in range(100)]
    for i in range(len(test_case)):
        test_case[i][2] = test_case[i][0] + test_case[i][1]
    ga = GA(test_case)
    
    iteration = 0
    while ga.best_equal_count < 99 and iteration < ga.max_generations:
        ga.step()
        best = ga.get_best()
        print "--\nProcessed: ", int(iteration/float(ga.max_generations)*100), "%"
        print "Best id: ", sum(best.data)
        print "Best score: ", best.adaptability(test_case)
        iteration = iteration + 1
    
    print "Finish! Data of the best: ", ga.get_best().data

if __name__ == "__main__":
    main()
    #case = [randint(0,7), randint(0,7), 0]
    #case[2] = case[0] + case[1]
    #ann = ANN(6, 15, [6, 6])
    #ann.set_weight([-0.5522898169144459, 0.0005668009941913743, -0.022955854280367727, 0.6080563345098318, 0.43338227170540655, 0.33860314820497905, -0.7509692672671621, -0.5914906132524597, 0.13110284174999853, 0.3943958848833057,0.1318145310117712, 0.8087145157516176, -0.8998558871541839, -0.507559274947271, 0.09898588383124363, 0.6376516851510129, -0.8891500479608712, 0.8925038634315022, 0.006614332845435333, 0.8011553397895377, 0.8610788938642578, 0.1606351047204636, -1.1743355096235593, 0.13808980093547885, 0.5438711445382586, -0.14310976645381823, -0.06292477159142806, -0.014314771739919685, 0.5081882506815093, 0.8571242984783108, 0.16897647014270312, -0.029168817589071416, -1.2634173584643038, 0.5715376685064752, 1.3804138815728526, 0.12688546543129764, 0.889403610814518, 0.4441466235317355, 0.0679957342739107, 0.8698091171499241, 0.24549258418038755,-0.3128976188230739, 0.5971930933816247, 0.014556174491848761, 0.7681731055949687, 0.8960280260969252, 0.9649797344333126, -0.7081516373015608, -0.773319805425846, 0.10819854344247082, 0.6990693687038926, 0.03001957748668338, 0.35025909021052604, 0.0010575436592278331, 0.11231600579776291, -0.3214721086217188, -0.00013213697912861644, 0.23075901078768846, -0.8212909632587571, -0.6655520255819009, 0.7455694499153938, -0.018988040900148717, 0.15484788231906155, 0.4310203049636162, 0.763128747154652, 0.10541170724639748, 0.3611904407914438, -0.4142989119240723, -0.01168060451936015, -0.020307352073703933, -0.9743781879494721, 0.7589533607606475, 0.0977495195454966, 0.5676217758587025, 0.6285291777498172, -1.030276206413855, 0.6632108749292362, 0.008681853397411232, 0.630770309570829, 0.8541979236617092, 0.3727569188907357, -1.1126728065593268, 0.018335689789263143, 0.17591190438252668, -0.3080263858682307, 0.34702936579568167, 0.046733824463786156,0.9002163783514348, 0.09608050035439686, 0.6263190581357128, 1.0654095589003618, 0.21428916068264892, -0.460661981574664, 0.49062990646517823, -0.6560889667803952, -0.339195324691543, 0.6973264389719276, 0.47053101233094086, 0.2700549408631193, 0.6940565622471003, -0.23124211783515092, 0.5651685151825363, 0.6597135189549249, 0.8811641176989509, 0.308928706416413, 0.5096493877079419, -0.23591810556059356, 0.6179166616421465, 0.8498631720661274, 0.14973126353256438, 0.46282337194220413, 0.16533867709352323, 0.2973650545249621, 0.601869434192164, 0.6839861183945886, 0.11008826188027943, 0.18035827000187743, 0.4285675069367785, 0.6118208569815994, -0.586237168737522, 0.854756978512287, -0.9423876733040386, 0.5485053334201493, 0.8191036356309254, 1.6739192707412938, 0.5732231122870529, 0.7826088705373806, 0.9520086467431038, 0.054236844836470954, 0.9418688258035605, 0.03585141457923091, 0.10566662025342499, 0.13356521658060594, 0.35880296454294724, 0.3004048746418835, 0.8386266208284037, 0.8846091963077694, 0.6618905330720997, 0.2695969316573198, 0.010737378733486347, 0.35778787412320967, 0.10023824815823601, -0.10107728219831291, -0.18810896541569566, 0.7039213999190891, 0.9901996833006519, -0.5681075525170699, 0.2839921789294183, 0.3402061818791817, -0.25348825011583054, 0.08042412457942683, 0.8679676426134122, 0.05534419496905951, -0.34334744067132117, 0.5319824250037428, -0.08681340415646066, -0.09825411604202994, -0.13985301579060783, 0.4369599608701096, 0.3658613653243771, -0.3410660249890688, 0.6461248060006097, 0.21438313345445914, 0.9279969712665084, 1.4961440787382712, 0.4394840482032287, 0.46462543527942746, -0.9748257224912653, -0.5184363277379777, 0.4600278983681052, 0.9120946577975527, 0.5566810513952337, 0.39353084153342177, 0.009442603712809916, -0.9038710123008491, -0.41271620701089884, 0.4025147730631886, 0.8175985322801291, 1.2834516009299586, 0.7984903235241352, 0.5761041031623588, 0.6492016440666272, 0.5343988596289017, -0.5287415719383365, 0.07757131631277547, 0.055562373124783515, 0.13324904279186556, 0.9971174019289888, -0.6356545356053117, 0.7897031723335103, 0.6644813734685596, 0.551696300494749, 1.0510952805110911, 0.8421435020975863, 0.7169837939499335])
    #list_input = [[bool(0b100 & case[0])], [bool(0b010 & case[0])], [bool(0b001 & case[0])], [bool(0b100 & case[1])], [bool(0b010 & case[1])], [bool(0b001 & case[1])]]
    #ann.set_input(list_input)
    #ann.recalculate()
    #list_output = ann.get_output()
    #print case, list_output, list_output[case[2]]