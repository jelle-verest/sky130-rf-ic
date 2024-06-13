# sky130-rf-ic
A demonstration of a 10GHz VCO in SKY130, produced using open source tools. 
This is part of an effort to teach IC design courses using both open source and simple to use tools.

## unique to this project
1. the inclusion of Klayout
2. a GDS to FastFieldSolver file converter

## toolchain
The circuit is designed in Xschem, simulated using NGspice. 
The layout is produced in both Magic and Klayout; The former contains all PCells and parasitic extraction, while the latter is more user friendly. 
DRC check is performed in KLayout and LVS in netgen.
RC extraction in MAGIC and EM extraction in FastFieldSolver.

Most of this toolchain is already described in other projects and is actively used by the majority of the SKY130 community, with exception of Klayout and FastFieldSolver, which are novel in this project.

## aim
The Integrated Circuits research group in the Eindhoven University of Technology wants to extend IC design education by utilising the open source SKY130 PDK in their courses.
The courses are not only aimed at IC design students, but also those from adjacent fields. Because of this, it is important to smooth the learning curve.
The standard industry used tool package for IC design is Cadence Virtuoso, which is notoriously difficult to use.

Therefor, this project aims to design an RFIC block as streamlined as possible, using SKY130 and open source software.

## Inductor design
A fully customizable PCell library has been written in Klayout's macro editor with the following content:
* a single turn square inductor
* a single turn octagonal inductor
* a 2 turn square inductor
* a 2 turn octogonal inductor

The solvers in the FastFieldSolvers package can calculate an equivalent circuit representation.
These solvers are the FastHenry2 solver, which is able to extract series resistances, self inductances and mutual inductances, and FasterCap, which is able to extract capacitances between nodes. 
These solvers require their own input file, which is generated using the custom made "gds2FastHenry" and "gds2FasterCap" converters. The outputs can then be combined together manually.


## Future goals
1.  Extensive documentation; because this project is still under construction, the documentation is not yet thorough. After finishing this project, a more extensive documentation will be written.
2.  More robust file conversion; Currently, the converters expect a certain format, which is made using the PCells in the IndLib. These are made using paths, which is more natural for the FastHenry input.
3.  polygon-to-path conversion algorithm; FastHenry expects current paths instead of polygons. An algorithm for determining current paths from a polygon will have to be made.
4.  all-in-one gds to equivalent circuit spice file converter; Currently the converters only convert a GDS file to the FastFieldSolvers input files, but this project aims to create a converter which accepts a GDS, converts it, runs it in the solvers and returns a SPICE file, ready for use in circuit simulators.
5.  Integration in Klayout; The extended goal of this project is to have an inductor PCell library which will automatically show the inductance, quality factor and self resonance frequency in the editor. 
