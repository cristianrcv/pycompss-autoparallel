#!/usr/bin/python

# -*- coding: utf-8 -*-

# For better print formatting
from __future__ import print_function

# Imports
from custom_value import Value

# Task imports
from pycompss.api.parallel import parallel
from pycompss.api.api import compss_wait_on


###########################################################
# MAIN WORKFLOW FUNCTION
###########################################################

@parallel()
def calculate_cm(num_objects, num_parts, num_dims, system_objects, masses):
    # Initialize object results
    system_objects_cms_position = [[Value(0) for _ in range(num_dims)] for _ in range(num_objects)]
    system_objects_mass = [Value(0) for _ in range(num_objects)]

    # Calculate CM and mass of every object in the system
    for obj_index in range(num_objects):
        # Calculate object mass and cm position
        for part_index in range(num_parts):
            # Update total object mass
            system_objects_mass[obj_index] += masses[system_objects[obj_index][part_index][0]]
            # Update total object mass position
            for dim in range(num_dims):
                system_objects_cms_position[obj_index][dim] += masses[system_objects[obj_index][part_index][0]] * \
                                                               system_objects[obj_index][part_index][1][dim]

        # Store final object CM and mass
        for dim in range(num_dims):
            system_objects_cms_position[obj_index][dim] /= system_objects_mass[obj_index] if system_objects_mass[
                                                                                                 obj_index] != Value(
                0) else Value(0)
    #
    # if __debug__:
    #     for obj_index in range(num_objects):
    #         print("Object " + str(obj_index) + " has CM in " + str(
    #             system_objects_cms_position[obj_index]) + " with mass " + str(system_objects_mass[obj_index]))
    # print("MASS AFTER G SYNC: " + str(system_objects_mass))
    # print("CMS AFTER G SYNC: " + str(system_objects_cms_position))

    # Initialize system results
    system_mass = Value(0)
    system_cm = [Value(0) for _ in range(num_dims)]

    # Calculate system CM for every object
    for obj_index in range(num_objects):
        # Update total mass
        system_mass += system_objects_mass[obj_index]
        # Update system mass position
        for dim in range(num_dims):
            system_cm[dim] += system_objects_mass[obj_index] * system_objects_cms_position[obj_index][dim]

    # Calculate system CM
    for dim in range(num_dims):
        system_cm[dim] /= system_mass if system_mass != Value(0) else Value(0)

    # Return result
    system_cm = compss_wait_on(system_cm)
    if __debug__:
        system_mass = compss_wait_on(system_mass)
        print("SYS MASS: " + str(system_mass))
        print("SYS CM: " + str(system_cm))

    return system_cm


###########################################################
# MAIN
###########################################################

def main():
    # Define system
    num_objects = 3
    num_parts = 4
    num_dims = 2

    system_objects = [[("pata", [Value(0), Value(0)]),
                       ("pata", [Value(2), Value(0)]),
                       ("pata", [Value(2), Value(2)]),
                       ("tablero", [Value(1), Value(1)])],
                      [("pata", [Value(3), Value(1)]),
                       ("pata", [Value(3), Value(2)]),
                       ("sillin", [Value(3), Value(1)]),
                       ("respaldo", [Value(3), Value(2)])],
                      [("reposapies", [Value(3), Value(3)]),
                       ("pata", [Value(3), Value(1)]),
                       ("pata", [Value(3), Value(2)]),
                       ("sillin", [Value(3), Value(1)])]
                      ]
    masses = {"pata": Value(2),
              "tablero": Value(5),
              "sillin": Value(3),
              "respaldo": Value(4),
              "reposapies": Value(1)}

    # Calculate CM
    system_cm = calculate_cm(num_objects, num_parts, num_dims, system_objects, masses)

    # Print result
    print("System CM: " + str(system_cm))


###########################################################
# ENTRY POINT
###########################################################

if __name__ == "__main__":
    main()
