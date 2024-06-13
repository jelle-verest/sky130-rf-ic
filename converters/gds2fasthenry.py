# Copyright 2023 J.N.G.W. Verest
# j.n.g.w.verest@tue.nl
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#    https://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Extract objects on all metal layers (LI - Metal5) in GDSII file
# Write result to polygon list for the FastHenry2 induction extraction

# CAVEATS:
#   This file is under construction and makes some (reasonable) assumptions, 
#   such as (1) a port is always a polygon on purpose 16, is always has a label 
#   name on purpose 5, there are no overlapping ports, port pairs are denoted
#   by port_[port number][p/m]. This converter still a work in progress. 
#   Coming features:
#    -  Automated spice file re-interpretation for integration with FasterCap
#    -  T junction recognition
#    -  input not generated using Klayout IndLib

# File history: 
# Initial version 


import gdspy
import sys
import numpy as np
from pathlib import Path



# SKY130 data

# layers to be examined  
layerlist = [
67, # LI
68, # M1
69, # M2
70, # M3
71, # M4
72  # M5
]

# list of purpose to evaluate
purposelist = [
16, # pin
20, # drawing
44, # via
]

# list of materialnames for each GDSII layer number
layermapping_metal = {
"67":"LI",
"68":"Metal1",
"69":"Metal2",
"70":"Metal3",
"71":"Metal4",
"72":"Metal5"
}
layermapping_via = {
"67":"Mcon",
"68":"Via1",
"69":"Via2",
"70":"Via3",
"71":"Via4"
}

 # as found in [1], center value chosen
stack_heights = {
"67":"0.9736",
"68":"1.5561",
"69":"2.1861",
"70":"3.2086",
"71":"4.4436",
"72":"6.0011"
}

 # as found in [1]
layer_heights = {
"67":"0.1",
"68":"0.36",
"69":"0.36",
"70":"0.845",
"71":"0.845",
"72":"1.26"
}

# unit resistivity of the substrate, as given by Tim Edwards. This is allegedly in a document, which is not cited. See this as a ball-park figure [3].
rho_subs = 4400; # Ohm/square


 # Equivalent resistivity calculated using rho = R*A/l, with parasitic
 # resistance found in [2], in [Ohm.um]
layer_resistivities = {
"67":"1.28",
"68":"4.50e-2",
"69":"4.50e-2",
"70":"3.97e-2",
"71":"3.97e-2",
"72":"3.59e-2"
}

via_resistivities = {
"68":0.375,
"69":0.325,
"70":0.35,
"71":0.482
}

via_widths = {
"68":0.15,
"69":0.2,
"70":.2,
"71":0.8
}

# get layername/materialname from GDSII layer number 
def layernum2layername (num, id):
    if(id==16) or (id==20):
        layername = layermapping_metal.get(str(num),"unknown")
    if(id==44):
        layername = layermapping_via.get(str(num),"unknown")
    return layername

# ============= main ===============

if len(sys.argv) >= 2:
    input_name = sys.argv[1]
    print("Input file: ", input_name)
    
    output_name = Path(input_name).stem + "out_fasthenry.inp"
    output_file = open(output_name, 'w')
    
    input_library = gdspy.GdsLibrary(infile=input_name)
    
    # evaluate only first top level cell
    cell = input_library.top_level()[0] 
    
    output_file.write("* " + str(cell) + '\n')
    output_file.write("*    automatically generated using gds2FastModel.py\n")
    output_file.write("*    contact: j.n.g.w.verest@tue.nl\n")
    
    cell.flatten(single_layer=None, single_datatype=None, single_texttype=None)
    
    # default settings
    output_file.write(".units uM\n\n")
    
    # find pins & labels
    max_dimension = 0
    ports = []
    for layer_to_extract in layerlist:
        curr_ports = cell.get_polygons(by_spec=True).get( (layer_to_extract, 16) )
        
        polys = cell.get_polygons()
        flat_list = []
        for xs in polys:
            for x in xs:
                flat_list.append(x)
        max_dimension = np.sqrt(max(np.sum( np.square(flat_list), axis=1)))
        
        
        curr_labels = cell.get_labels()
        
        if (curr_ports != None) and (curr_labels != None):

            # quick check whether num of pins == num of labels
            if len(curr_ports) != len(curr_labels):
                print("ERROR: unequal amount of ports & labels on " 
                + str(layernum2layername(layer_to_extract, 16)))
                break
        
            # append them to list
            for poly in curr_ports:
                mean_pos = np.mean(poly, axis=0)
                
                # find smallest distance label
                mindist = 99999999
                chosen_lab = None
                for o in curr_labels:
                    if mindist > sum(np.square( mean_pos - o.position )):
                        mindist = sum(np.square( mean_pos - o.position ))
                        chosen_lab = o

                # store pins
                ports.append( (chosen_lab.text, layer_to_extract, mean_pos) )
    
    
    
    # find the paths
    paths = cell.get_paths()
    
    
    index = 0
    # define nodes
    output_file.write("\n* POINTS \n")
    for path in paths:
        for pth in range(0,len(path.points)):
            output_file.write("N" + str(index)
            + " x=" + str(round(path.points[pth][0], 3))
            + " y=" + str(round(path.points[pth][1], 3))
            + " z=" + str(stack_heights.get(str(path.layers[0])))
            + "\n")
            index += 1
    
    
    chosen_node_a = -1
    chosen_node_b = -1
    # define ports
    output_file.write("\n* PORTS\n")
    for i in range(0,len(ports)):        
        # find for all ports the closest node
        mindist = 9999999
        # TODO: change this to depend on attached label
        index = 0
        for path in paths:
            for num in range(0,len(path.points)):            
                if (mindist > sum(np.square( ports[i][2] - path.points[num] ))):
                    mindist = sum(np.square( ports[i][2] - path.points[num] ))
                    if i%2 == 0:
                        chosen_node_a = index
                    else:
                        chosen_node_b = index
                index+=1
        
    output_file.write( ".external N" + str(chosen_node_a) 
    + " N" + str(chosen_node_b) + " 1\n")
   
    # make connections
    index = 0
    for path in paths:
        output_file.write("\n* EDGES PATH["+ str(paths.index(path)) +"] \n")
        for i in range(0,len(path.points)-1):
            output_file.write("E" + str(index)
            + " N"      + str(index)
            + " N"      + str(index+1)
            + " w="     + str(round(path.widths[i][0],3))
            + " h="     + str(layer_heights.get(str(path.layers[0])))    
            + " rho="   + str(layer_resistivities.get(str(path.layers[0])))
            + " nwinc=" + str(20)  
            + "\n")
            index+=1
        index+=1
    
    # via connections
        # find via group -> assume len(paths)-1 via clusters? (alternative is K-means)
            # 1. look for path ends between adjacent layers
            # 2. bounding box around
    output_file.write("\n* VIAS\n")
    for i in range(len(paths)):
        
        for j in range(i+1, len(paths)):
            if (abs(paths[i].layers[0] - paths[j].layers[0]) == 1):
                min_dist = 99999
                index_1 = -99
                index_2 = -99
                for x in range(2):
                    for y in range(2):
                        d = sum(pow(paths[i].points[-x]-paths[j].points[-y],2))
                        if (d < min_dist):
                            index_1 = -x # either 0 or -1 (start or end)
                            index_2 = -y
                            min_dist = d
                
                # bounds are in 
                    # min(x1, x2)-w  <= x <= max(x1, x2) + w
                    # min(y1, y2)-w  <= y <= max(y1, y2) + w
                width = max(paths[i].widths[index_1], paths[j].widths[index_2])
                lb_x = min(paths[i].points[index_1][0], paths[j].points[index_2][0])-width/2
                ub_x = max(paths[i].points[index_1][0], paths[j].points[index_2][0])+width/2
                lb_y = min(paths[i].points[index_1][1], paths[j].points[index_2][1])-width/2
                ub_y = max(paths[i].points[index_1][1], paths[j].points[index_2][1])+width/2
                
                vias = cell.get_polygons(by_spec=True).get( (min(paths[i].layers[0], paths[j].layers[0]), 44) )
                                
                if not vias:
                    print("WARNING: no vias connecting two adjacent layers.")
                else:
                    num_via_pillars = 0
                    cluster_sum = 0
                    for via_under_inspection in vias:
                        mean = sum(via_under_inspection)/4
                        
                        if ((mean[0] >= lb_x) 
                        and (mean[0] <= ub_x)
                        and (mean[1] >= lb_y)
                        and (mean[1] <= ub_y) ):
                            num_via_pillars += 1
                            cluster_sum += mean
                    
                    cluster_mean = cluster_sum / num_via_pillars
                    via_layer = min(paths[i].layers[0],paths[j].layers[0])
                    
                    output_file.write("N0_via" + str(i)+str(j)+
                    " x=" + str(round(cluster_mean[0], 3)) + 
                    " y=" + str(round(cluster_mean[1], 3)) + 
                    " z=" + str(stack_heights.get(str(paths[i].layers[0]))) + "\n"
                    )
                    output_file.write("N1_via" + str(i)+str(j)+
                    " x=" + str(round(cluster_mean[0], 3)) + 
                    " y=" + str(round(cluster_mean[1], 3)) + 
                    " z=" + str(stack_heights.get(str(paths[j].layers[0]))) + "\n"
                    )
                
                    output_file.write("E_via" + str(i)+str(j)+
                    " N0_via" + str(i)+str(j)+
                    " N1_via" + str(i)+str(j)+
                    " w=" + str(1) + 
                    " h=" + str(1) + 
                    " rho=" + str(via_resistivities.get(str(via_layer))/num_via_pillars) + 
                    " nwinc=1 nhinc=1 \n")
                   
                   
                    i_pt_1 = -(len(paths[i].points)-1)*index_1
                    for ind in range(i):
                        i_pt_1 += len(paths[ind].points)
                    i_pt_2 = -(len(paths[j].points)-1)*index_2
                    for ind in range(j):
                        i_pt_2 += len(paths[ind].points)
                    
                    output_file.write(".equiv N0_via"+str(i)+str(j)+" N"+str(i_pt_1)+"\n")
                    output_file.write(".equiv N1_via"+str(i)+str(j)+" N"+str(i_pt_2)+"\n")
        
   
    # simulation settings
    total_length = 0
    for path in paths:
        for i in range(0,len(path.points)-1):
            curr_point = path.points[i]
            next_point = path.points[i+1]
            
            total_length += np.sqrt( sum(pow(curr_point-next_point,2) ))
    
    
    f_max = 3e8 / (10*total_length*1e-6*np.sqrt(3.9))
    f_max = np.round(f_max, 1-int(np.floor(np.log10(f_max))))
    #print("total length of path: " + str(round(total_length,-1)) + " um")
    #print("limit the electrical length to 1/10th lambda")
    print("maximum usable frequency = " + str(f_max/1e9) + " GHz")
        # resonance rule of thumb: f_r @ 70% of 3/4 lambda
        # Graduation thesis, IC group TUe
    f_r = 0.7*0.75*3e8/(total_length*1e-6*np.sqrt(3.9))
    #print("resonance frequency estimate: f_r = " + str(int(f_r/1e9))+" GHz")
    
    gr_len = 2 * round(max_dimension, 0)
    lam = int(np.ceil(total_length / 20))
    
    # substrate
    output_file.write("\n* SUBSTRATE\n")
    output_file.write("G1\n")
    output_file.write("+ x1="+str(-gr_len)+" y1="+str(-gr_len)+" z1="+str(0)+"\n")
    output_file.write("+ x2="+str(gr_len)+" y2="+str(-gr_len)+" z2="+str(0)+"\n")
    output_file.write("+ x3="+str(gr_len)+" y3="+str(gr_len)+" z3="+str(0)+"\n")
    output_file.write("+ thick=0.1\n+ seg1="+str(lam)+" seg2="+str(lam)+"\n")
    output_file.write("+ rho="+str(rho_subs)+"\n")
    
    output_file.write("\n* SIMULATION SETTINGS\n")
    output_file.write(".freq fmin=1.000000e+06 fmax=" + str(f_max) + " ndec=1\n")
    output_file.write(".end\n\n")
    
    output_file.close()
    
else:
    print ("Usage: gds2FastHenry.py [gds_file]")


# References:
# [1]   https://skywater-pdk.readthedocs.io/en/main/rules/assumptions.html#process-stack-diagram
# [2]   https://skywater-pdk.readthedocs.io/en/main/rules/rcx.html#resistance-values, in “SKY130 Stackup Capacitance Data” spreadsheet.
# [3]   https://open-source-silicon.slack.com/archives/C016HUV935L/p1704550228823649?thread_ts=1704545442.597049&cid=C016HUV935L
