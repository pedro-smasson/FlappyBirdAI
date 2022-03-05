from __future__ import print_function

import copy
import warnings

import graphviz
import matplotlib.pyplot as pyplot
import numpy as np


def plot_stats(statistics, ylog=False, view=False, filename='avg_fitness.svg'):
    """ Plots the population's average and best fitness. """
    if pyplot is None:
        warnings.warn("This display is not available due to a missing optional dependency (matplotlib)")
        return

    generation = range(len(statistics.most_fit_genomes))
    best_fitness = [c.fitness for c in statistics.most_fit_genomes]
    avg_fitness = np.array(statistics.get_fitness_mean())
    stdev_fitness = np.array(statistics.get_fitness_stdev())

    pyplot.plot(generation, avg_fitness, 'b-', label="average")
    pyplot.plot(generation, avg_fitness - stdev_fitness, 'g-.', label="-1 sd")
    pyplot.plot(generation, avg_fitness + stdev_fitness, 'g-.', label="+1 sd")
    pyplot.plot(generation, best_fitness, 'r-', label="best")

    pyplot.title("Population's average and best fitness")
    pyplot.xlabel("Generations")
    pyplot.ylabel("Fitness")
    pyplot.grid()
    pyplot.legend(loc="best")
    if ylog:
        pyplot.gca().set_yscale('symlog')

    pyplot.savefig(filename)
    if view:
        pyplot.show()

    pyplot.close()


def plot_spikes(spikes, view=False, filename=None, title=None):
    """ Plots the trains for a single spiking neuron. """
    t_values = [t for t, I, v, u, f in spikes]
    v_values = [v for t, I, v, u, f in spikes]
    u_values = [u for t, I, v, u, f in spikes]
    I_values = [I for t, I, v, u, f in spikes]
    f_values = [f for t, I, v, u, f in spikes]

    fig = pyplot.figure()
    pyplot.subplot(4, 1, 1)
    pyplot.ylabel("Potential (mv)")
    pyplot.xlabel("Time (in ms)")
    pyplot.grid()
    pyplot.plot(t_values, v_values, "g-")

    if title is None:
        pyplot.title("Izhikevich's spiking neuron model")
    else:
        pyplot.title("Izhikevich's spiking neuron model ({0!s})".format(title))

    pyplot.subplot(4, 1, 2)
    pyplot.ylabel("Fired")
    pyplot.xlabel("Time (in ms)")
    pyplot.grid()
    pyplot.plot(t_values, f_values, "r-")

    pyplot.subplot(4, 1, 3)
    pyplot.ylabel("Recovery (u)")
    pyplot.xlabel("Time (in ms)")
    pyplot.grid()
    pyplot.plot(t_values, u_values, "r-")

    pyplot.subplot(4, 1, 4)
    pyplot.ylabel("Current (I)")
    pyplot.xlabel("Time (in ms)")
    pyplot.grid()
    pyplot.plot(t_values, I_values, "r-o")

    if filename is not None:
        pyplot.savefig(filename)

    if view:
        pyplot.show()
        pyplot.close()
        fig = None

    return fig


def plot_species(statistics, view=False, filename='speciation.svg'):
    """ Visualizes speciation throughout evolution. """
    if pyplot is None:
        warnings.warn("This display is not available due to a missing optional dependency (matplotlib)")
        return

    species_sizes = statistics.get_species_sizes()
    num_generations = len(species_sizes)
    curves = np.array(species_sizes).T

    fig, ax = pyplot.subplots()
    ax.stackplot(range(num_generations), *curves)

    pyplot.title("Speciation")
    pyplot.ylabel("Size per Species")
    pyplot.xlabel("Generations")

    pyplot.savefig(filename)

    if view:
        pyplot.show()

    pyplot.close()


def draw_net(config, genome, view=False, filename=None, node_names=None, show_disabled=True, prune_unused=False,
             node_colors=None, fmt='svg'):
    """ Receives a genome and draws a neural network with arbitrary topology. """
    # Attributes for network nodes.
    if graphviz is None:
        warnings.warn("This display is not available due to a missing optional dependency (graphviz)")
        return

    if node_names is None:
        node_names = {}

    assert type(node_names) is dict

    if node_colors is None:
        node_colors = {}

    assert type(node_colors) is dict

    node_attrs = {
        'shape': 'circle',
        'fontsize': '9',
        'height': '0.2',
        'width': '0.2'}

    dot = graphviz.Digraph(format=fmt, node_attr=node_attrs)

    inputs = set()
    for k in config.genome_config.input_keys:
        inputs.add(k)
        name = node_names.get(k, str(k))
        input_attrs = {'style': 'filled', 'shape': 'box', 'fillcolor': node_colors.get(k, 'lightgray')}
        dot.node(name, _attributes=input_attrs)

    outputs = set()
    for k in config.genome_config.output_keys:
        outputs.add(k)
        name = node_names.get(k, str(k))
        node_attrs = {'style': 'filled', 'fillcolor': node_colors.get(k, 'lightblue')}

        dot.node(name, _attributes=node_attrs)

    if prune_unused:
        connections = set()
        for cg in genome.connections.values():
            if cg.enabled or show_disabled:
                connections.add((cg.in_node_id, cg.out_node_id))

        used_nodes = copy.copy(outputs)
        pending = copy.copy(outputs)
        while pending:
            new_pending = set()
            for a, b in connections:
                if b in pending and a not in used_nodes:
                    new_pending.add(a)
                    used_nodes.add(a)
            pending = new_pending
    else:
        used_nodes = set(genome.nodes.keys())

    for n in used_nodes:
        if n in inputs or n in outputs:
            continue

        attrs = {'style': 'filled',
                 'fillcolor': node_colors.get(n, 'white')}
        dot.node(str(n), _attributes=attrs)

    for cg in genome.connections.values():
        if cg.enabled or show_disabled:
            #if cg.input not in used_nodes or cg.output not in used_nodes:
            #    continue
            input, output = cg.key
            a = node_names.get(input, str(input))
            b = node_names.get(output, str(output))
            style = 'solid' if cg.enabled else 'dotted'
            color = 'green' if cg.weight > 0 else 'red'
            width = str(0.1 + abs(cg.weight / 5.0))
            dot.edge(a, b, _attributes={'style': style, 'color': color, 'penwidth': width})

    dot.render(filename, view=view)

    return dot