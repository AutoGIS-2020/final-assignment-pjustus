# AccessViz

import AccessViz as av

def AccessViz():

    """
        A tool for managing, analyzing and visualizing the Travel Time Matrix data set.

    Usage:
        ./AccessViz.py

    License:
        MIT License

        Copyright (c) 2021 Justus Poutanen

        Permission is hereby granted, free of charge, to any person obtaining a copy
        of this software and associated documentation files (the "Software"), to deal
        in the Software without restriction, including without limitation the rights
        to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
        copies of the Software, and to permit persons to whom the Software is
        furnished to do so, subject to the following conditions:

        The above copyright notice and this permission notice shall be included in all
        copies or substantial portions of the Software.

        THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
        IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
        FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
        AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
        LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
        OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
        SOFTWARE.
    """

    # Defining a list of choices
    yn_list = ["yes", "no", ""]
    # Defining ending screen
    exit = "You have exited AccessViz. Please restart AccessViz to try again."
    # Defining starting screen
    print("Welcome to AccessViz. Press enter at any time to exit.")
    # Asking if user wants to see YKR ID grid map
    map_check = av.yn_loop("Do you want to see a map with the YKR ID grid? yes/no: ", yn_list)
    if map_check == "yes":
        av.YKR_map()
    elif map_check == "":
        return print(exit)
    # Asking for user's list of YKR ID's
    YKR_IDs_input = input("Insert a list of YKR ID's (e.g. [1234567, 5787544, 9876543]): ")
    if YKR_IDs_input == "":
        return print(exit)
    # Converting the input to a list
    list1 = YKR_IDs_input[1:]
    list2 = [str(x) for x in list1.split()]
    YKR_IDs = []
    for i in list2:
        i = i[:-1]
        YKR_IDs.append(i)
    # Asking if user wants to extract files
    zip_check = av.yn_loop("Do you need to extract the TimeTravelMatrix (TTM) files n\ or the MetropAccess_YKR_grid? yes/no: ", yn_list)
    if zip_check == "yes":
        zip_name = input("Insert the name of the zip file: ")
        if zip_name == "":
            return print(exit)
        zip_target = input("Insert the name of the target folder: ")
        if zip_target == "":
            return print(exit)
        av.unzip(zip_name, zip_target)
        return print("Please restart AccessViz.")
    elif zip_check == "":
        return print(exit)
    # Asking for user's input folder
    input_folder_name = input("Insert the name of the folder where the TTM files are: ")
    if input_folder_name == "":
        return print(exit)
    # Asking for user's output folder
    output_folder_name = input("Insert the name of the output folder: ")
    if output_folder_name == "":
        return print(exit)
    # Asking if user wants the TTM filepaths to a text file
    FFF_check = av.yn_loop("TTM filepaths to a text file? yes/no: ", yn_list)
    if FFF_check == "yes":
        FF_result = av.FileFinder(YKR_IDs, input_folder_name, output_folder_name, to_file=True)
    elif FFF_check == "no":
        FF_result = av.FileFinder(YKR_IDs, input_folder_name, output_folder_name)
    elif FFF_check == "":
        return print(exit)
    # Creating and getting filepaths of geopackage files
    TJ_result = av.TableJoiner(YKR_IDs, output_folder_name, FF_result)
    # Asking if user wants to visualize results
    visu_check = av.yn_loop("Do you want to visualize the results? yes/no: ", yn_list)
    if visu_check == "yes":
        visualizer_tm = input("Insert the mode of travel for Visualizer, car/pt/bike/walk: ")
        if visualizer_tm == "":
            return print(exit)
        visualizer_mp = input("Insert the type of map for Visualizer, static/interactive: ")
        if visualizer_mp == "":
            return print(exit)
        av.Visualizer(YKR_IDs, output_folder_name, visualizer_tm, visualizer_mp, TJ_result)
        print(f"The map(s) can be found in: {output_folder_name}")
    elif visu_check == "no":
        print(f"Geopackage files can be found in: {output_folder_name}")
    elif visu_check == "":
        return print(exit)
    # Asking if user wants to compare travel modes
    ctool_check = av.yn_loop("Do you want to compare two travel modes? yes/no: ", yn_list)     
    if ctool_check == "yes":
        tm_input = input("Insert a list of travel modes to be compared (e.g. [car, pt]): ")
        if tm_input == "":
            return print(exit)
        # Converting the input to a list
        tm_list1 = tm_input[1:]
        tm_list2 = [str(x) for x in tm_list1.split()]
        tms = []
        for i in tm_list2:
            i = i[:-1]
            tms.append(i)
        av.ComparisonTool(tms, TJ_result, output_folder_name)
        return print(exit)
    else:
        return print(exit)

