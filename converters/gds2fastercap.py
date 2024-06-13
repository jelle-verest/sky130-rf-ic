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
# Write result to polygon list for the FastModel parasitics extraction

# CAVEATS:
#   This file is under construction and makes some (reasonable) assumptions, 
#   such as (1) a port is always a polygon on purpose 16, is always has a label 
#   name on purpose 5, there are no overlapping ports, port pairs are denoted
#   by port_[port number][p/m]. This converter still a work in progress. 
#   Currently, only single layer coils without center taps are supported.

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

 # as found in [1]
stack_bottom = {
"67":"0.9361",
"68":"1.3761",
"69":"2.0061",
"70":"2.7861",
"71":"4.0211",
"72":"5.3711"
}

 # as found in [1]
stack_top = {
"67":"1.0361",
"68":"1.7361",
"69":"2.3661",
"70":"3.6311",
"71":"4.8661",
"72":"6.6311"
}

# unit resistivity of the substrate, as given by Tim Edwards. This is allegedly in a document, which is not cited. See this as a ball-park figure [3].
rho_subs = 4400*2; # Ohm/square


 # Equivalent resistivity calculated using rho = R*A/l, with parasitic
 # resistance found in [2], in [Ohm.um]
layer_resistivities = {
"67":"1.28e-12",
"68":"4.50e-14",
"69":"4.50e-14",
"70":"3.97e-14",
"71":"3.97e-14",
"72":"3.59e-14"
}

# get layername/materialname from GDSII layer number 
def layernum2layername (num, id):
    if(id==16) or (id==20):
        layername = layermapping_metal.get(str(num),"unknown")
    if(id==44):
        layername = layermapping_via.get(str(num),"unknown")
    return layername
    
def outer_product_2d(A, B):
    return A[0]*B[1]-A[1]*B[0]

def in_triangle(pt, a, b, c):
    d1 = outer_product_2d(a-pt, b-pt)
    d2 = outer_product_2d(b-pt, c-pt)
    d3 = outer_product_2d(c-pt, a-pt)
    
    has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
    has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
    
    return not (has_neg and has_pos)

# recursive triangulation
def triangulate(pts):
    
    end = len(pts)-1
    
    # take 1st pnt and assume 2nd
    A = pts[0]
    B = pts[1]
    
    # choose 3rd by min dist
    rem_pnt = []

    dist_1 = sum(pow(pts[2]-A,2) + pow(pts[2]-B,2))
    dist_2 = sum(pow(pts[end]-A,2)+pow(pts[end]-B,2))
    if dist_1 < dist_2:
        C = pts[2]
        rem_pnt = B
    else:
        C = pts[end]
        rem_pnt = A  
        
    # check if points are inside
    point_in_triangle = False
    for point in pts:
        if ( (point == A).any() and 
         (point == B).any() and
         (point == C).any() ):
            in_triangle(point, A, B, C)
            # print("point in triangle found!")
            point_in_triangle = True
    
    # check if det < 0
    if (outer_product_2d(B-A, C-A) < 0) or point_in_triangle:
        #print("assumed wrongly")
        # redo calculations
        A = pts[end]
        B = pts[0]

        dist_1 = sum(pow(pts[1]-A,2) + pow(pts[1]-B,2))
        dist_2 = sum(pow(pts[end-1]-A,2)+pow(pts[end-1]-B,2))

        # check distances
        if dist_1 < dist_2:
            C = pts[1]
            rem_pnt = B
        else:
            C = pts[end-1]
            rem_pnt = A  
    
    triangle = [A, B, C]
    
    new_pts = []
    for x in pts:
        if not ((x == rem_pnt).all()):
            new_pts.append(x)
    return [new_pts, triangle]
    
# ============= main ===============

if len(sys.argv) >= 2:
    input_name = sys.argv[1]
    print("Input file: ", input_name)
    
    output_name = Path(input_name).stem + "_out_fastercap.qui"
    output_file = open(output_name, 'w')
    
    input_library = gdspy.GdsLibrary(infile=input_name)
    
    # evaluate only first top level cell
    cell = input_library.top_level()[0]
    print(cell)
    
    output_file.write("* " + str(cell) + '\n')
    output_file.write("*    automatically generated using gds2FasterCap.py\n")
    output_file.write("*    contact: j.n.g.w.verest@tue.nl\n")
    
    cell.flatten(single_layer=None, single_datatype=None, single_texttype=None)
    
    # default settings
    output_file.write(".units uM\n\n")
    
    # find pins & labels
    max_dimension = 0
    ports = []
    for layer_to_extract in layerlist:
        print("Evaluating layer ", str(layer_to_extract))
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
                print("Port-label pair found! \tPrt: " + str(mean_pos) + "\tLab: "
                + str(chosen_lab.position))
                ports.append( (chosen_lab.text, layer_to_extract, mean_pos) )




    # find the paths
    paths = cell.get_paths()
    


    int_output_label = 0
        
    for path in paths:
        
        pts = path.get_polygons()[0]
        coords = pts
        
        # create geometry
        
        # top side
        output_file.write("\n* TOP " +str(layernum2layername(path.layers[0],20))+ "\n")
        for i in range(len(coords)-2):
            [coords, triangle] = triangulate(coords)
            
            # round all triangle points            
            output_file.write("T B "
            +str(round(triangle[0][0],3))+" "
            +str(round(triangle[0][1],3))+" "
            +str(stack_top.get(str(path.layers[0])))+" " 
            +str(round(triangle[1][0],3))+" "
            +str(round(triangle[1][1],3))+" "
            +str(stack_top.get(str(path.layers[0])))+" " 
            +str(round(triangle[2][0],3))+" "
            +str(round(triangle[2][1],3))+" " 
            +str(stack_top.get(str(path.layers[0])))
            +"\n")
        output_file.write("\n* BOTTOM " +str(layernum2layername(path.layers[0],20))+ "\n")
        coords = pts    
        for i in range(len(coords)-2):
            [coords, triangle] = triangulate(coords)
            
            # round all triangle points            
            output_file.write("T B "
            +str(round(triangle[0][0],3))+" "
            +str(round(triangle[0][1],3))+" "
            +str(stack_bottom.get(str(path.layers[0])))+" " 
            +str(round(triangle[1][0],3))+" "
            +str(round(triangle[1][1],3))+" "
            +str(stack_bottom.get(str(path.layers[0])))+" " 
            +str(round(triangle[2][0],3))+" "
            +str(round(triangle[2][1],3))+" " 
            +str(stack_bottom.get(str(path.layers[0])))
            +"\n")
        output_file.write("\n* SIDES " +str(layernum2layername(path.layers[0],20))+ " (except for connections)\n")
    
    
        # find port indices
        
        port_indices = []
        
        for port in ports:
            min_dist1 = 99999999
            min_dist2 = 99999999
            ind1 = -1
            ind2 = -1
        
            for i in range(0, len(pts)-1):
                if (sum(pow(pts[i]-port[2],2)) < min_dist1):
                    
                    if (sum(pow(pts[ind1]-port[2],2)) < min_dist2):
                        ind2 = ind1
                        min_dist2 = sum(pow(pts[ind2]-port[2],2))
                    ind1 = i
                    min_dist1 = sum(pow(pts[i]-port[2],2))
                else:
                    if (sum(pow(pts[ind1]-port[2],2)) < min_dist1):
                        ind2 = i
                        min_dist2 = sum(pow(pts[i]-port[2],2))
                        
            port_indices.append([ind1, ind2])
        
        min_indices = []
        for x in port_indices:
            min_indices.append(min(x))
    
        for i in range(0, len(pts)-1):
            if (i not in min_indices):
                output_file.write("Q B " 
                +str(round(pts[i][0],3))+" "
                +str(round(pts[i][1],3))+" "
                +str(stack_bottom.get(str(path.layers[0])))+" "
                +str(round(pts[i+1][0],3))+" "
                +str(round(pts[i+1][1],3))+" "
                +str(stack_bottom.get(str(path.layers[0])))+" "
                +str(round(pts[i+1][0],3))+" "
                +str(round(pts[i+1][1],3))+" "
                +str(stack_top.get(str(path.layers[0])))+" "
                +str(round(pts[i][0],3))+" "
                +str(round(pts[i][1],3))+" "
                +str(stack_top.get(str(path.layers[0])))+"\n")
            else:
                output_file.write("Q " + str(ports[min_indices.index(i)][0]) + " "
                +str(round(pts[i][0],3))+" "
                +str(round(pts[i][1],3))+" "
                +str(stack_bottom.get(str(path.layers[0])))+" "
                +str(round(pts[i+1][0],3))+" "
                +str(round(pts[i+1][1],3))+" "
                +str(stack_bottom.get(str(path.layers[0])))+" "
                +str(round(pts[i+1][0],3))+" "
                +str(round(pts[i+1][1],3))+" "
                +str(stack_top.get(str(path.layers[0])))+" "
                +str(round(pts[i][0],3))+" "
                +str(round(pts[i][1],3))+" "
                +str(stack_top.get(str(path.layers[0])))+"\n")


    # vias
    # TODO: adding all individual vias is expensive; it creates unnecessary 
    # polygons, a simple bounding box will also suffice.
    output_file.write("\n VIAS "  
    + str(layernum2layername(path.layers[0],44)) )    
    polygons = cell.get_polygons(by_spec=True)
    
    for layer in layerlist:
        vias_layer = polygons.get( (layer, 44) )
        if vias_layer is None:
            continue
        for via_pillar in vias_layer:
            if via_pillar is None:
                continue
            for i in range(len(via_pillar)):
                if i is None:
                    continue
                                    
                output_file.write("Q B "
                +str(round(via_pillar[i-1][0],3))+" "
                +str(round(via_pillar[i-1][1],3))+" "
                +str(stack_bottom.get(str(layer+1)))+" "
                +str(round(via_pillar[i][0],3))+" "
                +str(round(via_pillar[i][1],3))+" "
                +str(stack_bottom.get(str(layer+1)))+" "
                +str(round(via_pillar[i][0],3))+" "
                +str(round(via_pillar[i][1],3))+" "
                +str(stack_top.get(str(layer)))+" "
                +str(round(via_pillar[i-1][0],3))+" "
                +str(round(via_pillar[i-1][1],3))+" "
                +str(stack_top.get(str(layer)))+"\n")
    
    
    

    # stack
    polys = cell.get_polygons()
    flat_list = []
    for xs in polys:
        for x in xs:
            flat_list.append(x)
    # maximum length in any direction
    md = np.sqrt(max(np.sum( np.square(flat_list), axis=1)))
    md = 2*round(md, -1)
    md = str(md)
    
    output_file.write("D SiO2 1 3.9 0 0 0 0 0 100\n")
    
    # dielectric file
    output_file.write("\nEND\n\n* dielectric geometry\n")
    output_file.write("FILE SiO2\n")
    output_file.write("Q cube -"+md+" -"+md+" 0       "+md+" -"+md+" 0       "+md+" -"+md+" 11.8834 -"+md+" -"+md+" 11.8834 \n")
    output_file.write("Q cube  "+md+"  "+md+" 0       "+md+"  "+md+" 0       "+md+"  "+md+" 11.8834  "+md+" -"+md+" 11.8834 \n")
    output_file.write("Q cube  "+md+"  "+md+" 0      -"+md+"  "+md+" 0      -"+md+"  "+md+" 11.8834  "+md+"  "+md+" 11.8834 \n")
    output_file.write("Q cube -"+md+"  "+md+" 0      -"+md+" -"+md+" 0      -"+md+" -"+md+" 11.8834 -"+md+"  "+md+" 11.8834 \n")
    output_file.write("Q cube -"+md+" -"+md+" 0       "+md+" -"+md+" 0       "+md+"  "+md+" 0       -"+md+"  "+md+" 0 \n")
    output_file.write("Q cube -"+md+" -"+md+" 11.8834 "+md+" -"+md+" 11.8834 "+md+"  "+md+" 11.8834 -"+md+"  "+md+" 11.8834 \n")
    
    output_file.write("END")
    output_file.close()
    
else:
    print ("Usage: gds2FasterCap.py [gds_file]")


# References:
# [1]   https://skywater-pdk.readthedocs.io/en/main/rules/assumptions.html#process-stack-diagram
# [2]   https://skywater-pdk.readthedocs.io/en/main/rules/rcx.html#resistance-values, in “SKY130 Stackup Capacitance Data” spreadsheet.
# [3] https://open-source-silicon.slack.com/archives/C016HUV935L/p1704550228823649?thread_ts=1704545442.597049&cid=C016HUV935L
