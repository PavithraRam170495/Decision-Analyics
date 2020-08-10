from ortools.sat.python import cp_model

#Task A
#object - names
names = ['Carol', 'Elisa', 'Oliver', 'Lucas']

#predicates - university, nationality, course and gender
university = ['London', 'Cambridge', 'Oxford', 'Edinburg']
nationality = ['Australia', 'USA', 'South Africa', 'Canada']
course = ['History', 'Medicine', 'Law', 'Architecture']
gender = ['male','female']

#Task D
#solution printer which prints the possible solutions with object name and its respective predicates
class SolutionPrinter(cp_model.CpSolverSolutionCallback):
    def __init__(self, university, nationality, course, gender):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.university_ = university
        self.nationality_ = nationality
        self.course_ = course
        self.gender_ = gender
        self.solutions_ = 0

    def OnSolutionCallback(self):
        self.solutions_ = self.solutions_ + 1
        print("solution", self.solutions_)

        for name in names:
            print(" - " + name + ":")
            for uni in university:
                if (self.Value(self.university_[name][uni])):
                    print("    - ", uni)
            for nation in nationality:
                if (self.Value(self.nationality_[name][nation])):
                    print("    - ", nation)
            for cours in course:
                if (self.Value(self.course_[name][cours])):
                    print("    - ", cours)
            for gen in gender:
                if (self.Value(self.gender_[name][gen])):
                    print("    - ", gen)
        print()


def main():
    model = cp_model.CpModel()

    #creating Boolean Decision variables for every object and all the predicate values
    name_university = {}
    for name in names:
        variables = {}
        for uni in university:
            variables[uni] = model.NewBoolVar(name + uni)
        name_university[name] = variables

    name_nationality = {}
    for name in names:
        variables = {}
        for nation in nationality:
            variables[nation] = model.NewBoolVar(name + nation)
        name_nationality[name] = variables

    name_course = {}
    for name in names:
        variables = {}
        for cours in course:
            variables[cours] = model.NewBoolVar(name + cours)
        name_course[name] = variables

    name_gender = {}
    for name in names:
        variables = {}
        for gen in gender:
            variables[gen] = model.NewBoolVar(name + gen)
        name_gender[name] = variables

    # Task C
    # implicit constraints
    # 1. Carol and Elisa are females. Oliver and Lucas are males.
    model.AddBoolAnd([name_gender['Carol']['female']])
    model.AddBoolAnd([name_gender['Elisa']['female']])
    model.AddBoolAnd([name_gender['Oliver']['male']])
    model.AddBoolAnd([name_gender['Lucas']['male']])


    # 2. every student goes to a different university, is from a different nationality and studies a different course
    for i in range(4):
        for j in range(i + 1, 4):
            for k in range(4):
                model.AddBoolOr(
                    [name_university[names[i]][university[k]].Not(), name_university[names[j]][university[k]].Not()])
                model.AddBoolOr([name_nationality[names[i]][nationality[k]].Not(),
                                 name_nationality[names[j]][nationality[k]].Not()])
                model.AddBoolOr([name_course[names[i]][course[k]].Not(), name_course[names[j]][course[k]].Not()])


    # 3. every student should have a property(nationality, course, university, gender)
    for name in names:
        variables = []
        for uni in university:
            variables.append(name_university[name][uni])
        model.AddBoolOr(variables)

        variables = []
        for nation in nationality:
            variables.append(name_nationality[name][nation])
        model.AddBoolOr(variables)

        variables = []
        for cours in course:
            variables.append(name_course[name][cours])
        model.AddBoolOr(variables)

        variables = []
        for gen in gender:
            variables.append(name_gender[name][gen])
        model.AddBoolOr(variables)

        # 4 .every student should posses a maximum of one property(university, nationality and course)
        for i in range(4):
            for j in range(i + 1, 4):
                model.AddBoolOr(
                    [name_university[name][university[i]].Not(), name_university[name][university[j]].Not()])
                model.AddBoolOr(
                    [name_nationality[name][nationality[i]].Not(), name_nationality[name][nationality[j]].Not()])
                model.AddBoolOr([name_course[name][course[i]].Not(), name_course[name][course[j]].Not()])

        for i in range(2):
            for j in range(i + 1, 2):
                model.AddBoolOr([name_gender[name][gender[i]].Not(), name_gender[name][gender[j]].Not()])

        #Task B
        # explicit constraints given in the assignment
        # constraint1 : One of them is going to London
        # This constraint is included in the implicit constraints(every student should have atleast one property)

        # constraint 2 : Exactly one boy and one girl chose a university in a city with the same initial of their names
        model.AddBoolXOr([name_university['Carol']['Cambridge'], name_university['Elisa']['Edinburg']])
        model.AddBoolXOr([name_university['Oliver']['Oxford'], name_university['Lucas']['London']])

        # constraint 3 : A boy is from Australia, the other studies History.
        model.AddBoolAnd([name_nationality[name]["Australia"]]).OnlyEnforceIf(name_gender[name]["male"]).OnlyEnforceIf([name_course[name]["History"].Not()])
        #Explicitly mentioning that the other boy studies 'History' does not give a solution at all.
        #model.AddBoolAnd([name_course[name]["History"]]).OnlyEnforceIf(name_gender[name]["male"])

        # constraint 4 : A girl goes to Cambridge, the other studies medicine.
        model.AddBoolAnd([name_university[name]["Cambridge"]]).OnlyEnforceIf(name_gender[name]["female"]).OnlyEnforceIf(name_course[name]["Medicine"].Not())
        # Explicitly mentioning that the other girl studies 'Medicine' does not give a solution at all.
        # model.AddBoolAnd(name_course[name]["Medicine"]).OnlyEnforceIf(name_gender[name]["female"])

        # constraint 5 : Oliver studies Law or is from USA; He is not from South Africa.
        model.AddBoolXOr([name_course["Oliver"]["Law"], name_nationality["Oliver"]["USA"]])
        #It is not necessary to mention that Oliver is not from 'South Africa'
        model.AddBoolAnd([name_nationality["Oliver"]["South Africa"].Not()])

        # constraint 6 : The student from Canada is a historian or will go to Oxford.
        #1-1 also works
        model.AddBoolOr([name_course[name]["History"], name_university[name]["Oxford"]]).OnlyEnforceIf(
             name_nationality[name]["Canada"])


        # constraint 7 : The student from South Africa is going to Edinburg or will study Law.
        #1-1 also works
        model.AddBoolOr([name_university[name]["Edinburg"], name_course[name]["Law"]]).OnlyEnforceIf(
            name_nationality[name]["South Africa"])




    solver = cp_model.CpSolver()
    solver.SearchForAllSolutions(model, SolutionPrinter(name_university, name_nationality, name_course, name_gender))

main()
