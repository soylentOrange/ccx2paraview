© Ihor Mirzov, UJV Rez, May 2019

Tested in ccx_2.15 for:

- element types:
    - S3, S6, S4, S8
    - CPE3, CPE4, CPS3, CPS4
    - C3D15, C3D20
- output variables:
    - NDTEMP
    - STRESS
    - DISP
    - FORC
    - PE
    - SDV
    - TOSTRAIN
- analysis type:
    - static
    - coupled-temperature displacement
    - visco
    - frequency

<br/><br/>



# ccx2paraview.py

Converts CalculiX .frd-file to view and postprocess calculation results in [Paraview](https://www.paraview.org/).  
For each time step generates separate file - it makes possible to animate time history.  

To convert to legacy ASCII .vtk-format, run command:

    python3 ccx2paraview.py -frd jobname -fmt vtk

To convert to modern XML .vtu-format, run command:

    python3 ccx2paraview.py -frd jobname -fmt vtu

By default script will skip ERROR fields generated by CalculiX. So mentioned commands are equivalent to:

    python3 ccx2paraview.py -frd jobname -fmt vtk -skip 1
    python3 ccx2paraview.py -frd jobname -fmt vtu -skip 1

If you'd like to leave CacluliX ERROR fields, run commands with '-skip 0' argument:

    python3 ccx2paraview.py -frd jobname -fmt vtk -skip 0
    python3 ccx2paraview.py -frd jobname -fmt vtu -skip 0

<br/><br/>



# Known bug

For field output in your Calculix .inp-file always use NSET parameter. In this case conversion goes well. For example:

    *NODE FILE, NSET=ALL
        NT, U
    *EL FILE, NSET=ALL
        S, PEEQ, SDV

<br/><br/>



# Tests

Folders *tests-elements* and *tests-examples* contain .inp-tasks + .frd-calculation + .vtk and .vtu convertion results.  
Needed for the development process.  *tests-examples* are taken directly from [Calculix examples](http://www.dhondt.de/ccx_2.15.test.tar.bz2).

Run all tests with command:

    python3 tests.py

<br/><br/>



# TODO

- Generate invariants, principal min/max and equivalents for stresses and strains.
- Test converter for all the Calculix examples.
- Windows Line endings.
