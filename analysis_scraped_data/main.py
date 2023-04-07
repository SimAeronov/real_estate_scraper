import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import random


#  Dataframe cleanup function
def clean_dataframe(scraped_data):
    """
    Input as Pandas.Dataframe from Google Form. Replaces 'What is the Location?' with 'Location'..Price, Link and Info |
    Removes values that contain Price as 'Ценапризапитване' |
    Removes duplicate values | Converts BGN to Euro | Price column is converted to type-int

    :param scraped_data: Pandas.Dataframe
    :return: Pandas.Dataframe
    """
    scraped_data.rename(columns={"What is the Location?": "Location", "What is the Price?": "Price",
                                 "What is the Link?": "Link", "What is the Info?": "Info"}, inplace=True)

    # Here I remove rows that contain "ask for price" in "Price" column, contain Nan and Duplicates
    scraped_data = scraped_data[scraped_data["Price"].astype(str).str.contains("Ценапризапитване") == False]
    scraped_data = scraped_data.dropna()
    scraped_data = scraped_data.drop_duplicates(subset=["Link"])

    # Price
    # Kinda complicated expression, here I search inside "Price" column for substring "лв."
    # Once I find this substring I convert to int, then from BGN to Euro, then again to int
    try:
        scraped_data.loc[scraped_data["Price"].str.contains("лв"), "Price"] = \
            (scraped_data["Price"].str.replace("лв.", "", regex=True).astype(int) * 0.51).astype(int)
    except AttributeError:
        print("No Values in BGN found")

    # Now that I have cleared "Price" column I can convert everything to integer
    scraped_data["Price"] = scraped_data["Price"].astype(int)
    return scraped_data


# Find missing values (sold real estate)
def find_sold_realestate(scraped_data, scraped_data_old):
    """
    Returns Pandas.Dataframe with each element that is inside the second argument and NOT inside the first argument

    :param scraped_data: Pandas.Dataframe New
    :param scraped_data_old: Pandas.Dataframe Old
    :return: Pandas.Dataframe Values from Old Not in New
    """
    List_of_sold_realestate_Location, List_of_sold_realestate_price, List_of_sold_realestate_Link = [], [], []
    List_of_sold_realestate_info, List_of_sold_realestate_timestamp = [], []
    index_of_row_realestate = 0  # Prob not the best way but well...
    for Link_to_old_realestate in scraped_data_old["Link"].values:
        # First I find the last "=" where the page number is, I get only the string before that
        index_end_Link_substring = Link_to_old_realestate.rfind("&slink=")
        index_start_Link_substring = Link_to_old_realestate.rfind("adv=")
        current_Link_to_old_realestate = Link_to_old_realestate[index_start_Link_substring:index_end_Link_substring]
        # if current link (old data) is not in links column from new data...  any(arr) retrn true if single true in arr
        if not any(pd.Series(scraped_data["Link"].values).str.contains(current_Link_to_old_realestate)):
            List_of_sold_realestate_timestamp.append(scraped_data_old['Timestamp'].iloc[index_of_row_realestate])
            List_of_sold_realestate_Location.append(scraped_data_old['Location'].iloc[index_of_row_realestate])
            List_of_sold_realestate_price.append(scraped_data_old['Price'].iloc[index_of_row_realestate])
            List_of_sold_realestate_Link.append(Link_to_old_realestate)
            List_of_sold_realestate_info.append(scraped_data_old['Info'].iloc[index_of_row_realestate])
        index_of_row_realestate += 1
    return_dataframe_realestate = pd.DataFrame(
        list(zip(List_of_sold_realestate_timestamp, List_of_sold_realestate_Location, List_of_sold_realestate_price,
                 List_of_sold_realestate_Link, List_of_sold_realestate_info)),
        columns=['Timestamp', 'Location', 'Price', 'Link', 'Info'])
    return return_dataframe_realestate


# Print Data of interest
def print_data_of_interest(scraped_data, Location_of_interest):
    """
    Prints Date, Location, Price, Link and numb of unique such elements

    :param scraped_data: Pandas.Dataframe
    :param Location_of_interest: String Name of interest
    """
    data_of_interest_to_print = scraped_data.loc[scraped_data["Location"].str.contains(Location_of_interest)]
    numb_of_elements_of_interest, current_element_of_interest = len(data_of_interest_to_print), 1
    for row_data_of_interest_print in data_of_interest_to_print.iterrows():
        print(f" \n DATA OF INTEREST {current_element_of_interest} of {numb_of_elements_of_interest}:"
              f" \n {row_data_of_interest_print[1][0]} \n {row_data_of_interest_print[1][1]} \n "
              f"{row_data_of_interest_print[1][2]} Euro \n {row_data_of_interest_print[1][3]}"
              f"\n {row_data_of_interest_print[1][4]}")
        current_element_of_interest += 1


# Print max price
def print_max_price_location(scraped_data):
    """
    Prints Location, Price and Link for max price data

    :param scraped_data: Pandas Dataframe
    """
    print("\n HIGHEST PRICE FOR REAL ESTATE:")
    Location_of_max_price = scraped_data.loc[scraped_data["Price"] == scraped_data["Price"].max()]
    for row_data_max_price_row in Location_of_max_price .iterrows():
        print(f"{row_data_max_price_row[1][1]} \n {row_data_max_price_row[1][2]} Euro \n"
              f" {row_data_max_price_row[1][3]} \n")


# Print min price
def print_min_price_location(scraped_data):
    """
    Prints Location, Price and Link for min price data

    :param scraped_data: Pandas Dataframe
    """
    print("\n LOWEST PRICE FOR REAL ESTATE:")
    Location_of_max_price = scraped_data.loc[scraped_data["Price"] == scraped_data["Price"].min()]
    for row_data_max_price_row in Location_of_max_price .iterrows():
        print(f"{row_data_max_price_row[1][1]} \n {row_data_max_price_row[1][2]} Euro \n"
              f" {row_data_max_price_row[1][3]} \n")


# Create Plot Location, Price, Occurrence
def plot_tripple_bar(List_unique_location_names, List_unique_location_count, price_mean, plot_name, **kwargs):
    """
    Pyplots data as X, Y1, Y2, Name of plot, interesting="String Name from X"

    :param List_unique_location_names: Pandas.Dataframe X value
    :param List_unique_location_count:  Pandas.Dataframe Y1 value
    :param price_mean:   Pandas.Dataframe Y2 value
    :param plot_name: String Name of Plot
    :param kwargs: interesting="StringName"
    """
    # Here I generate a random color for each unique value (done in a bad way)
    random_colors = []
    for _ in List_unique_location_names:
        random_colors.append('#%02X%02X%02X' % (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))

    # Now I get my kwarg{key} holding name of value of interest. If yes, I change the color of the bar.
    if kwargs.get("interesting"):
        key_value_of_interest = kwargs.get("interesting")
        try:
            index_of_key_value_of_interest = List_unique_location_names.index(key_value_of_interest)
            List_unique_location_names[index_of_key_value_of_interest] += "----------------"
        except ValueError:
            print(f"Warning: [ {kwargs.get('interesting')} ] not in List")

    # Next I plot my data
    fig_1, ax = plt.subplots(figsize=(10, 5))
    ax2 = ax.twinx()
    ax.bar(List_unique_location_names, List_unique_location_count, color=random_colors)
    ax2.bar(List_unique_location_names, price_mean, color="black", alpha=0.2)
    ax.set_xlabel('Location')
    ax.set_ylabel('Occurrence')
    ax2.set_ylabel('Price [Eur]', color="grey")
    fig_1.autofmt_xdate(rotation=90)
    fig_1.canvas.manager.set_window_title(plot_name)
    plt.subplots_adjust(bottom=0.3)
    ax2.yaxis.set_major_formatter(mtick.StrMethodFormatter("{x:,.0f} $"))
    # Next few lines print the name of the LMB-ed bar
    def onclick(event):
        axes = event.inaxes
        x = event.xdata
        try:
            lbls = axes.get_xticklabels()
            idx = int(x.round())
            lbl = lbls[idx]
            print(lbl.get_text())
        except AttributeError:
            print("Frame of plot")

    fig_1.canvas.mpl_connect('button_press_event', onclick)


def remove_municipality_or_city(remove_text_dataframe, what_to_remove="Municipality"):
    """
    In example [Village Name, Municipality] if  what_to_remove is [Municipality], only [Village Name] will remain,
    otherwise [Municipality] will remain. NOTE: ['Location'] column should exist!

    :param remove_text_dataframe: Pandas.DataFrame as input
    :param what_to_remove: None
    :return: Pandas.DataFrame
    """
    # Town, Municipality: Remove Municipality => to_replace=r",.*$" | Town => to_replace=r"^.*,\s"
    if what_to_remove == "Municipality":
        remove_text_dataframe["Location"].replace(to_replace=r",.*$", value='', regex=True, inplace=True)
        return remove_text_dataframe
    remove_text_dataframe["Location"].replace(to_replace=r"^.*,\s", value='', regex=True, inplace=True)
    return remove_text_dataframe


# === CODE STARTS HERE ===
scraped_data_old = pd.read_csv("SavedData/scraped_data_8.csv")
scraped_data_new = pd.read_csv("SavedData/scraped_data_9.csv")

# Here I cleanup both dataframes
scraped_data_new = clean_dataframe(scraped_data_new)
scraped_data_old = clean_dataframe(scraped_data_old)

# Using Regex I replace everything after the "," with "". I do this to remove the "municipality" string
# Town, Municipality: Remove Municipality => to_replace=r",.*$" | Town => to_replace=r"^.*,\s"
scraped_data_new = remove_municipality_or_city(scraped_data_new, "Municipality")
# Next I count all unique values
unique_values_count = scraped_data_new["Location"].value_counts()
# Now I get the mean price per specific location
price_mean_all = scraped_data_new.groupby('Location', as_index=True)['Price'].mean()
# Map element order of mean_price(name:mean_price) to unique_count(name:num_of_occurrences) so the plot matches names
price_mean_all = unique_values_count.index.to_series().map(price_mean_all)

# === in the next few lines I get data of interest and plot it ===

# Get the max price value and location
print_max_price_location(scraped_data_new)
# Get the min price value and location
print_min_price_location(scraped_data_new)
# Compare values from old data to new data, find which Location Links are missing hence find sold real estate
dataframe_of_sold_realestate = find_sold_realestate(scraped_data_new, scraped_data_old)
# Remove the name of the municipality. Name of city [,] Name of municipality | to_replace=r",.*$" or =r"^.*,\s"
dataframe_of_sold_realestate = remove_municipality_or_city(dataframe_of_sold_realestate, "Municipality")
# Get count of unique sold real estates and their mean price
unique_sold_values_count = dataframe_of_sold_realestate["Location"].value_counts()
# Get mean price for sold realestate, then sort this data so it matches indexes with unique_sold_values_count.names
sold_price_mean = dataframe_of_sold_realestate.groupby('Location', as_index=True)['Price'].mean()
sold_price_mean = unique_sold_values_count.index.to_series().map(sold_price_mean)
# I can get new realestate by
# Print data for a specific Location from specific dataframe
names_of_interest =["Трявна"]
for element_from_names_of_interest in names_of_interest:
    print(f"PRINTING DATA FOR {element_from_names_of_interest}")
    print_data_of_interest(dataframe_of_sold_realestate, element_from_names_of_interest)
# Plot the data
plot_tripple_bar(unique_sold_values_count.index.tolist(), unique_sold_values_count, sold_price_mean, "Sold Real Estate")
plot_tripple_bar(unique_values_count.index.tolist(), unique_values_count, price_mean_all,
                 "Location, Price and Occurrence", interesting="с. Драгановци")
plt.show()

