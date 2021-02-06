from pydantic import BaseModel
from typing import List
import pygad
import numpy as np


TASK_START = "start"
TASK_END = "end"


# # ToDo try again to import this from another file
# class Task(BaseModel):
#     duration: int
#     people: int


class FormA(BaseModel):
    event: str
    time: int
    people: int


class FormB(BaseModel):
    time_a: int
    time_b: int
    people: int


def _item_iterator(solution_inputs):
    number_items = len(solution_inputs)
    return range(number_items)


def people_score(form_b: FormB, max_number_people):
    if form_b.people <= max_number_people:
        return 0
    else:
        return (form_b.time_b - form_b.time_a) *\
               (form_b.people - max_number_people)


def run_optimization(solution_inputs, optimization_parameters):

    def fitness_func(solution, solution_idx):
        item_iterator = _item_iterator(solution_inputs)
        starts = solution.copy()
        ends = [starts[i] + solution_inputs[i].duration for i in item_iterator]
        total_duration = np.max(ends) - np.min(starts)

        form_a_events = [
            FormA(
                time = starts[i],
                people = solution_inputs[i].people,
                event = TASK_START
            )
            for i in item_iterator
        ]
        form_a_events = form_a_events + [
            FormA(
                time = ends[i],
                people = solution_inputs[i].people,
                event = TASK_END
            )
            for i in item_iterator
        ]
        form_a_events.sort(key=lambda x: x.time)

        form_b_events = []
        running_people = 0
        for i in range(1, len(form_a_events)):
            if form_a_events[i - 1].event == "start":
                running_people += form_a_events[i - 1].people
            else:
                running_people -= form_a_events[i - 1].people
            aaa = FormB(
                time_a = form_a_events[i - 1].time,
                time_b = form_a_events[i].time,
                people = running_people
            )
            form_b_events.append(aaa)

        people_resource_score = np.sum([
            people_score(x, optimization_parameters.max_people)
            for x in form_b_events
        ])

        return 1.0 / ((1 * total_duration) + (1000 * people_resource_score))

    # last_fitness = 0
    #
    # def callback_generation(ga_instance):
    #     global last_fitness
    #     print("Generation = {generation}".format(generation=ga_instance.generations_completed))
    #     print("Fitness    = {fitness}".format(fitness=ga_instance.best_solution()[1]))
    #     print("Change     = {change}".format(change=ga_instance.best_solution()[1] - last_fitness))
    #     last_fitness = ga_instance.best_solution()[1]

    fitness_function = fitness_func
    ga_instance = pygad.GA(
        num_generations = optimization_parameters.number_generations,
        num_parents_mating = optimization_parameters.number_parents_mating,
        fitness_func = fitness_function,
        sol_per_pop = optimization_parameters.population_size,
        num_genes = len(solution_inputs),
        gene_type = int,
        init_range_low = 0,
        init_range_high = np.sum([x.duration for x in solution_inputs]),
        parent_selection_type = optimization_parameters.parent_selection_type,
        keep_parents = optimization_parameters.keep_parents,
        crossover_type = optimization_parameters.crossover_type,
        mutation_type = optimization_parameters.mutation_type,
        mutation_percent_genes = optimization_parameters.mutation_percent_genes
        # on_generation = callback_generation
    )
    ga_instance.run()
    solution, solution_fitness, solution_idx = ga_instance.best_solution()
    outcome = ["Parameters of the best solution : {solution}".format(solution=solution),
               "Fitness value of the best solution = {solution_fitness}".format(solution_fitness=solution_fitness),
               "Index of the best solution : {solution_idx}".format(solution_idx=solution_idx)]
    return "\n".join(outcome)
