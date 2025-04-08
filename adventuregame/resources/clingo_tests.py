from clingo.control import Control

# init clingo controller in 'all model output' mode:
ctl = Control(["0"])

tested_asp_file = "test_adv_solve_asp5.txt"

# load ASP encoding:
with open(tested_asp_file, 'r', encoding='utf-8') as lp_file:
    example_lp = lp_file.read()

# print(example_lp)

# add encoding to clingo controller:
ctl.add(example_lp)

print("Encoding added.")

print("Grounding...")
# ground the encoding:
ctl.ground()

# report successful grounding:
print("Grounded!")
# for the complexity of these text adventures, even extensive ones, grounding should be finished in under a minute
# if it does, the encoding likely needs improvements - some early versions took more than a minute, while the current
# version, as used for adventure solving and shown in adventure_solve_asp_example.lp, takes milliseconds

# solve encoding, collect produced models:
models = list()
with ctl.solve(yield_=True) as solve:
    for model in solve:
        print("model:", model)
        model_split = model.__str__().split()
        models.append(model_split)
    satisfiable = str(solve.get())
    if satisfiable == "SAT":
        print("Adventure can be solved.")
    elif satisfiable == "UNSAT":
        print("Adventure can NOT be solved.")
# the last model in the models list is the optimal solution