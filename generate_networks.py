#!/usr/bin/env python2.5

import sys
import random
from math import ceil
sys.path.append('./python_modules')
import networkx as nx
import matplotlib.pyplot as plt
from prettytable import PrettyTable

TAB = '  '

def get_adjmatrix(G):
    ans = ''
    d = nx.convert.to_dict_of_dicts(G)
    for n in d:
        #ans += n + ': '
        for n2 in G.nodes():
            ans += '1 ' if n2 in d[n].keys() else '0 '
        ans += '\n'
    return ans

def get_clustering_coeff(G):
    cc = []
    for n in G.degree_iter():
        node, deg = n
        node_subgraph = G.subgraph(G.neighbors(node))
        num_e_sub = node_subgraph.size()
        try:
            cc.append(2.0 * num_e_sub / deg / (deg-1))
        except ZeroDivisionError:
            cc.append(1)  # convert 0/0 to 1
    cc_avg = sum(cc)/len(cc)
    return cc_avg

def write_adjmatrix_to_file(G, filename):
    f = open(filename, 'w')
    f.write(get_adjmatrix(G))
    f.close()

def get_degree_distribution(G):
    degree_range = range(0, max(G.degree())+1)
    degree_count = []
    degree_dist = {}
    for i in degree_range:
        degree_count.append(G.degree().count(i))
    for i in degree_range:
        degree_dist[i] = degree_count[i]*1.0/sum(degree_count)
    #print degree_dist
    #print
    return degree_dist

def get_max_degree_count(G):
    degree_range = range(0, max(G.degree())+1)
    degree_count = []
    for i in degree_range:
        degree_count.append(G.degree().count(i))
    return max(degree_count)

def rule1(G, current_vertex, prev_chosen_vertices = [], debug = False):
    #if debug: print TAB, current_vertex, 'rule1',
    degree_dict = {}
    degree_pmf = {}
    # buidling degree_pmf
    for n in G.degree_iter():
        degree_dict[n[0]] = n[1]
    for n in degree_dict:
        degree_pmf[n] = 1.0*degree_dict[n]/sum(degree_dict.values())
    while True:     # make sure to pick a distinct vertex
        cumul_prob = 0
        r = random.random()
        for n in degree_pmf:  # scan the cumulative-pmf
            cumul_prob += degree_pmf[n]
            if r < cumul_prob:
                w = n
                break         # break on pmf hit
        #if debug: print w,
        if w not in prev_chosen_vertices and w != current_vertex:
            break   # break if a distinct vertex is picked
    if debug: print TAB*2, current_vertex, '--r1--', w
    return w

def rule2(G, current_vertex, prev_rule1_vertex, prev_chosen_vertices, debug = False):
    #if debug: print TAB, current_vertex, 'rule2',
    # if rule is not possibe
    if list(set(G.neighbors(prev_rule1_vertex)).difference(G.neighbors(current_vertex))) == [current_vertex]:
        if debug: print TAB*2, current_vertex, 'rule2 not possibe! switching to rule1...',
        return rule1(G, current_vertex, prev_chosen_vertices, debug = debug)
    while True:     # make sure rule2 is met
        u = random.choice(G.neighbors(prev_rule1_vertex))
        #if debug: print u,
        if u not in prev_chosen_vertices and u not in G.neighbors(current_vertex) and u != current_vertex:
            break   # break if rule2 is met
    if debug: print TAB*2, current_vertex, '--r2--', u
    return u

def smallworld_graph(V, m, p, debug = False, verbose = True):
    if not verbose: debug = False
    if m > V:
        print 'BAD INPUT: initial vertices', m, 'cannot be larger than total vertices', V, '!'
        sys.exit(1)
    print 'generating small world graph with', m, 'initial and', V, 'total vertices and P(rule1) =', p, '...'
    G = nx.Graph()
    if verbose: print TAB, 'generating', m, 'initial vertices...'
    for n in xrange(0, m):    # adding initial m vertices
        G.add_node('V'+str(n))
    # adding (m+1)th vertices and connect it to initial m vertices
    G.add_node('V'+str(m))
    if verbose: print TAB, 'generating the rest of', (V-m), 'vertices and connecting them...'
    for e in xrange(0, m):  # adding m edges for (m+1)th vertex
        G.add_edge('V'+str(m), 'V'+str(e))
        if debug: print TAB*2, 'V'+str(m), '------', 'V'+str(e)
    # adding the rest of (V-m-1) vertices
    for n in xrange(m+1, V):
        current_vertex = 'V'+str(n)
        G.add_node(current_vertex)
        prev_chosen_vertices = []
        for e in xrange(0, m):  # adding m edges for the current vertex
            # first edge always with rule1 and subsequent edges selected with probabilty distribution
            r = min(0, p-1) if e == 0 else random.random()
            if r < p: # rule1
                chosen_vertex = rule1(G, current_vertex, prev_chosen_vertices, debug = debug)
                prev_rule1_vertex = chosen_vertex
            else:     # rule2
                chosen_vertex = rule2(G, current_vertex, prev_rule1_vertex, prev_chosen_vertices, debug = debug)
            G.add_edge(current_vertex, chosen_vertex)
            prev_chosen_vertices.append(chosen_vertex)
    if debug: print TAB, '------------------------------------------------------------'
    if verbose: print TAB, 'completed!'
    if verbose: print TAB, '#vertices:', G.order(), TAB, '#edges:', G.size()
    if verbose: print TAB, 'clustering coeffecient:', get_clustering_coeff(G)
    print
    return G

def random_graph(V, E, debug = False, verbose = True):
    if not verbose: debug = False
    if E not in range(int(ceil(V/2.0)), V*(V-1)/2+1):
        print 'BAD INPUT: cannot generate a graph with', V, 'vertices and', E, 'edges!'
        sys.exit(1)
    print 'generating random graph with', V, 'vertices and', E, 'edges...'
    G = nx.Graph()
    if verbose: print TAB, 'generating', V, 'vertices...'
    for n in xrange(0, V):    # adding all V vertices
        G.add_node('V'+str(n))
    if verbose: print TAB, 'connecting vertices randomly...'
    ii = 0
    while G.size() != E:
        n1, n2 = None, None
        while n1 == n2 or G.has_edge(n1, n2): # avoiding self loops and repeated edges
            n1 = random.choice(G.nodes())
            n2 = random.choice(G.nodes())
        G.add_edge(n1, n2)
        if debug: print TAB*2, '#', ii, ':', n1, '------', n2
        ii += 1
    # searching for orphan nodes
    nodes_orphan = []
    for n in G:
        if G.degree(n) == 0: # if orphan node
            nodes_orphan.append(n)
    nodes_nonorphan = list(set(G.nodes()).difference(nodes_orphan))
    # connecting orphan nodes
    if verbose: print TAB, 'connecting', len(nodes_orphan), 'orphan vertices...'
    for n in nodes_orphan:
        while True:         # make sure all the neighbors have degree > 1
            while True:     # make sure the selected node has degree > 0
                n1 = random.choice(nodes_nonorphan)
                if G.degree(n1) > 0:
                    break   # break if selected node has degree > 0 (CHANGE: previously 1)
            can_delete = []
            for n2 in G.neighbors_iter(n1):
                if G.degree(n2) > 1:
                    can_delete.append(n2)
            if len(can_delete) != 0:
                n3 = random.choice(can_delete)
                G.remove_edge(n1, n3)
                G.add_edge(n, n1)
                nodes_nonorphan.append(n)
                if debug: print TAB*2, n, '-----', n1, '(', n1, '--x--', n3, ')'
                break       # break if all the neighbors have degree > 1
    if debug: print TAB, '------------------------------------------------------------'
    if verbose: print TAB, 'completed!'
    if verbose: print TAB, '#vertices:', G.order(), TAB, '#edges:', G.size()
    if verbose: print TAB, 'clustering coeffecient:', get_clustering_coeff(G)
    print
    return G

def main(V, m, debug = False):
    # sequence of p to iterate over. only first three entries will be used
    pr1 = tuple([0.3, 0.5, 0.7])

    #random.setstate( )
#    f = open('help_stuff/random_state.out', 'w')
#    f.write(str(random.getstate()))
#    f.close()

    RG = random_graph(V, (V-m)*m, debug=debug)
    RG_dd = get_degree_distribution(RG)
    RG_cc = get_clustering_coeff(RG)

    SW, SW_dd, SW_cc, SW_cc_list = {}, {}, {}, []
    pr1 = tuple(pr1[0:3])
    for p in pr1:
        SW[p] = smallworld_graph(V, m, p, debug=debug)
        SW_dd[p] = get_degree_distribution(SW[p])
        SW_cc[p] = get_clustering_coeff(SW[p])
    for i in xrange(0, len(pr1)):
        p = pr1[i]
        SW_cc_list.append(SW_cc[p])

    x = PrettyTable(['Graph type', 'P(rule1)', '#Vertices', '#Edges', 'min. degree', 'max. degree', 'Clustering coeff'])
    x.align['Graph type'] = 'l'         # left align
    x.align['Clustering coeff'] = 'r'   # right align
    x.add_row(['Random', '-', RG.order(), RG.size(), min(RG.degree()), max(RG.degree()), round(RG_cc, 4)])
    for p in pr1:
        x.add_row(['Small-world', p, SW[p].order(), SW[p].size(), min(SW[p].degree()), max(SW[p].degree()), round(SW_cc[p], 4)])
    print x

    filename = 'adjmatrix_random_V'+str(V)+'_E'+str((V-m)*m)+'.out'
    write_adjmatrix_to_file(RG, filename)
    print 'writing adjacency matrix to file', filename, '...'
    for p in pr1:
        filename = 'adjmatrix_smallworld_V'+str(V)+'_m'+str(m)+'_p'+str(p)+'.out'
        write_adjmatrix_to_file(SW[p], filename)
        print 'writing adjacency matrix to file', filename, '...'

    # -------------- start plotting ---------------------------- #
    fig1 = plt.figure(figsize=(13,8))
    fig1.subplots_adjust(wspace = 0.50, hspace = 0.50)
    for i in xrange(0, min(3, len(pr1))):
        p = pr1[i]
        ax1 = fig1.add_subplot(2, 3, i+1)
        ax1.set_title('small-world graph\n degree distribution for p = ' + str(p))
        #ax1.stem(SW_dd[p].keys(), SW_dd[p].values())
        ax1.plot(SW_dd[p].keys(), SW_dd[p].values(), 'o-')
        ax1.grid()
        ax1.set_xlabel('degree'); ax1.set_ylabel('P(degree)')
        ax2 = ax1.twinx()
        try:    ax2.set_yticks(range(0, get_max_degree_count(SW[p]), get_max_degree_count(SW[p])/5) )
        except: ax2.set_yticks(range(0, get_max_degree_count(SW[p])) )
        ax2.set_ylabel('# of vertices');
    ax1 = fig1.add_subplot(236)
    ax1.set_title('random graph\n degree distribution')
    #ax1.stem(RG_dd.keys(), RG_dd.values())
    ax1.plot(RG_dd.keys(), RG_dd.values(), 'o-')
    ax1.grid()
    ax1.set_xlabel('degree'); ax1.set_ylabel('P(degree)')
    ax2 = ax1.twinx()
    try:    ax2.set_yticks(range(0, get_max_degree_count(RG), get_max_degree_count(RG)/5 ) )
    except: ax2.set_yticks(range(0, get_max_degree_count(RG)) )
    ax2.set_ylabel('# of vertices');

    ax1 = fig1.add_subplot(234)
    ax1.set_title('small-world graph\n clustering-coeff vs. P(rule1)')
    ax1.plot(pr1, SW_cc_list, 'o-')
    ax1.grid()
    ax1.axis([min(pr1)-0.1, max(pr1)+0.1, 0, max(SW_cc_list)+0.2])
    ax1.set_xlabel('P(rule1)'); plt.ylabel('clustering coeffecient')

    try:
        spam = nx.graphviz_layout(nx.empty_graph())
    except ImportError:
        print 'Warning: Couldn\'t find Python module pygraphviz; drawing with prmitive spring layout algorithm; will be slow!'
    fig2 = plt.figure(figsize=(13,8))
    for i in xrange(0, min(3, len(pr1))):
        p = pr1[i]
        ax1 = fig2.add_subplot(2, 2, i+1)
        ax1.set_title('small-world graph for p = ' + str(p))
        G = SW[p]
        try:
            pos = nx.graphviz_layout(G, prog='twopi', root='V3', args='')
        except ImportError:
            pos = nx.spring_layout(G)
        nx.draw_networkx_nodes(G, pos, node_size=1, alpha=1, node_color='k', with_labels=False)
        nx.draw_networkx_edges(G, pos, alpha=0.2, edge_color='b', with_labels=False)
        ax1.axis('equal')
    ax1 = fig2.add_subplot(224)
    ax1.set_title('random graph')
    G = RG
    try:
        pos = nx.graphviz_layout(G, prog='twopi', root='V3', args='')
    except ImportError:
        pos = nx.spring_layout(G)
    nx.draw_networkx_nodes(G, pos, node_size=1, alpha=1, node_color='k', with_labels=False)
    nx.draw_networkx_edges(G, pos, alpha=0.2, edge_color='b', with_labels=False)
    ax1.axis('equal')

    fileprefix = 'V'+str(V)+'_m'+str(m)
    print 'saving plots as png files ...'
    fig1.savefig('degree_distribution_'+fileprefix+'.png', dpi=72)
    fig2.savefig('graph_layout_'+fileprefix+'.png', dpi=72)

    print 'now showing plots...'
    plt.show()
    # -------------- end plotting ---------------------------- #



if __name__ == '__main__':
    try:
        V1, m1 = int(sys.argv[1]), int(sys.argv[2])
        debug1 = True if sys.argv[-1].lower() == 'debug' else None
    except:
        print 'Usage:', sys.argv[0], 'V m [debug]'
        print 'V = total vertices in the graph'
        print 'm = initial vertices in the small-world graph'
        print 'Example:', sys.argv[0], '1000 3'
        sys.exit(1)
    print 'running with V , m = ', V1, ',', m1, '(in debug mode)' if debug1 else ''
    main(V1, m1, debug1)
