import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from streamlit_folium import folium_static
import plotly.express as px

# Function to perform Descriptive Statistics analysis
def descriptive_statistics(df):
    st.subheader("Summary Statistics:")
    st.write(df.describe())
# Function to perform Spatial Analysis: Mapping the distribution of listings across neighborhoods
def spatial_analysis(df):
    st.subheader("Spatial Analysis: Distribution of Listings Across Neighborhoods")
    
    # Check if the DataFrame is empty
    if df.empty:
        st.write("DataFrame is empty. No data to display.")
        return
    
    # Check if the DataFrame contains necessary columns
    if 'Country' not in df.columns:
        st.write("DataFrame does not contain a 'Country' column.")
        return
    
    # Aggregate data by country
    country_counts = df['Country'].value_counts().reset_index()
    country_counts.columns = ['Country', 'Count']
    
    # Load a GeoJSON file with country boundaries
    # Specify the encoding when reading the GeoJSON file
    with open('G:\Airbnb\custom.geo.json', 'r', encoding='utf-8') as file:
     geojson_data = file.read()
   
    
    # Create a choropleth map
    my_map = folium.Map(location=[0, 0], zoom_start=2)
    folium.Choropleth(
        geo_data=geojson_data,
        name='choropleth',
        data=country_counts,
        columns=['Country', 'Count'],
        key_on='feature.properties.name',
        fill_color='YlGnBu',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Number of Listings'
    ).add_to(my_map)

    # Display the map using folium_static
    folium_static(my_map)

def availability_box_plot(df, country=None, room_type=None, property_type=None, cancellation_policy=None):
    # Filter DataFrame based on selected criteria
    filtered_df = df.copy()
    if country:
        filtered_df = filtered_df[filtered_df['Country'].isin(country)]
    if room_type:
        filtered_df = filtered_df[filtered_df['Room_type'].isin(room_type)]
    if property_type:
        filtered_df = filtered_df[filtered_df['Property_type'].isin(property_type)]
    if cancellation_policy:
        filtered_df = filtered_df[filtered_df['Cancellation_policy'].isin(cancellation_policy)]

    hover_data = {"Availability_365": True, "No_of_reviews": True}
    fig = px.box(
        data_frame=filtered_df,
        x="Room_type",
        y="Availability_365",
        color="Room_type",
        hover_data=hover_data,
        title="Availability by Room Type"
    )
    st.plotly_chart(fig, use_container_width=True)
   
# Function to perform Price Analysis: Comparison of prices between different neighborhoods
def price_analysis(df, country=None, property_type=None, room_type=None, cancellation_policy=None):
    st.subheader("Price Analysis: Comparison of Prices Between Different Neighborhoods")

    # Filter DataFrame based on user selection
    filtered_df = df.copy()
    if country:
        filtered_df = filtered_df[filtered_df['Country'].isin(country)]
    if property_type:
        filtered_df = filtered_df[filtered_df['Property_type'].isin(property_type)]
    if room_type:
        filtered_df = filtered_df[filtered_df['Room_type'].isin(room_type)]
    if cancellation_policy:
        filtered_df = filtered_df[filtered_df['Cancellation_policy'].isin(cancellation_policy)]

    # Display choropleth map of listing prices by country
    st.subheader("Choropleth Map: Average Listing Prices by Country")
    country_df = filtered_df.groupby(['Country'], as_index=False)['Price'].mean().rename(columns={'Price': 'Average_Price'})
    fig = px.choropleth(country_df,
                        title='Average Listing Prices by Country',
                        locations='Country',
                        locationmode='country names',
                        color='Average_Price',
                        color_continuous_scale=px.colors.sequential.Plasma
                        )
    st.plotly_chart(fig, use_container_width=True)

    # AVG AVAILABILITY IN COUNTRIES SCATTERGEO
    country_df = filtered_df.groupby(['Country'], as_index=False)["Availability_365"].mean()
    country_df["Availability_365"] = country_df["Availability_365"].astype(int)
    fig = px.scatter_geo(
      data_frame=country_df,
      locations="Country",
      color="Availability_365",
      hover_data=["Availability_365"],
      locationmode="country names",
       size="Availability_365",
        title="Avg Availability in each Country",
        color_continuous_scale="agsunset"
    )
    st.plotly_chart(fig, use_container_width=True)

    # Boxplot of price distribution in selected neighborhood
    neighborhood = st.selectbox("Select a neighborhood:", filtered_df['Host_Neighbourhood'].unique())
    neighborhood_data = filtered_df[filtered_df['Host_Neighbourhood'] == neighborhood]
    fig, ax = plt.subplots()
    sns.boxplot(data=neighborhood_data, x='Host_Neighbourhood', y='Price', palette='tab10', ax=ax)
    plt.xlabel('Host Neighborhood')
    plt.ylabel('Price')
    plt.title('Price Distribution in ' + neighborhood)
    plt.xticks(rotation=45, ha='right')
    st.pyplot(fig)

    # AVAILABILITY BY ROOM TYPE BOX PLOT
    fig7,ax7=plt.subplots()
    sns.boxplot(data=filtered_df, x='Room_type', y='Availability_365', palette='Set2', ax=ax7)
    plt.xlabel('Room Type')
    plt.ylabel('Availability')
    plt.title('Availability by Room Type')
    plt.xticks(rotation=45, ha='right')
    st.pyplot(fig7)

    # Distribution of listings based on property type
    fig1, ax1 = plt.subplots()
    sns.countplot(data=filtered_df, x='Property_type', palette='Set1', ax=ax1)
    plt.xlabel('Property Type')
    plt.ylabel('Count')
    plt.title('Distribution of Listings Based on Property Types')
    plt.xticks(rotation=45)
    st.pyplot(fig1)

    # Heatmap of prices based on room types and property types
    pivot_table = filtered_df.pivot_table(index='Property_type', columns='Room_type', values='Price', aggfunc='mean')
    fig2, ax2 = plt.subplots()
    sns.heatmap(pivot_table, cmap='YlGnBu', annot=True, fmt=".0f", ax=ax2)
    plt.title('Heatmap of Prices Based on Room Types and Property Types')
    plt.xlabel('Room Type')
    plt.ylabel('Property Type')
    plt.xticks(rotation=45)
    plt.yticks(rotation=0)
    st.pyplot(fig2)

    # Distribution of listings based on number of bedrooms
    fig3, ax3 = plt.subplots()
    sns.histplot(filtered_df['Room_type'], bins=20, kde=True, ax=ax3)
    plt.xlabel('Number of Bedrooms')
    plt.ylabel('Frequency')
    plt.title('Distribution of Listings Based on Number of Bedrooms')
    st.pyplot(fig3)

    # Distribution of listing prices
    st.subheader("Distribution of Listing Prices:")
    fig4, ax4 = plt.subplots()
    sns.histplot(filtered_df['Price'], bins=30, kde=True, color='skyblue', ax=ax4)
    plt.xlabel('Price')
    plt.ylabel('Frequency')
    plt.title('Distribution of Listing Prices')
    st.pyplot(fig4)

    # Price variation across different property types
    st.subheader("Price Variation Across Different Property Types:")
    fig5, ax5 = plt.subplots()
    sns.boxplot(data=filtered_df, x='Property_type', y='Price', palette='Set2', ax=ax5)
    plt.xlabel('Property Type')
    plt.ylabel('Price')
    plt.title('Price Variation Across Different Property Types')
    plt.xticks(rotation=45, ha='right')
    st.pyplot(fig5)
# Display the number of reviews based on selected country, room type, and property type
    filtered_reviews_df = filtered_df.groupby(['Country', 'Room_type', 'Property_type'])['No_of_reviews'].sum().reset_index()
    st.subheader("Number of Reviews Based on Selected Criteria:")
    st.write(filtered_reviews_df)

  # Filter DataFrame based on selected country, room type, and property type
    filtered_df = df.copy()
    if country:
     filtered_df = filtered_df[filtered_df['Country'].isin(country)]
    if room_type:
      filtered_df = filtered_df[filtered_df['Room_type'].isin(room_type)]
    if property_type:
      filtered_df = filtered_df[filtered_df['Property_type'].isin(property_type)]

# Display distribution of amenities for the filtered DataFrame
    if 'Amenities' in filtered_df.columns:
     amenities_column = filtered_df['Amenities'].fillna('').astype(str)
     st.subheader("Distribution of Amenities:")
     unique_amenities = set(','.join(amenities_column.tolist()).split(', '))
     for amenity in unique_amenities:
        if amenity.strip() != '' and amenity.strip() != 'nan':  # Check for empty string and 'nan'
            percentage = filtered_df['Amenities'].apply(lambda x: amenity in str(x)).mean() * 100
            st.write(f"Percentage of Listings with {amenity}: {percentage:.2f}%")
    else:
     st.write("Amenities column not found in the dataset.")

# Main Function
def main():
    st.title("Airbnb Data Analysis")
    
    # Upload dataset
    uploaded_file = st.file_uploader("Upload your Airbnb dataset:", type=["csv"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.dataframe(df.head())

        # Perform selected analysis
        analysis_type = st.sidebar.selectbox("Choose Analysis", ["Descriptive Statistics", "Spatial Analysis", "Price Analysis", "Availability Analysis"])
        if analysis_type == "Descriptive Statistics":
            descriptive_statistics(df)
        elif analysis_type == "Spatial Analysis":
            spatial_analysis(df)
        elif analysis_type == "Price Analysis":
            # Get user inputs for filtering
            country = st.sidebar.multiselect('Select Country', sorted(df['Country'].unique()))
            property_type = st.sidebar.multiselect('Select Property Type', sorted(df['Property_type'].unique()))
            room_type = st.sidebar.multiselect('Select Room Type', sorted(df['Room_type'].unique()))
            cancellation_policy = st.sidebar.multiselect('Select Cancellation Policy', sorted(df['Cancellation_policy'].unique()))
            price_analysis(df, country, property_type, room_type, cancellation_policy)
        elif analysis_type == "Availability Analysis":
            # Get user input for selecting country, room type, property type, and cancellation policy
            country = st.sidebar.multiselect('Select Country', sorted(df['Country'].unique()))
            room_type = st.sidebar.multiselect('Select Room Type', sorted(df['Room_type'].unique()))
            property_type = st.sidebar.multiselect('Select Property Type', sorted(df['Property_type'].unique()))
            cancellation_policy = st.sidebar.multiselect('Select Cancellation Policy', sorted(df['Cancellation_policy'].unique()))

            availability_box_plot(df, country, room_type, property_type, cancellation_policy)


if __name__ == "__main__":
    main()
