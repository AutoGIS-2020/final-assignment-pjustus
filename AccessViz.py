# AccessViz

import glob
import os
from pathlib import Path
import pandas as pd
import geopandas as gpd
import zipfile
from pyproj import CRS
import matplotlib.pyplot as plt
import contextily as ctx
import folium
import branca

def main():
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
    map_check = yn_loop("Do you want to see a map with the YKR ID grid? yes/no: ", yn_list)
    if map_check == "yes":
        YKR_map()
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
    zip_check = yn_loop("Do you need to extract the TimeTravelMatrix (TTM) files n\ or the MetropAccess_YKR_grid? yes/no: ", yn_list)
    if zip_check == "yes":
        zip_name = input("Insert the name of the zip file: ")
        if zip_name == "":
            return print(exit)
        zip_target = input("Insert the name of the target folder: ")
        if zip_target == "":
            return print(exit)
        unzip(zip_name, zip_target)
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
    FFF_check = yn_loop("TTM filepaths to a text file? yes/no: ", yn_list)
    if FFF_check == "yes":
        FF_result = FileFinder(YKR_IDs, input_folder_name, output_folder_name, to_file=True)
    elif FFF_check == "no":
        FF_result = FileFinder(YKR_IDs, input_folder_name, output_folder_name)
    elif FFF_check == "":
        return print(exit)
    # Creating and getting filepaths of geopackage files
    TJ_result = TableJoiner(YKR_IDs, output_folder_name, FF_result)
    # Asking if user wants to visualize results
    visu_check = yn_loop("Do you want to visualize the results? yes/no: ", yn_list)
    if visu_check == "yes":
        visualizer_tm = input("Insert the mode of travel for Visualizer, car/pt/bike/walk: ")
        if visualizer_tm == "":
            return print(exit)
        visualizer_mp = input("Insert the type of map for Visualizer, static/interactive: ")
        if visualizer_mp == "":
            return print(exit)
        Visualizer(YKR_IDs, output_folder_name, visualizer_tm, visualizer_mp, TJ_result)
        print(f"The map(s) can be found in: {output_folder_name}")
    elif visu_check == "no":
        print(f"Geopackage files can be found in: {output_folder_name}")
    elif visu_check == "":
        return print(exit)
    # Asking if user wants to compare travel modes
    ctool_check = yn_loop("Do you want to compare two travel modes? yes/no: ", yn_list)     
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
        ComparisonTool(tms, TJ_result, output_folder_name)
        return print(exit)
    else:
        return print(exit)

def FileFinder(YKR_IDs: list, input_folder_name: str, output_folder: str, to_file=False):
    """
    Returns a list of travel time matrix filepaths based on a list of YKR ID values
    from a specified input data folder. 

            Parameters:
                    YKR_IDs (list): A list of YKR_ID numbers
                    input_folder_name (str): Name of the input folder
                    output_folder (str): Name of the output folder
                    to_file (boolean): If True, also returns a text file

            Returns:
                    file_paths (list): A list of filepaths
    """
    # Using assert to make sure input is ok
    assert type(YKR_IDs) == list, "The input of the YKR_ID:s needs to be a list!"
    # Finding the folder from the user's instance
    input_folder = Path(input_folder_name).absolute()
    # Using assert to make sure input folder exists
    assert os.path.isdir(input_folder) == True, "Check the input folder's name!"
    # Defining counter
    counter = 0
    # Creating an empty list for the filepaths
    file_paths = []
    # Creating a variable for the f-string
    glob_end = "*.txt"
    # Creating a variable for glob
    glob_start = f"{input_folder_name}/**/travel_times_to_ "
    # Creating a list to check for false YKR ID's
    false_names = YKR_IDs.copy()
    # For-looping the user's folders (and subfolders) with glob
    for name in glob.glob(glob_start+glob_end, recursive=True):
        # Finding the YKR ID part of the filepath
        end_txt = name[-11:]
        end = end_txt[:-4]
        # Finding filename of the filepath
        fname = name[-28:]
        # Checking if the YKR ID of the filepath exists in input list
        if end in YKR_IDs:
            # Increasing counter
            counter += 1
            # Informing user of current progress
            print(f"Processing file {fname}. Progress: {counter}/{len(glob.glob(glob_start+glob_end, recursive=True))}")
            # Appending filepath to list
            file_paths.append(name)
            # Removing real YKR ID's from the false YKR ID list
            false_names.remove(end)
        else:
            continue
    # Informing user of false YKR ID's
    for false_ID in false_names:
        print(f"YKR ID number {false_ID} does not exist in folder: {input_folder_name}\nMake sure the YKR ID values in the input list are typed correctly.")
    # Checking for the optional parameter (default is False)
    if to_file == True:
        # Writing the list of filepaths to a text file
        fullname = os.path.join(output_folder, "YKR_ID_fps.txt")         
        YKR_txt = open(fullname, "w")
        YKR_txt.write(str(file_paths))
        YKR_txt.close()
        # Informing the user of the name of the new text file
        print(f"Filepath of the text file: {fullname}")
    # Returning the list of filepaths
    return file_paths

def TableJoiner(YKR_IDs: list, output_folder: str, FF_result):
    """
    Returns spatial layers as geopackage files based on a list of YKR_ID numbers 
    to a specified output folder. 

            Parameters:
                    YKR_IDs (list): A list of YKR ID numbers
                    output_folder (str): Name of the output folder
                    FF_result (list): A list of filepaths of the YKR ID numbers 

            Returns:
                    gpkg_files (list): A list of filepaths of the geopackage files
    """
    # Using assert to make sure output_folder is ok
    assert type(output_folder) == str, "The output_folder must be a string!"
    assert os.path.isdir(output_folder) == True, "Check the output_folder's name!"
    # Reading the grid file
    grid = gpd.read_file(GridFpFinder())
    # Getting the filepaths
    filepaths = FF_result
    # Creating an empty list for the file names
    gpkg_files = []
    # For-looping filepaths
    for fp in filepaths:
        # Getting the ID part of the filepath
        id_txt = fp[-11:]
        YKR_ID = id_txt[:-4]
        # Checking if files already exist
        fname = os.path.join(output_folder, f"{YKR_ID}.gpkg")
        my_file = Path(fname)
        if my_file.is_file():
            # Appending filepaths to the list
            gpkg_files.append(fname)
            continue
        else:
            # Reading the filepath
            data = pd.read_csv(fp, sep=";")
            # Merging the filepath with grid 
            merge = grid.merge(data, how="right", left_on="YKR_ID", right_on="from_id")
            # Creating a output path for the data with unique name
            output_fp = os.path.join(output_folder, f"{YKR_ID}.gpkg")
            # Saving the spatial layer 
            merge.to_file(output_fp, driver="GPKG")
            # Adding the filepaths to a list
            gpkg_files.append(output_fp)
    return gpkg_files

def GridFpFinder():
    """
    Returns the YKR grid filepath from the current directory.
    """
    # Defining flag
    flag = False
    # Getting current directory
    p = Path().absolute()
    # For-looping current directory
    for root, dirs, files in os.walk(p):
        for file in files:
            # Looking for the grid file
            if file.endswith('.shp'):
                if file == "MetropAccess_YKR_grid_EurefFIN.shp":
                    # Creating a filepath of the grid file
                    fullpath = os.path.join(root, file)
                    grid_fp = os.path.abspath(fullpath)
                    # Changing flag value
                    flag = True
    # Checking flag value
    if flag == False:
        # Raising an error
        raise OSError(f"Grid file: MetropAccess_YKR_grid_EurefFIN.shp does not exist in current working directory!\n{p}")
    # Returning the grid's filepath
    return grid_fp

def unzip(zip_file: str, target_folder: str):
    """
    Extracts selected file to a selected directory. 

            Parameters:
                    zip_file (str): Name of the zip file
                    target_dir (str): Name of the target directory

            Returns:
                    None
    """
    assert os.path.isfile(zip_file) == True, "Check the name of the zip file!"
    # Reading zipfile
    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        # Extracting zipfile to target folder
        zip_ref.extractall(target_folder)
        # Informing user of the progress
        print(f"File: {zip_file} extracted to: {target_folder}.")
    
def Visualizer(YKR_IDs: list, output_folder: str, travel_mode: str, map_type: str, TJ_result):
    """
    Returns .png or .html files of maps based on a list of YKR ID values. 

            Parameters:
                    YKR_IDs (list): A list of YKR_ID numbers
                    output_folder (str): Name of the output folder
                    travel_mode (str): Mode of travel. Accepted modes are:
                                        - "car"
                                        - "pt"
                                        - "bike"
                                        - "walk"
                    map_type (str): Type of map. Accepted types are:
                                        - "static"
                                        - "interactive"
                    TJ_result (list): A list of filepaths of the geopackage files

            Returns:
                    None
    """
    # Getting the filepaths 
    gpkg_fps = TJ_result
    # For-looping the files
    for fp in gpkg_fps:
        # Getting the YKR ID number
        name = fp[:-5]
        YKR_ID = name[-7:]
        # Reading the data
        data = gpd.read_file(fp)
        # Changing CRS
        data = data.to_crs(epsg=3857)
        # Checking map_type
        if map_type == "static":
            static_mapper(travel_mode, data, YKR_ID, output_folder)
        elif map_type == "interactive":
            interactive_mapper(travel_mode, data, YKR_ID, output_folder)
        else:
            raise SyntaxError("Check the spelling of map_type parameter!")
                
def static_mapper(tm, data, YKR_ID, output_folder):
    """
    Creates static maps for Visualizer. 

            Parameters:
                    tm (str): Mode of travel
                    data (str): Geometry data
                    YKR_ID (str): YKR ID number
                    output_folder (str): Name of the output folder

            Returns:
                    None
    """
    # Checking travel mode
    if tm == "car":
        variable = "car_r_t"
        # Creating unique credits
        credits = f"Travel time data to YKR ID {YKR_ID} by car in rush hour by Digital Geography Lab 2018, Map Data © OpenStreetMap contributors"
    elif tm == "pt":
        variable = "pt_r_t"
        # Creating unique credits
        credits = f"Travel time data to YKR ID {YKR_ID} by pt in rush hour by Digital Geography Lab 2018, Map Data © OpenStreetMap contributors"
    elif tm == "bike":
        variable = "bike_s_t"
        # Creating unique credits
        credits = f"Travel time data to YKR ID {YKR_ID} by slow cycling by Digital Geography Lab 2018, Map Data © OpenStreetMap contributors"
    elif tm == "walk":
        variable = "walk_t"
        # Creating unique credits
        credits = f"Travel time data to YKR ID {YKR_ID} on foot by Digital Geography Lab 2018, Map Data © OpenStreetMap contributors"
    else:
        raise SyntaxError("Check the spelling of travel_mode parameter!")
    # Saving the destination square 
    dest = data.loc[data["from_id"] == data["to_id"]]
    # Dealing with no data values
    data = data.loc[data[variable] > -1]
    # Plotting the data
    fig, ax = plt.subplots(figsize=(12, 8))
    if tm == "walk":
        # Changing the unit of time to hours
        data["walk_h_t"] = data["walk_t"] / 60 
        # Plotting the data
        data.plot(ax=ax,
              column="walk_h_t",
              cmap="RdYlBu",
              linewidth=0,
              scheme="quantiles",
              k=9,
              alpha=0.6,
              legend=True)
        # Legend in hours
        ax.get_legend().set_title("Travel time (hour)")
    else:
        # Plotting the data
        data.plot(ax=ax,
                  column=variable,
                  cmap="RdYlBu",
                  linewidth=0,
                  scheme="quantiles",
                  k=9,
                  alpha=0.6,
                  legend=True)
        # Legend in minutes
        ax.get_legend().set_title("Travel time (min)")
    # Plotting the destination square
    dest.plot(ax=ax,
              color="black",
              linewidth=0,
              alpha=0.8)
    # Adjusting legend
    ax.get_legend().set_bbox_to_anchor((1.24, 1))

    # Adding basemap
    ctx.add_basemap(ax, 
                    source=ctx.providers.OpenStreetMap.Mapnik,
                    attribution=credits)
    # Removing axis
    plt.axis("off")
    # Creating a output path for the map with unique name
    outfp = os.path.join(output_folder, f"{variable}_to_{YKR_ID}_static_map.png")
    # Saving figure
    plt.savefig(outfp, dpi=300)

def interactive_mapper(tm, data, YKR_ID, output_folder):
    """
    Creates interactive maps for Visualizer. 

            Parameters:
                    tm (str): Mode of travel
                    data (str): Geometry data
                    YKR_ID (str): YKR ID number
                    output_folder (str): Name of the output folder

            Returns:
                    None
    """
    # Checking travel mode
    if tm == "car":
        variable = "car_r_t"
        credits = f"Travel time data to YKR ID {YKR_ID} by car in rush hour by Digital Geography Lab 2018, Map Data © OpenStreetMap contributors"
    elif tm == "pt":
        variable = "pt_r_t"
        credits = f"Travel time data to YKR ID {YKR_ID} by pt in rush hour by Digital Geography Lab 2018, Map Data © OpenStreetMap contributors"
    elif tm == "bike":
        variable = "bike_s_t"
        credits = f"Travel time data to YKR ID {YKR_ID} by slow cycling by Digital Geography Lab 2018, Map Data © OpenStreetMap contributors"
    elif tm == "walk":
        variable = "walk_t"
        credits = f"Travel time data to YKR ID {YKR_ID} on foot by Digital Geography Lab 2018, Map Data © OpenStreetMap contributors"
    else:
        raise SyntaxError("Check the spelling of travel_mode parameter!")
    # Saving the destination square 
    #data[variable].loc[data["from_id"] == data["to_id"]] = 0
    dest = data.loc[data["from_id"] == data["to_id"]]
    # Dealing with no data values
    data = data.loc[data[variable] > -1]
    # Subsetting data
    data = data[["from_id", variable, "geometry"]]
    # Creating the map instance
    m = folium.Map(location=[60.25, 24.8], zoom_start=10, control_scale=True)
    if tm == "walk":
        # Changing the unit of time to hours
        data["walk_h_t"] = data[variable] / 60
        # Setting colorscale
        colorscale = branca.colormap.linear.RdYlBu_05.to_step(data = data["walk_h_t"], n = 9, method = 'quantiles')
        # Setting caption
        colorscale.caption = f"Travel time (hour)"
        # Defining style so the destination YKR ID square is black
        my_style = lambda x: {'fillColor':'black' if
                    x['properties']['from_id']== int(YKR_ID) else
                    colorscale(x['properties']["walk_h_t"]), 'weight':0, 
                             "fillOpacity": 0.9,}
        # Defining tooltip
        my_tooltip = folium.features.GeoJsonTooltip(fields=['from_id', "walk_h_t"],
                                                    aliases = ['YKR ID:', "Travel time (hour):"],
                                                    labels=True,
                                                    sticky=False)
        # Creating the choropleth map
        folium.features.GeoJson(data,  
                                name='Labels',
                                style_function=my_style,
                                tooltip=my_tooltip                                             
        ).add_to(m)
        
        # Adding a popup for the destination square
        dest_gjson = folium.GeoJson(dest, name='Destination square')
        popup = folium.Popup('Destination square')
        popup.add_to(dest_gjson)
        dest_gjson.add_to(m)
        
    else:
        # Setting colorscale
        colorscale = branca.colormap.linear.RdYlBu_05.to_step(data = data[variable], n = 9, method = 'quantiles')
        # Setting caption
        colorscale.caption = f"Travel time (min)"
        # Defining style so the destination YKR ID square is black
        my_style = lambda x: {'fillColor':'black' if
                    x['properties']['from_id']== int(YKR_ID) else
                    colorscale(x['properties'][variable]), 'weight':0, 
                             "fillOpacity": 0.9,}
        # Defining tooltip
        my_tooltip = folium.features.GeoJsonTooltip(fields=['from_id', variable],
                                                    aliases = ['YKR ID:', "Travel time (min):"],
                                                    labels=True,
                                                    sticky=False)
        # Creating the choropleth map
        folium.features.GeoJson(data,  
                                name='Grid',
                                style_function=my_style,
                                tooltip=my_tooltip                                             
        ).add_to(m)
        # Adding a popup for the destination square
        dest_gjson = folium.GeoJson(dest, name='Destination square')
        popup = folium.Popup('Destination square')
        popup.add_to(dest_gjson)
        dest_gjson.add_to(m)
    # Adding the colormap
    m.add_child(colorscale)
    # Adding layer control
    folium.LayerControl().add_to(m)
    title_html = '''
             <h3 align="center" style="font-size:16px"><b>{}</b></h3>
             '''.format(credits) 
    m.get_root().html.add_child(folium.Element(title_html))
    # Creating a output path for the map with unique name
    outfp = os.path.join(output_folder, f"{variable}_to_{YKR_ID}_map.html")
    # Saving the map
    m.save(outfp)

def ComparisonTool(tm_comp: list, TJ_result, output_folder):
    """
    Compares two travel modes by subtracting the first travel mode by the latter one.

            Parameters:
                    tm_comp (list): A list of travel modes to be compared
                    TJ_result (str): A list of filepaths of geopackage files
                    output_folder (str): Name of the output folder

            Returns:
                    None
    """
    # Using assert to make sure input is ok
    assert type(tm_comp) == list, "The travel modes for comparison has to be passed as a list!"
    assert len(tm_comp) == 2, "Make sure there are only two travel modes to be compared!"
    for tm in tm_comp:
        assert tm in ["car", "pt", "bike", "walk"], "Allowed travel modes are: car, pt, bike, walk."
    # Separating the travel modes
    tm1 = tm_comp[0]
    tm2 = tm_comp[1]
    # Finding the right column names for tm1
    if tm1 == "car" or tm1 == "pt":
        tm1_t = f"{tm1}_r_t"
        tm1_d = f"{tm1}_r_d"
    elif tm1 == "bike":
        tm1_t = f"{tm1}_s_t"
        tm1_d = f"{tm1}_d"
    else:
        tm1_t = f"{tm1}_t"
        tm1_d = f"{tm1}_d"
    # Finding the right column names for tm2
    if tm2 == "car" or tm2 == "pt":
        tm2_t = f"{tm2}_r_t"
        tm2_d = f"{tm2}_r_d"
    elif tm2 == "bike":
        tm2_t = f"{tm2}_s_t"
        tm2_d = f"{tm2}_d"
    else:
        tm2_t = f"{tm2}_t"
        tm2_d = f"{tm2}_d" 
    # Creating column names
    ct_t = f"{tm1[0]}_vs_{tm2[0]}_t"
    ct_d = f"{tm1[0]}_vs_{tm2[0]}_d"
    # Getting the files from TableJoiner
    gpkg_fps = TJ_result
    # For-looping the files
    for fp in gpkg_fps:
        # Getting the YKR ID number
        name = fp[:-5]
        YKR_ID = name[-7:]
        # Reading the data
        data = gpd.read_file(fp)
        # Dealing with no data values
        data = data.loc[data[tm1_t] > -1]
        data = data.loc[data[tm1_d] > -1]
        data = data.loc[data[tm2_t] > -1]
        data = data.loc[data[tm2_d] > -1]
        # Calculating the differences
        data[ct_t] = data.apply(lambda x: x[tm1_t] - x[tm2_t], axis=1)
        data[ct_d] = data.apply(lambda x: x[tm1_d] - x[tm2_d], axis=1)
        # Creating a output path for the data with unique name
        fname = f"Accessibility_{YKR_ID}_{tm1}_vs_{tm2}.gpkg"
        output_fp = os.path.join(output_folder, fname)
        # Saving the geopackage file to output folder
        data.to_file(output_fp, driver="GPKG")

def YKR_map():
    """
    Displays a map of YKR ID grid.
    
    """
    # Reading the grid file
    grid = gpd.read_file(GridFpFinder())
    # Creating the map instance
    m = folium.Map(location=[60.25, 24.8], zoom_start=10, control_scale=True)
    # Creating the choropleth map
    folium.features.GeoJson(grid,  
                            name='Grid',
                            style_function=lambda x: {'edgecolor':'black', 'fillColor': 'transparent', 'weight': 0.2},
                            tooltip=folium.features.GeoJsonTooltip(fields=['YKR_ID'],
                                                                    aliases = ['YKR ID:'],
                                                                    labels=True,
                                                                    sticky=False
                                                                                )
                           ).add_to(m)
    # Adding layer control
    folium.LayerControl().add_to(m)
    display(m)

def yn_loop(question: str, choices: list):
    """
    Asks for input until given a correct one and returns it.

            Parameters:
                    question (str): A defined question
                    choices (list): List of choices to choose from

            Returns:
                    choice (str): The user's choice
    """
    yes_no = "Accepted answers are yes & no. To exit press enter."
    choice = input(question)
    while choice not in choices:
        print(yes_no)
        choice = input(question)
    return choice
