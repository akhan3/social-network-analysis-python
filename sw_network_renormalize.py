import networkx as nx
import matplotlib.pyplot as plt
import random
import sys
from math import ceil

TAB = '  '
fig = plt.figure()

def clustering_coeff(G):
    cc = []
    for n in G.degree_iter():
        node, deg = n
        node_subgraph = G.subgraph(G.neighbors(node))
        num_e_sub = node_subgraph.number_of_edges()
        try:
            cc.append(2.0 * num_e_sub / deg / (deg-1))
        except ZeroDivisionError:
            cc.append(1)  # convert 0/0 to 1
        #print node, ':', num_e_sub, deg, cc[-1]
    cc_avg = sum(cc)/len(cc)
    #print 'Average CC:', cc_avg
    return cc_avg

def get_adjmatrix(G):
    ans = ''
    d = nx.convert.to_dict_of_dicts(G)
    nodes_all = G.nodes()
    for n in d:
        #ans += n + ': '
        for n2 in nodes_all:
            if n2 in d[n].keys():
                ans += '1 '
            else:
                ans += '0 '
        ans += '\n'
    return ans

def write_adjmatrix_to_file(G, filename):
    print 'writing adjacency matrix to file randomgraph_adjmatrix.txt...'
    adjmatrix = get_adjmatrix(G)
    print adjmatrix
    f = open(filename, 'w')
    f.write('# Random graph with '+ str(V) + ' vertices and ' + str(E) + ' edges\n\n')
    f.write(adjmatrix)
    f.close()

def degree_distribution(G, fig = None):
    degree_all = G.degree()
    degree_range = range(0, max(degree_all)+1)
    degree_hist = []
    degree_pmf = []
    for i in degree_range:
        degree_hist.append(degree_all.count(i))
    for i in degree_hist:
        degree_pmf.append(i*1.0/sum(degree_hist))
    if fig != None:
        degree_fig = fig.add_subplot(1, 2, 2)
        degree_fig.stem(degree_range, degree_pmf)
        plt.xlim(-1, degree_range[-1]+1)
        degree_fig.set_title('Nodes\'s degree distribution')

def random_graph(V, E):
    if E not in range(int(ceil(V/2.0)), V*(V-1)/2+1):
        print 'BAD INPUT: cannot generate a graph with', V, 'vertices and', E, 'edges!'
        sys.exit(1)
    print 'generating random graph with', V, 'vertices and', E, 'edges...'
    G = nx.Graph()
    for n in xrange(0, V):
        G.add_node('n'+str(n))
    nodes_all = G.nodes()
    while G.number_of_edges() != E:
        n1, n2 = None, None
        while n1 == n2: # avoiding self loops
            n1 = random.choice(nodes_all)
            n2 = random.choice(nodes_all)
        G.add_edge(n1, n2)
    G_original = G.copy() # save a copy of original
    print 'connecting orphan nodes...'
    nodes_orphan = []
    for n in G:
        if G.degree(n) == 0: # if orphan node
            nodes_orphan.append(n)
    nodes_nonorphan = list(set(nodes_all).difference(nodes_orphan))
    for n in nodes_orphan:
        while True:       # make sure all the neighbors have degree > 1
            while True:   # make sure the selected node has degree > 1
                n1 = random.choice(nodes_nonorphan)
                if G.degree(n1) > 0: break  # make sure the selected node has degree > 0 (CHANGE: previously 1)
            can_delete = []
            for n2 in G.neighbors_iter(n1):
                if G.degree(n2) > 1:
                    can_delete.append(n2)
            if len(can_delete) != 0:
                n3 = random.choice(can_delete)
                G.remove_edge(n1, n3)
                G.add_edge(n, n1)
                nodes_nonorphan.append(n)
                #print n, 'is connected to', n1, '(', n1, '-x-', n3, ')'
                break     # make sure all the neighbors have degree > 1
    write_adjmatrix_to_file(G, 'randomgraph_adjmatrix.txt')
    cc = clustering_coeff(G)
    print 'Clustering Coeffecient:', clustering_coeff(G)
    fig = plt.figure()
    graph_fig = fig.add_subplot(1, 2, 1)
    graph_fig.set_title('Random graph with '+ str(V) + ' vertices and ' + str(E) + ' edges')
    nx.draw(G)
    degree_distribution(G, fig)
    plt.show()
    print
    return cc


def smallworld_graph(V, m, p):
    if m > V:
        print 'BAD INPUT: initial vertices', m, 'cannot be larger than total vertices', V, '!'
        sys.exit(1)
    print 'generating small world graph with', m, 'initial and', V, 'total vertices...'
    G = nx.Graph()
    for n in xrange(0, m):    # adding initial m vertices
        G.add_node('n'+str(n))
    ### adding (m+1)th vertices and connect it to initial m vertices
    ##G.add_node('n'+str(m))
    ##print 'n'+str(m)
    ##for e in xrange(0, m):  # adding m edges for (m+1)th vertex
        ##G.add_edge('n'+str(m), 'n'+str(e))
    # adding the rest of (V-m-1) vertices
    for n in xrange(m+1, V):
        current_vertex = 'n'+str(n)
        G.add_node(current_vertex)
        print current_vertex
        prev_chosen_vertices = []
        for e in xrange(0, m):  # adding m edges for the current vertex
            if e == 0:    # first edge always with rule1
                r = 0
            else:         # subsequent edges with either rule1 or rule2
                r = random.random()
            if r < p: # Rule1
                chosen_vertex = rule1(G, current_vertex, prev_chosen_vertices)
            else:     # Rule2
                chosen_vertex = rule2(G, current_vertex, prev_chosen_vertices)
            G.add_edge(current_vertex, chosen_vertex)
            prev_chosen_vertices.append(chosen_vertex)
    print '----------------------------------------------------'
    print G.number_of_nodes(), G.number_of_edges()
    ##draw_graph(G)
    #graph_fig = fig.add_subplot(1, 1, 1)
    #nx.draw(G)
    #plt.show()


def rule1(G, current_vertex, prev_chosen_vertices = []):
    print TAB, 'Rule1',
    degree_dict = {}
    degree_pmf = {}
    # buidling degree_pmf
    for n in G.degree_iter():
        degree_dict[n[0]] = n[1]
    if sum(degree_dict.values()) == 0:
        print 'FIRST_DOWN'
        for n in degree_dict:
            degree_pmf[n] = 1.0/len(degree_dict)
    else:
        for n in degree_dict:
            degree_pmf[n] = 1.0*degree_dict[n]/sum(degree_dict.values())
    while True:   # make sure to select a distint vertex
        for n in degree_pmf:
            if n != current_vertex and degree_pmf[n] == 0:
                print 'renormalizing...',
                degree_pmf = renormalize(dict(degree_pmf), 10)
                break
        cumul_prob = 0
        r = random.random()
        for n in degree_pmf:
            cumul_prob += degree_pmf[n]
            if r < cumul_prob:
                #print TAB*2, cumul_prob-degree_pmf[n], '<', r, '<', cumul_prob, '~', n,
                w = n
                break
        print w,
        if w not in prev_chosen_vertices and w != current_vertex:
            break
    print
    return w

def rule2(G, current_vertex, prev_chosen_vertices):
    print TAB, 'Rule2',
    while True:       # make sure rule2 is met
        u = random.choice(G.nodes())
        break
        #if u in G.neighbors(w):
    print
    return u

def renormalize(pmf, k):
    # find zero probabilities
    z = []
    for n in pmf:
        if pmf[n] == 0:
            z.append(n)
    # find non-zero probabilities
    n = list(set(pmf.keys()).difference(z))
    # find minimum non-zero probability and divide by k
    n_pmf = []
    for i in n:
        n_pmf.append(pmf[i])
    minbyk = 1.0 * min(n_pmf) / k
    # update pmf
    for i in n:
        pmf[i] = pmf[i] * (1-minbyk)
    for i in z:
        pmf[i] = minbyk / len(z)
    return pmf

def draw_graph(G, subplot):
    nx.draw(G)



def main(V, E, m, p):
    #pmf = {'a':0.5, 'b':0, 'c':0.3, 'd':0, 'e':0.2}
    #print pmf
    #renormalize(pmf, 10)
    #print pmf

    #random.seed(6989678)
    #random.setstate((3, (2147483648L, 3979802604L, 2946318591L, 3420361768L, 2272154636L, 2887807158L, 950091802L, 909739676L, 4197541076L, 1099938467L, 969138513L, 3787251873L, 1048936368L, 3766488719L, 4073579576L, 1494693236L, 2811915126L, 2887961764L, 795595064L, 599194672L, 2944304247L, 3133659946L, 2108727395L, 146942132L, 2930580032L, 4029467206L, 3476686202L, 1723899667L, 3564011346L, 2969019178L, 3638639333L, 603600960L, 3611996904L, 1475552843L, 4150218740L, 1662390172L, 1596250353L, 1047371075L, 2880248537L, 210943886L, 4167505012L, 227832918L, 1433497917L, 1969110040L, 2100862042L, 3628050519L, 1299142636L, 2529396995L, 769038451L, 328302582L, 2466483594L, 1392983655L, 466258906L, 3937340421L, 3230786510L, 2627758998L, 3985163342L, 385312614L, 2437293476L, 985780677L, 3521732970L, 3044567346L, 765966671L, 245260737L, 1532868391L, 1972850734L, 189176360L, 2322941445L, 3766041320L, 2167956381L, 3284425029L, 1800767550L, 3801184182L, 1313125264L, 1043160329L, 3014419559L, 30448983L, 3932434841L, 2207773053L, 2845412081L, 178278478L, 123328749L, 3797557452L, 1611811053L, 1973008766L, 3830757447L, 3659792260L, 1458695956L, 2357926125L, 1467620534L, 589457002L, 477898933L, 2152891389L, 833410434L, 154906668L, 2862188273L, 2432014877L, 1257797442L, 1694533416L, 4207132005L, 4176716985L, 1687448270L, 922534281L, 1282112219L, 2463911092L, 2070597240L, 508905293L, 2757434376L, 2799443901L, 2065140296L, 629275153L, 2053172290L, 1477347308L, 3679267094L, 991520310L, 2492512052L, 2037655870L, 2765477037L, 714765809L, 1391075346L, 693561878L, 2232648941L, 1130598377L, 155681699L, 653969394L, 1133311662L, 1396765015L, 3681486231L, 4216710107L, 4112977881L, 1046735067L, 1079927981L, 3234917229L, 1056153751L, 2152001943L, 2384826567L, 4107319735L, 4034960334L, 3309586449L, 4052856080L, 1685018900L, 3897274179L, 1724913713L, 1126726710L, 4047359280L, 1836850241L, 2821495033L, 751807035L, 762891537L, 1999461828L, 2675206341L, 3475690525L, 2540056600L, 977293705L, 725212760L, 2062843207L, 4261743292L, 1769233887L, 3399923352L, 1508344312L, 1189686325L, 2148316010L, 303238411L, 4294479171L, 3111826400L, 2997994750L, 424334120L, 2696016132L, 1540498824L, 2320621086L, 173098922L, 1185931309L, 3265608278L, 2076742727L, 2653928552L, 787362338L, 1667579822L, 3652066138L, 583792322L, 3631912237L, 4189224664L, 3717739958L, 3797322202L, 2492584751L, 1169769884L, 1917179351L, 917855917L, 248530471L, 351545914L, 2167314122L, 918461079L, 1110999930L, 3514440946L, 1555310948L, 2378316891L, 1811684335L, 3148990119L, 723604439L, 1710787331L, 1727402106L, 3519012490L, 50859096L, 4083225369L, 538913573L, 240902778L, 3336113207L, 2638407546L, 1305394578L, 2346616424L, 1545933225L, 1805221196L, 2068559003L, 1702468728L, 1676709313L, 3861850445L, 2531045867L, 3938789380L, 471152940L, 1372918313L, 1560468402L, 697761999L, 2630936087L, 420166495L, 564556575L, 2115691L, 2084195219L, 3326812116L, 147072447L, 269099649L, 3452835859L, 2252760214L, 3411187732L, 2405695134L, 682119631L, 444842279L, 553532017L, 4096019451L, 507400234L, 3330436473L, 1862463229L, 3292364929L, 587389963L, 3870961960L, 2919863192L, 1142609404L, 2213449981L, 1860102467L, 2925801904L, 3407022729L, 1214204114L, 2509855442L, 3005679048L, 4070284438L, 2433557521L, 329344568L, 3389171503L, 2221928226L, 2788060070L, 4259223485L, 3435815430L, 453011511L, 1041600107L, 2458068729L, 249974255L, 955935954L, 1219210187L, 2273022038L, 1013858202L, 675040727L, 3514823023L, 2216015570L, 1957762148L, 985059654L, 1770720865L, 1498700381L, 212504094L, 2264331916L, 4095596474L, 211496637L, 3626277298L, 3448276065L, 3246767251L, 1814741378L, 311078577L, 3928859447L, 1002424389L, 424092530L, 2461131327L, 2107697172L, 1209990082L, 2737845641L, 2881268249L, 990586554L, 1028889368L, 552588176L, 2251216491L, 514083776L, 2012471223L, 919975823L, 758443027L, 328630522L, 2200711874L, 4182301025L, 382118961L, 1741731367L, 3710478568L, 4229615917L, 3175172451L, 2510082341L, 3524783041L, 4276100645L, 3380522018L, 689918296L, 837143117L, 2966108762L, 2947759750L, 2935984991L, 190885840L, 1486773128L, 2257354864L, 1944283084L, 2016061077L, 46997102L, 425170406L, 4218963536L, 1849165106L, 1846009232L, 3364907107L, 845432753L, 1024162868L, 1678685410L, 2032956903L, 3534606652L, 4264996913L, 48550210L, 2528599177L, 1861821195L, 3803663854L, 2463144470L, 3525393424L, 853518091L, 1814409760L, 2483850557L, 1355419892L, 3791512800L, 3623034537L, 3492162566L, 3416423883L, 3538988878L, 3599329858L, 3524586544L, 912715570L, 1509405449L, 2293466679L, 2246092264L, 357043114L, 1130057568L, 3751824151L, 937324872L, 1916401518L, 2300894133L, 2358670053L, 979959648L, 1226270036L, 1340504953L, 2518746479L, 2722796590L, 284564683L, 1346878197L, 2444209226L, 4204331635L, 4142205348L, 778762787L, 1028758484L, 2493588781L, 502037345L, 3107152937L, 3321650869L, 19661461L, 1070773189L, 2562321795L, 3067464268L, 537364383L, 880003398L, 3654394742L, 1623650190L, 443333058L, 4242550744L, 4017709692L, 4136064813L, 246524076L, 2068365252L, 3195001302L, 264228869L, 3999374169L, 2975985837L, 3299634630L, 1660136669L, 3499372244L, 1624357767L, 1409034756L, 4074941144L, 1882439589L, 123233320L, 2157094821L, 3199988618L, 2754378061L, 2347437539L, 2167501343L, 1037384796L, 949859244L, 3033242710L, 444778441L, 1194075124L, 1393044462L, 758462361L, 3600301911L, 966957127L, 2427244219L, 3791153282L, 4220434027L, 1530662500L, 1960501159L, 953698507L, 291316936L, 3674903280L, 2444170488L, 720864111L, 1145413251L, 3101137741L, 330215241L, 1946571478L, 82638496L, 3829737583L, 2478075986L, 3315898307L, 3295905647L, 398418963L, 3749171521L, 2921453086L, 3797575740L, 3547785526L, 2335491133L, 682204126L, 2731446193L, 4209714312L, 944870892L, 4201910494L, 2517798533L, 4147547958L, 2782979533L, 2506742152L, 1801475988L, 1177156988L, 2260376744L, 2288807115L, 2784042537L, 1919252770L, 1706938361L, 232122763L, 4084895486L, 414462999L, 1319315976L, 3748015407L, 1360766702L, 3676861430L, 411632156L, 3817961431L, 3430025978L, 2077254055L, 2826209163L, 2245112223L, 1928913828L, 2637017361L, 1723417999L, 924350147L, 4142831227L, 589008933L, 2370377228L, 1734459491L, 2653140134L, 3538020524L, 912627172L, 1801494959L, 3962497933L, 556004722L, 4287373740L, 4026879587L, 3476184556L, 1242315102L, 3326801685L, 3040056560L, 1530837512L, 1777923939L, 629666526L, 2847103989L, 4087103235L, 3417141481L, 3550228499L, 3678327637L, 3705876458L, 3934688598L, 4192991943L, 3409401449L, 531723711L, 175553476L, 834519029L, 2504180275L, 3575927623L, 1186897377L, 2782400865L, 2889110351L, 3755102262L, 2297008367L, 4050042574L, 1701675267L, 4059382729L, 4268182188L, 1910812596L, 3720425743L, 3049539760L, 2664851816L, 2489063858L, 2540825093L, 1731682018L, 4201791382L, 1466252245L, 2641772507L, 2824594679L, 2574853180L, 1477974192L, 4246881183L, 2233566268L, 1863043308L, 1231733829L, 4100088905L, 2042456565L, 3507395292L, 942199611L, 3025491508L, 4260359504L, 1431904834L, 3868221735L, 78027560L, 1055282499L, 950485408L, 2622090460L, 1433431999L, 1554308826L, 2613328761L, 2655328406L, 3820678327L, 1360150276L, 3063456683L, 669883013L, 467788297L, 2760236673L, 3381183077L, 1693376508L, 1593143734L, 2034578212L, 2791214253L, 4435542L, 1047976146L, 3844727995L, 1000937402L, 3436802345L, 2178948167L, 2702355759L, 4129814883L, 3109391572L, 2252339741L, 389919257L, 758281817L, 3357829746L, 4140735962L, 2482147246L, 1228337669L, 4056405157L, 1912127L, 3931031507L, 1846060900L, 352967363L, 4271390979L, 655992821L, 3454857005L, 3825576119L, 3071382909L, 1871669012L, 3420769233L, 3354668452L, 2296115118L, 1874118450L, 1047669709L, 661110902L, 3031465137L, 1535054202L, 3072017852L, 4145371957L, 1331828473L, 1049267998L, 3801754813L, 1723380588L, 1656287596L, 3239183879L, 2642075067L, 964980591L, 1228729937L, 4253875197L, 3317975360L, 651984876L, 727409607L, 316200214L, 4080276769L, 497132068L, 131893731L, 829234098L, 2057236316L, 1736865763L, 364149773L, 4266117478L, 3609136976L, 3104393518L, 2696891940L, 624L), None))
    #print random.getstate()
    smallworld_graph(V, m, p)
    #mc_count = 100
    #cc_avg = 0
    #for i in xrange(1, mc_count+1):
        #this_cc = random_graph(V, E)
        #cc_avg = ((i-1) * cc_avg + this_cc) / i
        #print 'Running-average Clustering Coeffecient:', cc_avg
    #print
    #print
    #print 'Monte Carlo simulation count:', mc_count
    #print 'Average Clustering Coeffecient:', cc_avg

if __name__ == '__main__':
    V, E, m, p = 1000, 2991, 3, 0.7
    V, E, m, p = 10, 12, 3, 0.7
    main(V, E, m, p)
